'''
Author: DefeedBack
Date: 2026-06-25 22:30:41
LastEditors: DefeedBack
LastEditTime: 2026-06-25 22:32:54
Description: 

Copyright (c) 2026 by 3102907235@qq.com, All Rights Reserved. 
'''

class AppException(Exception):
    """
    业务异常类"""
    def __init__(self, code: str, message:str,status_code: int=500):
        super().__init__(code,message,status_code)
        self.code = code
        self.message = message
        self.status_code = status_code

        