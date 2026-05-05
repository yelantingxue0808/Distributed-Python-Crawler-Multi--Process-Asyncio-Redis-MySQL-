"""
@Author  : 孔天宇
@Desc    :
"""
from utils import logger, utils

from config import settings, db_settings
from dao import data_base
from multiprocessing import current_process
import json


def save_data_mysql(data_list):
    # 连接数据库
    db = data_base.DataBase(db_settings.DatabaseConfig.MYSQL).get_connect()
    db.set_charset(charset='utf8')
    # 创建游标对象
    cursor = db.cursor()
    count = 0
    # 进程
    process_id = int(current_process().name.split('-')[-1])
    # 清空medical_table
    try:
        logger.get_logger().info('将数据保存到MYSQL中')
        # sql = 'truncate table medical_table'
        # cursor.execute(sql)
        sql = utils.build_insert_mysql(table='medical_table',
                                       fields=['品名', '规格', '市场', '价格', '趋势', '周涨跌', '月涨跌', '年涨跌'])
        # 将每个进程中的读取的100组8个字段组成的字典列表数据批量存入MYSQL
        for data in data_list:
            field_list = [data["品名"], data["规格"], data["市场"], data["价格"], data["趋势"],
                          data["周涨跌"], data["月涨跌"], data["年涨跌"]]
            if len(field_list) == 8:
                cursor.execute(sql, field_list)
                count += 1
                # 提交事务
                db.commit()
            else:
                logger.get_logger().info(f'处理的数据没有8个字段')
        logger.get_logger().info(f'进程{process_id}保存到MSQL中的数据总共{count}条')
    except Exception as error:
        logger.get_logger().warning('数据保存发生异常：', error)
        # 回滚事务
        db.rollback()
    # 关闭数据库
    db.close()
    cursor.close()


def save_data_redis(role, data=None):
    if role == settings.CrawlerRole.HEN:
        r, redis_config = data_base.DataBase(db_settings.DatabaseConfig.REDIS).get_connect(role)
        urls_dic = {"urls": data}
        urls_json = json.dumps(urls_dic)
        r.sadd(redis_config['key'], urls_json)
        # 返回集合的个数
        # process_id = int(current_process().name.split('-')[-1])
        logger.get_logger().info(f'累加存储了{r.scard(redis_config["key"])}个json格式的urls到redis\n')
        r.close()
    else:
        # 将解析后的数据存储进redis
        r, redis_config = data_base.DataBase(db_settings.DatabaseConfig.REDIS).get_connect(role)
        # 将列表组成一个json字符串存储到redis中
        data_dic = {redis_config['key']: data}
        parse_datas = json.dumps(data_dic)
        r.rpush(redis_config['key'], parse_datas)
        # 查看列表中有多少个元素
        logger.get_logger().info(f'redis列表中累积存储了{r.llen(redis_config["key"])}条数据')
        r.close()
