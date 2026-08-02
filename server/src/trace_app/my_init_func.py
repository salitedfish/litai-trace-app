from mg_app_framework import InitFuncBasic

from trace_app.service.device_status_service import load_initial_device_status
from trace_app.utils.db import get_db_handler, db_index_map


class MyInitFunc(InitFuncBasic):
    async def init_func(self):
        await add_indexes()
        # 预填设备实时状态，避免重启后看板设备状态全空
        await load_initial_device_status()


async def add_indexes():
    db = await get_db_handler(None)

    for collection_name, indexes in db_index_map.items():
        collection = db.get_collection(collection_name)

        try:
            existing_indexes = await collection.list_indexes().to_list(None)
            existing_index_keys = [
                tuple(idx['key']) for idx in existing_indexes
            ]

            for index in indexes:
                index_tuple = tuple(index)
                if index_tuple not in existing_index_keys:
                    await collection.create_index(index)

        except Exception as e:
            print(f"为集合 {collection_name} 创建索引时出错: {str(e)}")
            continue
