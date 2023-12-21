from fastapi import APIRouter, Depends, BackgroundTasks
from pprint import pprint
import json
from datetime import datetime, timedelta
from time import sleep

from utils.auth import AuthHandler
from db.food import db_get_diary_by_userid, db_get_catalogue, db_get_users_weights_range, db_get_users_cached_stats, db_get_users_body_weight, db_save_users_body_weight
from utils.food_utils import organize_by_dates_and_ids, list_to_dict_with_ids, get_coefficients, extend_diary, get_date_range, get_cached_stats, stats_recalc, prep_target_kcals
from env import FETCH_DAYS_RANGE_OFFSET
from schemas import BodyWeight

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/full_update/{date_iso}', tags=['Food -> Diary'])
def get_full_update(date_iso: str, background_tasks: BackgroundTasks, user_id=Depends(auth_handler.auth_wrapper)):
    response_dict = {}

    dates_list = get_date_range(date_iso, FETCH_DAYS_RANGE_OFFSET)
    # print('\n', 'dates_list')
    # pprint(dates_list)
    diary_result = {date: {} for date in dates_list}
    # print('\n', 'diary_result')
    # pprint(diary_result)

    diary_food_raw = db_get_diary_by_userid(dates_list[0], dates_list[-1], user_id)
    # print('\n', 'diary_raw')
    # pprint(diary_raw)
    diary_food_prepped = organize_by_dates_and_ids(diary_food_raw)
    # print('\n', 'diary_prepped')
    # pprint(diary_prepped)
    diary_result = extend_diary(diary_result, diary_food_prepped, 'food', {})
    # print('\n', 'diary_result')
    # pprint(diary_result)

    weights = db_get_users_weights_range(dates_list[0], dates_list[-1], user_id)
    # print('\n', 'weights')
    # pprint(weights)
    weights_dictified = {date.isoformat(): weight for date, weight in weights}
    # print('\n', 'weights_dictified')
    # pprint(weights_dictified)
    diary_result = extend_diary(diary_result, weights_dictified, 'body_weight', None)
    # print('\n', 'diary_result')
    # pprint(diary_result)

    # TODO: сократить количество запросов к базе данных тут
    coefficients = get_coefficients(user_id)
    response_dict['coefficients'] = coefficients

    stats = get_cached_stats(background_tasks, user_id, date_iso, coefficients)
    # print('\n', 'stats')
    # pprint(stats)
    target_kcals = prep_target_kcals(stats, dates_list)
    # print('\n', 'target_kcals')
    # pprint(target_kcals)
    diary_result = extend_diary(diary_result, target_kcals, 'target_kcals', None)

    response_dict['diary'] = diary_result

    catalogue_raw = db_get_catalogue()
    # print('\n', 'catalogue_raw')
    # pprint(catalogue_raw)
    catalogue_prepped = list_to_dict_with_ids(catalogue_raw)
    # print('\n', 'catalogue_prepped')
    # pprint(catalogue_prepped)
    response_dict['catalogue'] = catalogue_prepped

    # background_tasks.add_task(stats_recalc, user_id, date_iso, coefficients)

    # print('\n', 'response_dict')
    # pprint(response_dict)
    return response_dict


@router.post('/body_weight/', tags=['Food -> Diary'])
def get_stats(body_weight: BodyWeight, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_save_users_body_weight(body_weight.date_iso, body_weight.body_weight, user_id)
    return {'result: ': res}


@router.get('/stats/{date_iso}', tags=['Food -> Diary'])
def get_stats(date_iso: str, user_id=Depends(auth_handler.auth_wrapper)):
    # res = db_get_users_cached_stats(user_id)
    sleep(2)
    return

# @router.post('/food', tags=['Food -> Diary'])
# def add_bank(bank: Bank, user_id=Depends(auth_handler.auth_wrapper)):
#     # res = db_add_bank(bank, user_id)
#     # return {'result: ': res}
#     return


# @router.put('/food/{bank_id}', tags=['Food -> Diary'])
# def edit_bank(bank: Bank, bank_id: int, user_id=Depends(auth_handler.auth_wrapper)):
#     # res = db_update_bank(bank, bank_id, user_id)
#     # return {'result: ': res}
#     return


# @router.delete('/food/{bank_id}', tags=['Food -> Diary'])
# def delete_bank(bank_id: int, user_id=Depends(auth_handler.auth_wrapper)):
#     # res = db_delete_bank(bank_id, user_id)
#     # return {'result: ': res}
#     return

# # TODO: ломает подзагрузку, возвращает не так же оформленную еду как в get_full_update!!!
# @router.get('/food/{date_iso}', tags=['Food -> Diary'])
# def get_food(date_iso: str, user_id=Depends(auth_handler.auth_wrapper)):
#     response_dict = {}
#     dates_list = get_date_range(date_iso, FETCH_DAYS_RANGE_OFFSET)
#     diary_food_raw = db_get_diary_by_userid(dates_list[0], dates_list[-1], user_id)
#     diary_food_prepped = organize_by_dates_and_ids(diary_food_raw)
#     diary_result = {date: {} for date in dates_list}
#     diary_result = extend_diary(diary_result, diary_food_prepped, 'food', {})
#     response_dict['diary'] = diary_result
#     return response_dict
