def dictify_list_with_ids(incoming_list: list) -> dict:
    return {d['id']: d for d in incoming_list}
