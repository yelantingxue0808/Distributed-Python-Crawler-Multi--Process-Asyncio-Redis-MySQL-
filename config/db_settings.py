"""
@Author  : 孔天宇
@Desc    : 
"""


class DatabaseConfig:
    REDIS = 0
    MYSQL = 1
    MONGODB = 2


DEFAULT_CONFIG_DATABASE = DatabaseConfig.REDIS

MYSQL_CONFIG = {
    DatabaseConfig.MYSQL: {
        'host': 'localhost',
        'database': 'text3',
        'user': 'root',
        'password': '123456'

    }
}


