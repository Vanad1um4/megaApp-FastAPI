from fastapi import APIRouter, Depends, BackgroundTasks
from pprint import pprint
import json
from datetime import datetime, timedelta
from time import sleep

from utils.auth import AuthHandler
from db.food import db_get_diary_by_userid, db_get_catalogue, db_get_users_weights_range, db_save_users_body_weight, db_get_users_food_catalogue_ids_list, db_add_new_catalogue_entry, db_update_catalogue_entry, db_update_users_food_catalogue_ids_list, db_add_users_food_catalogue_ids_list, db_add_diary_entry, db_edit_diary_entry, db_delete_diary_entry, db_get_height
from utils.food_utils import organize_by_dates_and_ids, list_to_dict_with_ids, get_coefficients, extend_diary, get_date_range, get_cached_stats, prep_target_kcals, catalogue_ids_prep, dictify_dates_list, dictify_weights_list
from env import FETCH_DAYS_RANGE_OFFSET
from schemas import BodyWeight, CatalogueEntry, DiaryEntry

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/full_update/{date_iso}', tags=['Food -> Diary'])
def get_full_update(date_iso: str, background_tasks: BackgroundTasks, user_id=Depends(auth_handler.auth_wrapper)):
    response_dict = {}

    dates_list = get_date_range(date_iso, FETCH_DAYS_RANGE_OFFSET)
    diary_result = dictify_dates_list(dates_list)

    diary_food_raw = db_get_diary_by_userid(dates_list[0], dates_list[-1], user_id)
    diary_food_prepped = organize_by_dates_and_ids(diary_food_raw)
    diary_result = extend_diary(diary_result, 'food', diary_food_prepped, {})

    weights_list = db_get_users_weights_range(dates_list[0], dates_list[-1], user_id)
    weights_dictified = dictify_weights_list(weights_list)
    diary_result = extend_diary(diary_result, 'body_weight', weights_dictified, None)

    # TODO: сократить количество запросов к базе данных тут
    coefficients = get_coefficients(user_id)
    response_dict['coefficients'] = coefficients

    stats = get_cached_stats(background_tasks, user_id, date_iso, coefficients)
    target_kcals = prep_target_kcals(stats, dates_list)
    diary_result = extend_diary(diary_result, 'target_kcals', target_kcals, None)
    response_dict['diary'] = diary_result

    catalogue_raw = db_get_catalogue()
    catalogue_prepped = list_to_dict_with_ids(catalogue_raw)
    response_dict['catalogue'] = catalogue_prepped

    personal_catalogue_raw = db_get_users_food_catalogue_ids_list(user_id)
    personal_catalogue_prepped = catalogue_ids_prep(personal_catalogue_raw)
    response_dict['personal_catalogue_ids'] = personal_catalogue_prepped

    users_height = db_get_height(user_id)
    response_dict['height'] = users_height[0] or 0

    # background_tasks.add_task(stats_recalc, user_id, date_iso, coefficients)
    return response_dict


@router.post('/diary/', tags=['Food -> Diary'])
def new_diary_entry(diary_entry: DiaryEntry, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_diary_entry(diary_entry.date, diary_entry.catalogue_id, diary_entry.food_weight, user_id)
    if res:
        return {'result': True, 'value': res[0]}
    return {'result': False}


@router.put('/diary/', tags=['Food -> Diary'])
def edit_diary_entry(diary_entry: DiaryEntry, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_edit_diary_entry(diary_entry.food_weight, diary_entry.id, user_id)
    if res:
        return {'result': True, 'value': diary_entry.id}
    return {'result': False}


@router.delete('/diary/{diary_entry_id}', tags=['Food -> Diary'])
def delete_diary_entry(diary_entry_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_diary_entry(diary_entry_id, user_id)
    if res:
        return {'result': True, 'value': diary_entry_id}
    return {'result': False}


@router.post('/body_weight/', tags=['Food -> Diary'])
def save_body_weight(body_weight: BodyWeight, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_save_users_body_weight(body_weight.date_iso, body_weight.body_weight, user_id)
    return {'result': res}


@router.post('/catalogue/', tags=['Food -> Diary'])
def add_catalogue_entry(catalogue_entry: CatalogueEntry, user_id=Depends(auth_handler.auth_wrapper)):
    res_id = 0
    if catalogue_entry.id == 0:
        res = db_add_new_catalogue_entry(catalogue_entry.name, catalogue_entry.kcals)
        if res:
            res_id = res[0]
    else:
        res = db_update_catalogue_entry(catalogue_entry.id, catalogue_entry.name, catalogue_entry.kcals)
        if res:
            res_id = catalogue_entry.id
    return {'result': True, 'value': res_id}


@router.put('/user-catalogue/{food_id}', tags=['Food -> Diary'])
def add_user_catalogue_entry(food_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    ids_string = db_get_users_food_catalogue_ids_list(user_id)

    if ids_string:
        ids_list = json.loads(ids_string[0])
        ids_list.append(food_id)
        res = db_update_users_food_catalogue_ids_list(json.dumps(ids_list), user_id)
    else:
        ids_list = [food_id]
        res = db_add_users_food_catalogue_ids_list(json.dumps(ids_list), user_id)

    if res:
        return {'result': True}
    return {'result': False}


@router.delete('/user-catalogue/{food_id}', tags=['Food -> Diary'])
def remove_entry_from_user_catalogue(food_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    ids_string = db_get_users_food_catalogue_ids_list(user_id)

    if ids_string:
        ids_list = json.loads(ids_string[0])
        ids_list.remove(food_id)
        res = db_update_users_food_catalogue_ids_list(json.dumps(ids_list), user_id)

    if res:
        return {'result': True}
    return {'result': False}


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
