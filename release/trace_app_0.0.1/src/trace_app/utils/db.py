from mg_app_framework import get_handler, TaskKey, get_logger, get_organization

db_index_map = {
    # 在此处注册新集合的索引
    # 'collection_name': [
    #     [("field_name", 1)],  # 升序索引
    #     [("field_a", 1), ("field_b", -1)],  # 复合索引
    # ],
}


async def get_db_handler(db_name=None):
    handler = get_handler(TaskKey.idi_server)
    organization = get_organization()
    if db_name is None:
        db_name = f'{organization}_trace_app'
    return handler[db_name]


async def get_collection_handler(collection_name, db_name=None):
    handler = await get_db_handler(db_name)
    all_collection_names = await handler.list_collection_names(False)
    if collection_name in all_collection_names:
        collection = handler.get_collection(collection_name)
    else:
        collection = await handler.create_collection(collection_name)
        try:
            existing_indexes = await collection.list_indexes().to_list(None)
            if collection_name in db_index_map.keys():
                indexes = db_index_map[collection_name]
                for index in indexes:
                    if index not in existing_indexes:
                        await collection.create_index(index)
        except Exception as e:
            get_logger().exception('get_collection_handler, e=%s' % e)
            return
    return collection
