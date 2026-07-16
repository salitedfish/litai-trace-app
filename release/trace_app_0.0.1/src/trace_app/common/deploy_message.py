from mg_app_framework import (
    get_handler, TaskKey, get_organization,
    get_logger
)


async def deploy_message_via_mq(key, data, org=None, time_series_data=True):
    get_logger().debug("=" * 20)
    get_logger().debug(data)
    if org is None:
        org = get_organization()

    mq_handler = get_handler(TaskKey.rabbitmq_async)
    await mq_handler.publish_message({
        'key': key,
        'data': data
    }, org, time_series_data=time_series_data)
