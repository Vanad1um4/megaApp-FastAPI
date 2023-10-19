from fastapi import APIRouter, Depends
from utils.auth import AuthHandler
from pprint import pprint

from schemas import Category
from db.category import db_get_category_list_by_user_id, db_add_category, db_update_category, db_delete_category

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/category', tags=['Money -> Category'])
def get_category_list(user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_category_list_by_user_id(user_id)
    prepped_categories = prep_categories(res)
    # pprint(prepped_categories)
    return {'category_list': prepped_categories}


@router.post('/category', tags=['Money -> Category'])
def add_category(category: Category, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_category(category, user_id)
    return {'result: ': res}


@router.put('/category/{category_id}', tags=['Money -> Category'])
def edit_category(category: Category, category_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_category(category, category_id, user_id)
    return {'result: ': res}


@router.delete('/category/{category_id}', tags=['Money -> Category'])
def delete_category(category_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_category(category_id, user_id)
    return {'result: ': res}


def prep_categories(category_list):
    result = []

    for item in category_list:
        if item['parent_id'] is None:
            item['children'] = []
            result.append(item)

        else:
            for output_item in result:
                if output_item['id'] == item['parent_id']:
                    output_item['children'].append(item)
                    break

    # for item in category_list:
    #     del item['parent_id']
    #     # del item['kind']

    return result


# def prep_categories(input_dict):
#     # if not isinstance(input_dict, dict):
#     #     raise ValueError("input_dict должен быть словарем")

#     output_dict = {'income': [], 'expense': [], 'transfer': []}

#     for item in input_dict:
#         if item['parent_id'] is None:
#             item['children'] = []
#             output_dict[item['kind']].append(item)
#         else:
#             for output_item in output_dict[item['kind']]:
#                 if output_item['id'] == item['parent_id']:
#                     output_item['children'].append(item)
#                     break
#             del item['parent_id']
#             del item['kind']

#     return output_dict


# def transform_dict(input_dict):
#     output_dict = {'income': [], 'expense': [], 'transfer': []}

#     # Создаем словарь id категории -> категория для быстрого доступа
#     id_to_category = {}

#     for item in input_dict:
#         # Избавляемся от ненужных ключей
#         del item['parent_id']
#         del item['kind']

#         # Создаем список children для каждой категории
#         item['children'] = []

#         # Сохраняем категории в словаре для быстрого доступа
#         id_to_category[item['id']] = item

#         # Добавляем категории верхнего уровня в output_dict
#         if item['parent_id'] is None:
#             output_dict[item['kind']].append(item)
#         else:
#             # Если это дочерняя категория, добавляем ее в родительскую категорию
#             parent_category = id_to_category.get(item['parent_id'])
#             if parent_category:
#                 parent_category['children'].append(item)

#     return output_dict


# def prep_categories(category_list):
#     result = {'income': [], 'expense': [], 'transfer': {}}
#     id_to_category = {}

#     # Сначала создаем все категории
#     for item in category_list:
#         id = item['id']
#         title = item['title']
#         kind = item['kind']

#         new_item = {'id': id, 'title': title, 'children': []}

#         if kind in result:
#             result[kind].append(new_item)

#         id_to_category[id] = new_item

#     # Затем добавляем дочерние элементы к родительским категориям
#     for item in category_list:
#         id = item['id']
#         parent_id = item['parent_id']

#         if parent_id is not None and parent_id in id_to_category:
#             id_to_category[parent_id]['children'].append(id_to_category[id])

#     return result

    # output_dict = {'income': [], 'expense': [], 'transfer': []}
    # id_to_category = {}

    # for item in category_list:
    #     id = item['id']
    #     title = item['title']
    #     parent_id = item['parent_id']
    #     kind = item['kind']

    #     new_item = {'id': id, 'title': title, 'children': []}

    #     if kind in output_dict:
    #         if parent_id is None:
    #             output_dict[kind].append(new_item)
    #         else:
    #             if parent_id in id_to_category:
    #                 id_to_category[parent_id]['children'].append(new_item)
    #             else:
    #                 print(f"Warning: Parent category with ID {parent_id} not found for category with ID {id}")

    # return output_dict
