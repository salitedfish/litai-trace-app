from os.path import dirname, realpath, basename, join
from mg_app_framework import AppConfigBasic, AppType, MongodbConfigBasic, RabbitMQConfigBasic, get_store

from trace_app.utils.mq_config import subscribe_key_and_process_func, process_mq_msg


class MongodbConfig(MongodbConfigBasic):
    def get_mongodb_host(self):
        return '192.168.130.252'

    def get_mongodb_port(self):
        return '27017'


class RabbitMQConfig(RabbitMQConfigBasic):

    def get_rabbitmq_host(self):
        return '192.168.130.252'

    def get_rabbitmq_port(self):
        return 5672

    def get_rabbitmq_username(self):
        return 'rabbitmq'

    def get_rabbitmq_password(self):
        return 'realtech@123'

    def publish_config_data(self):
        return False

    def get_rabbitmq_subscribe_list(self):
        return list(subscribe_key_and_process_func.keys())

    def message_process_func(self):
        return process_mq_msg

    def ack_before_message_process_func(self):
        return False

    def set_qos_num(self):
        return 5


class ConfigStore(AppConfigBasic):
    # ==================== DON'T MODIFY THE CODE BETWEEN COMMENT LINE ====================

    work_dir = dirname(dirname(dirname(realpath(__file__))))
    app = basename(dirname(realpath(__file__)))
    log_path = join(work_dir, 'log', app + '.log')
    uuid_path = join(work_dir, '.appid')

    def get_module_dir(self):
        return dirname(realpath(__file__))

    def get_log_path(self):
        return self.log_path

    def get_uuid_path(self):
        return self.uuid_path

    def get_data(self):
        return self.data

    def organization_info(self):
        return {
            'code': 'buXiuGang'
        }

    # ==================== DON'T MODIFY THE CODE BETWEEN COMMENT LINE ====================

    data = {
        'app_group': '应用组件',
        'app_name': '追溯应用',
        'app_type': AppType.user,
        'app_version': '0.0.1',
        'app_module_name': 'trace_app',
        'config_create': False,
        'data': {}
    }

    def get_admin_host(self):
        return '127.0.0.1'

    def get_app_port(self):
        return 18085

    def connect_admin(self):
        return False

    def get_login_switch(self):
        return False

    def get_swagger_enable(self):
        return True
