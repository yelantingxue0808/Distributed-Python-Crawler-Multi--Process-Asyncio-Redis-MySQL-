"""
@Author  : 孔天宇
@Desc    :
"""
URL = "https://www.zyctd.com/jiage/1-0-0-{}.html"


class PageConfig:
    START = 0
    STOP = 122
    STEP = 35


class CrawlerRole:
    HEN = 0  # 抓取url ->redis
    CAT = 1  # 解析数据 ->redis
    PIG = 2  # 保存数据 —>mysql


DEFAULT_ROLE = CrawlerRole.PIG

PROCESS = 6

REDIS_CONFIG = {
    CrawlerRole.HEN: {
        'key': 'urls',
        'db': 2,
        'password': 123456,
        'decode_responses': True,
        'host': 'localhost'
    },
    CrawlerRole.CAT: {
        'key': 'parse_data',
        'db': 2,
        'password': 123456,
        'decode_responses': True,
        'host': 'localhost'
    },
    CrawlerRole.PIG: {
    }
}
