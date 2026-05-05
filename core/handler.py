"""
@Author  : 孔天宇
@Desc    :
"""
import json

import aiohttp
import asyncio
from lxml import etree
from config import https_settings, settings, db_settings
from utils import logger, utils
from dao import save_data, data_base
from multiprocessing import current_process


async def send_url(url, session):
    """
    向url发送请求
    """
    async with session.get(url) as response:
        response_data = response.text(encoding='utf-8')
        return await response_data


async def parse_data(url):
    """
    解析数据
    """
    async with aiohttp.ClientSession(headers=https_settings.HEADERS) as session:
        # 阻塞等待，降低请求频率
        await asyncio.sleep(0.5)
        response_data = await send_url(url, session)
        # 使用xpath进行数据提取
        tree = etree.HTML(response_data, parser=None)
        all_list = []
        trs = tree.xpath("//tbody/tr")
        for tr in trs:
            try:
                item = {}
                tds = tr.xpath('./td[position()<9]')
                if len(tds) < 8:
                    continue

                item["品名"] = tds[0].xpath('./a[@title]/text()')[0] if tds[0].xpath('./a[@title]/text()') else ''
                item["规格"] = tds[1].xpath('./a[@title]/text()')[0] if tds[1].xpath(
                    './a[@title]/text()') else ''
                item["市场"] = tds[2].xpath('./text()')[0] if tds[2].xpath('./text()') else ''
                item["价格"] = tds[3].xpath('./text()')[0] if tds[3].xpath('./text()') else ''
                item["趋势"] = tds[4].xpath('./text()')[0] if tds[4].xpath('./text()') else ''
                item["周涨跌"] = tds[5].xpath('./text()')[0] if tds[5].xpath('./text()') else ''
                item["月涨跌"] = tds[6].xpath('./text()')[0] if tds[6].xpath('./text()') else ''
                item["年涨跌"] = tds[7].xpath('./text()')[0] if tds[7].xpath('./text()') else ''
                all_list.append(item)
                logger.get_logger().debug(f'{item}数据提取完成---{url}')
            except Exception as e:
                logger.get_logger().info(f'数据解析失败：{e}')
                continue
        return all_list


def task_process(role):
    """
    抓取url,解析数据、保存数据
    """
    if role == settings.CrawlerRole.HEN:
        # 将所有的urls，每个进程以30个url为一组进行存储
        process_id = int(current_process().name.split('-')[-1])
        urls_ = utils.get_url()
        for index in range(settings.PageConfig.START, settings.PageConfig.STOP, settings.PageConfig.STEP):
            # 以35个一组需要的进程数量,将122页的url分成4片
            group_count = index // settings.PageConfig.STEP + 1
            if group_count % settings.PROCESS == process_id % settings.PROCESS:
                urls_list = urls_[index: index + settings.PageConfig.STEP]
                # 将url存储到redis中
                save_data.save_data_redis(role, urls_list)
                logger.get_logger().info(f'进程{process_id}存储的区间范围是{index + 1}~{index + settings.PageConfig.STEP}'
                                         f'有{len(urls_list)}个url数据存储到redis中')

    elif role == settings.CrawlerRole.CAT:
        # 读取redis中的数据进行解析
        r, redis_config = data_base.DataBase(db_settings.DEFAULT_CONFIG_DATABASE).get_connect(role)
        redis_config_key = settings.REDIS_CONFIG[settings.CrawlerRole.HEN]['key']
        while True:
            # 循环：原子性弹出 URL 分片，直到集合为空（避免多进程重复处理）
            if r.scard(redis_config_key):
                # spop 是原子操作：多进程下每个进程只会拿到唯一的分片
                urls_str_json = r.spop(redis_config_key)
                urls_list = json.loads(urls_str_json)['urls']
                parse_data_list = asyncio.run(utils.batch_asyncio(urls_list))
                # 每100组数据组成一个列表放到redis中
                for index in range(0, len(parse_data_list), 100):
                    batch_data = parse_data_list[index:index + 100]
                    # 将解析的数据保存到redis中
                    save_data.save_data_redis(role, batch_data)
                logger.get_logger().info(f'将有{len(parse_data_list)}条解析完成的数据存储到redis中')

            else:
                logger.get_logger().info('redis集合为空，以抓取完所有url地址')
                break

    else:
        # 读取redis列表中的数据，将数据保存到mysql中
        # 每个进程读取redis列表中100组数据（100*8组），每100组数列表组成的数据存储到redis中
        r, redis_config = data_base.DataBase(db_settings.DatabaseConfig.REDIS).get_connect(settings.CrawlerRole.CAT)
        redis_config_key = redis_config['key']
        while True:
            if r.llen(redis_config_key):
                # 每读取100组(100*8)数据存入mysql,使用pop原子性弹出，直到为空
                redis_data = r.lpop(redis_config_key)
                # 将redis中的json数据转换成字典
                data_list = json.loads(redis_data)['parse_data']
                logger.get_logger().info(f'将有{len(data_list)}数据组成的列表存储到MYSQL')
                save_data.save_data_mysql(data_list)
            else:
                logger.get_logger().info(f'当前进程处理完了redis列表中所有数据,退出当前循环')
                break
