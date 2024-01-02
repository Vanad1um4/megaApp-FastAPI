from fastapi import APIRouter, Depends, BackgroundTasks
from pprint import pprint
import json
from datetime import datetime, timedelta

from db.food import db_get_use_coeffs_bool, db_get_catalogue_ids, db_get_users_coefficients, db_set_users_coefficients, db_get_users_first_date, db_get_users_weights_all, db_get_all_diary_entries, db_get_all_catalogue_entries, db_get_one_weight, db_get_users_cached_stats, db_save_users_stats
from utils.utils import stopwatch


# @stopwatch
def get_cached_stats(background_tasks: BackgroundTasks, user_id, date_iso, coefficients):
    """
    {'2020-10-14': [97.7, 97.7, 2090.0317, None],
     '2020-10-15': [97.5, 97.6, 2578.9357999999997, None],
     ...
     '2023-12-22': [45.3, 79.2, 359.448, 2348],
     '2023-12-23': [None, 75.0, 0, 2331]}
    """
    res = db_get_users_cached_stats(user_id)

    if not res:
        stats = save_new_stats(user_id, date_iso, coefficients)
        return stats

    stats_date = res['up_to_date']
    if date_iso <= stats_date:
        # background_tasks.add_task(save_new_stats, user_id, date_iso, coefficients)  # for debug purposes
        return json.loads(res['stats'])

    if date_iso > stats_date:
        background_tasks.add_task(save_new_stats, user_id, date_iso, coefficients)
        return json.loads(res['stats'])


def save_new_stats(user_id, date_iso, coefficients):
    stats = stats_recalc(user_id, date_iso, coefficients)
    _ = db_save_users_stats(date_iso, json.dumps(stats), user_id)
    return stats


# @stopwatch
def get_coefficients(user_id):
    """
    {1: 0.88,
     2: 0.94,
     ...
     357: 1.0,
     358: 1.0}
    """
    personal_coefficients = {}
    res_use_coeffs = db_get_use_coeffs_bool(user_id)
    if res_use_coeffs[0]:
        personal_coefficients = get_and_validate_coefficients(user_id)
    else:
        personal_coefficients = make_ones_for_coefficients()

    return personal_coefficients


# @stopwatch
def get_and_validate_coefficients(user_id: int) -> dict:
    res_catalogue_ids = db_get_catalogue_ids()
    res_coeffs = db_get_users_coefficients(user_id)

    catalogue_ids = set(sorted([x[0] for x in res_catalogue_ids]))

    users_coeffs = {}
    try:
        users_coeffs = json.loads(res_coeffs[0])
        users_coeffs = {int(key): value for key, value in users_coeffs.items()}
        users_coeffs_ids = set(sorted([x for x in users_coeffs.keys()]))

        if len(catalogue_ids) > len(users_coeffs_ids):
            diff = catalogue_ids - users_coeffs_ids
            for key in diff:
                users_coeffs[key] = 1.0
            users_coeffs_str = json.dumps(users_coeffs)
            db_set_users_coefficients(user_id, users_coeffs_str)

        if len(users_coeffs_ids) > len(catalogue_ids):
            diff = users_coeffs_ids - catalogue_ids
            for key in diff:
                del users_coeffs[key]
            users_coeffs_str = json.dumps(users_coeffs)
            db_set_users_coefficients(user_id, users_coeffs_str)

    except:
        users_coeffs = {key: 1.0 for key in catalogue_ids}
        users_coeffs_str = json.dumps(users_coeffs)
        db_set_users_coefficients(user_id, users_coeffs_str)

    return users_coeffs


# stopwatch
def make_ones_for_coefficients():
    res_catalogue_ids = db_get_catalogue_ids()
    catalogue_ids = set(sorted([x[0] for x in res_catalogue_ids]))
    return {key: 1 for key in catalogue_ids}


# @stopwatch
def stats_recalc(user_id, date_iso, coefficients):
    first_date = db_get_users_first_date(user_id)
    all_dates = dates_list_prep(first_date, date_iso)

    weights_raw = db_get_users_weights_all(user_id)
    weights_prepped = weights_prep(weights_raw, all_dates)

    diary_entries_raw = db_get_all_diary_entries(user_id)
    diary_entries_prepped = diary_entries_prep(diary_entries_raw, all_dates)

    catalogue_raw = db_get_all_catalogue_entries()
    catalogue_prepped = catalogue_prep(catalogue_raw)

    daily_sum_kcals = daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, coefficients, all_dates)

    avg_days = 7
    daily_sum_kcals_avg = average_dict(daily_sum_kcals, avg_days, round_bool=True, round_places=0)
    weights_prepped_avg = average_dict(weights_prepped, avg_days, round_bool=True, round_places=1)

    norm_days = 30
    target_kcals = target_kcals_prep(daily_sum_kcals_avg, weights_prepped_avg, norm_days)
    target_kcals_avg = average_dict(target_kcals, norm_days, round_bool=True, round_places=0)

    # print(len(all_dates), len(daily_sum_kcals), len(weights_prepped), len(weights_prepped_avg), len(target_kcals_avg))

    stats = stats_prep(all_dates, weights_prepped, weights_prepped_avg, daily_sum_kcals, target_kcals_avg)
    return stats


# @stopwatch
def stats_prep(all_dates, weights, avg_weights, eaten, target_kcals_avg):
    """
    {'2020-10-14': [97.7, 97.7, 2090.0317, None],
     '2020-10-15': [97.5, 97.6, 2578.9357999999997, None],
     ...
     '2023-12-22': [45.3, 79.2, 359.448, 2348],
     '2023-12-23': [None, 75.0, 0, 2331]}
    """
    stats = {}

    for day in all_dates:
        stats[day.isoformat()] = [
            weights.get(day, None),
            avg_weights.get(day, None),
            eaten.get(day, None),
            target_kcals_avg.get(day, None),
        ]

    return stats


def dates_list_prep(first_day, last_day_iso):
    """
    [datetime.date(2020, 10, 14),
     datetime.date(2020, 10, 15),
     ...
     datetime.date(2023, 12, 22),
     datetime.date(2023, 12, 23)]
    """
    last_day = datetime.fromisoformat(last_day_iso).date()
    days_amt = (last_day - first_day).days + 1
    all_dates = [first_day + timedelta(days=i) for i in range(days_amt)]
    return all_dates


def weights_prep(weights_raw, all_dates):
    """
    {datetime.date(2020, 10, 14): 97.7,
     datetime.date(2020, 10, 15): 97.5,
     ...
     datetime.date(2023, 12, 22): 45.3,
     datetime.date(2023, 12, 23): None}
    """
    weights_prepped = {date: None for date in all_dates}
    for item in weights_raw:
        weights_prepped[item[0]] = float(item[1])
    return weights_prepped


def diary_entries_prep(diary_entries_raw, all_dates):
    """
    {datetime.date(2020, 10, 14): [(133, 11), (27, 153), ...
     datetime.date(2020, 10, 15): [(111, 45), (110, 145), ...
     ...
     datetime.date(2023, 12, 22): [(103, 51), (85, 170)],
     datetime.date(2023, 12, 23): None}
    """
    # diary_entries_prepped = dict(all_dates)
    diary_entries_prepped = {date: None for date in all_dates}
    for row in diary_entries_raw:
        # print(row)
        if diary_entries_prepped[row[0]] == None:
            diary_entries_prepped[row[0]] = []
        diary_entries_prepped[row[0]].append((row[1], row[2]))

    return diary_entries_prepped


def catalogue_prep(catalogue):
    """
    {1: 212,
     2: 165,
     ...
     357: 25,
     358: 20}
    """
    catalogue_prepped = {}
    for item in catalogue:
        catalogue_prepped[item[0]] = item[1]
    return catalogue_prepped


def daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, personal_coeffs, all_dates):
    """
    {datetime.date(2020, 10, 14): 2090.0317,
     datetime.date(2020, 10, 15): 2578.9357999999997,
     ...
     datetime.date(2023, 12, 22): 359.448,
     datetime.date(2023, 12, 23): 0}
    """
    # daily_sum_kcals = dict(all_dates)
    daily_sum_kcals = {date: None for date in all_dates}
    for key, value in diary_entries_prepped.items():

        if daily_sum_kcals[key] == None:
            daily_sum_kcals[key] = 0

        if value != None:
            for food in value:
                daily_sum_kcals[key] += catalogue_prepped[food[0]] * personal_coeffs[food[0]] * food[1] / 100

    return daily_sum_kcals


def target_kcals_prep(kcals, weights, n):
    """
    {datetime.date(2020, 11, 12): 3172.833333333335,
     datetime.date(2020, 11, 13): 3109.4999999999986,
     ...
     datetime.date(2023, 12, 22): 1085.6666666666674,
     datetime.date(2023, 12, 23): 2080.8000000000015}
    """
    kcals_keys = list(kcals.keys())
    kcals_values = list(kcals.values())
    weights_values = list(weights.values())

    list_averaged = []
    for i in range(n-1, len(kcals_values)):
        list_averaged.append((sum(kcals_values[i-n+1:i+1]) - ((weights_values[i] - weights_values[i-n+1]) * 7700)) / n)

    kcals_keys = kcals_keys[len(kcals_keys)-len(list_averaged):]
    return {k: v for k, v in zip(kcals_keys, list_averaged)}


########################################################################################################################
    # this_days_weight = prep_one_weight_for_fiary_view(user_id, dates['this_day_iso'])
########################################################################################################################

def prep_one_weight_for_fiary_view(user_id: int, date_iso: str) -> float | None:
    weight_res = db_get_one_weight(user_id, date_iso)

    if weight_res[0] == 'success':
        this_days_weight = weight_res[1][0]
    else:
        this_days_weight = None

    return this_days_weight


########################################################################################################################
########################################################################################################################

# @stopwatch
def extend_diary(target_dict, property_name, value, value_if_none):
    """
    {'2023-12-13': {'food': {65328: {'catalogue_id': 166, 'date': datetime.date(2023, 12, 13), 'food_weight': 142, 'id': 65328},
                             65329: {'catalogue_id': 68, 'date': datetime.date(2023, 12, 13), 'food_weight': 71, 'id': 65329},
     ... 
     '2023-12-22': {'food': {65652: {'catalogue_id': 103, 'date': datetime.date(2023, 12, 22), 'food_weight': 51, 'id': 65652},
                             65653: {'catalogue_id': 85, 'date': datetime.date(2023, 12, 22), 'food_weight': 170, 'id': 65653}}},
     '2023-12-23': {'food': {}}}
    """
    for date in target_dict:
        target_dict[date][property_name] = value.get(date, value_if_none)
    return target_dict


# @stopwatch
# def prep_target_kcals(stats, dates_list):
#     target_kcals = {}
#     for date in dates_list:
#         target_kcals[date] = stats[date][3]
#     return target_kcals


def prep_target_kcals(stats, dates_list):
    """
    {'2023-12-13': 2470,
     '2023-12-14': 2475,
     ...
     '2023-12-22': 2348,
     '2023-12-23': 2331}
    """
    target_kcals = {}
    prev_value = 0
    for date in dates_list:
        prev_value = stats[date][3] if date in stats else prev_value
        target_kcals[date] = prev_value
    return target_kcals


# @stopwatch
def get_date_range(iso_date, fetch_days_range_offset):
    """
    ['2023-12-13', '2023-12-14', ... , '2023-12-22', '2023-12-23']
    """
    date = datetime.fromisoformat(iso_date)
    dates_before = [(date - timedelta(days=i)).date().isoformat() for i in range(fetch_days_range_offset, 0, -1)]
    dates_after = [(date + timedelta(days=i)).date().isoformat()
                   for i in range(1, fetch_days_range_offset + 1) if (date + timedelta(days=i)) <= datetime.now()]
    result = dates_before + [iso_date] + dates_after
    return result


def dictify_dates_list(dates_list):
    """
    {'2023-12-13': {}, '2023-12-14': {}, ... , '2023-12-22': {}, '2023-12-23': {}}
    """
    return {date: {} for date in dates_list}


def dictify_weights_list(weights_list):
    """
    {'2023-12-13': Decimal('74.3'),
     '2023-12-14': Decimal('74.6'),
     ...
     '2023-12-21': Decimal('136.0'),
     '2023-12-22': Decimal('45.3')}

    """
    return {date.isoformat(): weight for date, weight in weights_list}


# @stopwatch
def organize_by_dates_and_ids(inbound_list: list) -> dict:
    """
    {'2023-12-13': {65328: {'catalogue_id': 166, 'date': datetime.date(2023, 12, 13), 'food_weight': 142, 'id': 65328},
                    65329: {'catalogue_id': 68, 'date': datetime.date(2023, 12, 13), 'food_weight': 71, 'id': 65329},
     ...
     '2023-12-22': {65652: {'catalogue_id': 103, 'date': datetime.date(2023, 12, 22), 'food_weight': 51, 'id': 65652},
                    65653: {'catalogue_id': 85, 'date': datetime.date(2023, 12, 22), 'food_weight': 170, 'id': 65653}}}
    """
    result_dict = {}
    for food in inbound_list:
        # date = food['date']
        date = food['date'].strftime("%Y-%m-%d")
        id = food['id']
        if date not in result_dict:
            result_dict[date] = {}
            result_dict[date] = {}
        result_dict[date][id] = food
    return result_dict


# @stopwatch
def list_to_dict_with_ids(inbound_list: list) -> dict:
    """
    {1: {'id': 1, 'kcals': 212, 'name': 'Салат мимоза'},
     2: {'id': 2, 'kcals': 165, 'name': 'Салат колбаса капуста'},
     ...
     357: {'id': 357, 'kcals': 25, 'name': 'Ламинарии морская капуста'},
     358: {'id': 358, 'kcals': 20, 'name': 'Сок томатный'}}
    """
    result_dict = {}
    for item in inbound_list:
        id = item['id']
        result_dict[id] = item
    return result_dict


def catalogue_ids_prep(ids: str | None) -> list[int]:
    """
    ['77', '66']
    """
    if ids == None:
        return []
    return json.loads(ids[0])


def average_list(input_list, avg_range, round_bool=False, round_places=0):
    res = []

    # Не уменьшает итоговый список, считает среднее из доступного кол-ва чисел, если оных меньше avg_range
    for i in range(1, len(input_list)+1):
        j = 0 if i - avg_range <= 0 else i - avg_range
        if round_bool and round_places > 0:
            res.append(round(sum(input_list[j:i]) / (i - j), round_places))
        elif round_bool and round_places == 0:
            res.append(int(sum(input_list[j:i]) / (i - j)))
        else:
            res.append(sum(input_list[j:i]) / (i - j))

    return res


def average_dict(input_dict, avg_range, round_bool=False, round_places=0):
    """
    {datetime.date(2020, 10, 14): 97.7,
     datetime.date(2020, 10, 15): 97.6,
     ...
     datetime.date(2023, 12, 22): 79.2,
     datetime.date(2023, 12, 23): 75.0}
    """
    input_dict_keys = list(input_dict.keys())
    input_dict_values = list(input_dict.values())

    # replace None with previous value so you do not get en error trying to sum None and float down the line =)
    for i in range(1, len(input_dict_values)):
        if input_dict_values[i] == None:
            input_dict_values[i] = input_dict_values[i-1]

    list_averaged = []
    for i in range(1, len(input_dict_values)+1):
        j = 0 if i - avg_range <= 0 else i - avg_range
        if round_bool and round_places > 0:
            list_averaged.append(round(sum(input_dict_values[j:i]) / (i - j), round_places))
        elif round_bool and round_places == 0:
            list_averaged.append(int(sum(input_dict_values[j:i]) / (i - j)))
        else:
            list_averaged.append(sum(input_dict_values[j:i]) / (i - j))

    return {k: v for k, v in zip(input_dict_keys, list_averaged)}
