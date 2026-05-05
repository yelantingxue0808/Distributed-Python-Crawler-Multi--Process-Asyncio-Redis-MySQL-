"""
@Author  : 孔天宇
@Desc    :
"""
import ast
from multiprocessing import Process
from utils import utils, logger
from core import handler
from config import settings


def execute_task(role=settings.DEFAULT_ROLE):
    processes = []
    for _ in range(settings.PROCESS):  # 控制进程的数量
        p = Process(target=handler.task_process, args=(role,))
        p.start()
        processes.append(p)

    for pro in processes:
        pro.join()
    if role == settings.CrawlerRole.HEN:
        logger.get_logger().info('urls数据已保存到redis的集合中')
    elif role == settings.CrawlerRole.CAT:
        logger.get_logger().info('解析的数据已保存到redis中')
    else:
        logger.get_logger().info('读取redis数据保存到MYSQL中')
