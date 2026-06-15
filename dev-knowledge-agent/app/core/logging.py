'''
Author: DefeedBack
Date: 2026-06-12 16:02:25
LastEditors: DefeedBack
LastEditTime: 2026-06-12 16:08:10
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''
import logging 
import sys

def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # 日志静音
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    