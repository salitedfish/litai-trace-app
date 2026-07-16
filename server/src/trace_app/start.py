from mg_app_framework import app_start, set_store, set_config_func, set_init_task, TaskKey

from trace_app.my_init_func import MyInitFunc
from trace_app.config import ConfigStore, MongodbConfig, RabbitMQConfig


async def config_process():
    pass


def main(debug_flag=True):
    set_store(ConfigStore())
    set_config_func(config_process)
    set_init_task([{TaskKey.idi_server: MongodbConfig()},
                   {TaskKey.init_func: MyInitFunc()},
                   {TaskKey.rabbitmq_async: RabbitMQConfig()}
                   ])
    app_start(debug_flag)
