"""
@Author  : 孔天宇
@Desc    : 
"""
from config import db_settings
import pymysql
from redis import StrictRedis
from config import settings


# 创建一个单例模式
class DataBase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, db_type=db_settings.DEFAULT_CONFIG_DATABASE):  # 默认的是redis数据库
        self.db_type = db_type

    @classmethod
    def get_redis_connect(cls, role):
        # 连接数据库
        redis_config = settings.REDIS_CONFIG[role]
        r = StrictRedis(host=redis_config["host"], password=redis_config["password"], db=redis_config['db'],
                        decode_responses=redis_config['decode_responses'])
        return r, redis_config

    @staticmethod
    def get_mysql_connect():
        mysql_conf = db_settings.MYSQL_CONFIG[db_settings.DatabaseConfig.MYSQL]
        host = mysql_conf['host']
        password = mysql_conf['password']
        database = mysql_conf['database']
        user = mysql_conf['user']
        db = pymysql.connect(host=host, password=password, database=database, user=user)
        return db

    def get_connect(self, role=None):
        if self.db_type == db_settings.DatabaseConfig.MYSQL:
            return self.get_mysql_connect()
        else:
            return self.get_redis_connect(role)
