"""
@Author  : 孔天宇
@Desc    :
"""
from config.settings import PageConfig
from config import settings
from core import handler
import asyncio


def get_url():
    """
    获取所有的url
    """
    urls = [settings.URL.format(page) for page in range(PageConfig.START + 1, PageConfig.STOP + 1)]
    return urls


async def batch_asyncio(urls):
    """
    协程批量执行任务
    """
    tasks = []
    for url in urls:
        coroutine = handler.parse_data(url)
        task = asyncio.create_task(coroutine)
        tasks.append(task)
    data_list = await asyncio.gather(*tasks)
    item_list = []
    for data in data_list:
        item_list.extend(data)
    return item_list


def build_insert_mysql(table, fields=None):
    """
    insert into table(fields) values(values)
    """
    fields = fields or ''
    values = ','.join(["%s"] * len(fields))
    fields = ','.join(fields)
    sql = f'insert {table}({fields}) values({values})'
    return sql
