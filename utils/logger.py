"""
@Author  : 孔天宇
@Desc    :
"""
import logging
import os
from config import logging_settings


def get_logger():
    logger = logging.getLogger(logging_settings.LOGGER_NAME)
    # 如果有处理器，则返回logger,避免重复添加
    if logger.handlers:
        return logger
    if not os.path.exists(logging_settings.LOGGER_PATH):
        os.mkdir(logging_settings.LOGGER_PATH)
    path_file = os.path.join(logging_settings.LOGGER_PATH_FILE)

    logger.setLevel(level=logging.INFO)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename=path_file, encoding='utf-8', mode='a')

    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s : %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将处理器添加到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
