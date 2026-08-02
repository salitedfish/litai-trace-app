from mg_app_framework import get_logger, rabbitmq_publish_one

from trace_app.service.device_status_service import update_device_status

subscribe_key_and_process_func = {
    # 设备实时状态（device_exception_compute 推送，value 为状态码）
    "time_interval_status": update_device_status,
}


async def process_mq_msg(msg):
    msg_key = msg.get('key', None)
    msg_data = msg.get('data', None)
    if not msg_key:
        get_logger().error('msg key is None')
        return

    msg_process_func = subscribe_key_and_process_func.setdefault(msg_key, None)
    if not msg_process_func:
        get_logger().info('there is no process func for mq key:{} use default'.format(msg_key))
    else:
        await msg_process_func(msg_data)


async def send_rabbit_mq(data, key, time_series_data=True):
    await rabbitmq_publish_one(
        data={
            'key': key,
            'data': data
        },
        time_series_data=time_series_data
    )
    get_logger().info('successfully send MQ to ' + key + ' ' + str(data))
