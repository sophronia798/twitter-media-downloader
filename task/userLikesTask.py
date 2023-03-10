'''
Author: mengzonefire
Date: 2023-03-01 13:58:17
LastEditTime: 2023-03-10 18:33:01
LastEditors: mengzonefire
Description: likes页爬取任务类
'''

import json
import time
import traceback
import httpx

from common.const import *
from common.logger import writeLog
from common.text import *
from common.tools import getHttpText, parseData
from task.baseTask import Task


class UserLikesTask(Task):

    def __init__(self, userName: str, userId: int, media: bool):
        super(UserLikesTask, self).__init__()
        self.userName = userName
        self.userId = userId
        self.media = media
        self.savePath = os.path.join(getContext('dl_path'), userName, 'likes')

    def getDataList(self, cursor='', rest_id_list=[]):
        while True:
            if self.stop:
                return
            cursorPar = cursor and '"cursor":"{}",'.format(cursor)
            response = None
            with httpx.Client(proxies=getContext('proxy'), headers=getContext('headers'), verify=False) as client:
                for i in range(1, 6):
                    try:
                        response = client.get(userLikesApi, params={
                            'variables': userLikesApiPar.format(self.userId, twtCount, cursorPar),
                            'features': commonApiPar})
                        break
                    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError):
                        if i >= 5:
                            print(network_error_warning)
                            self.stopGetDataList()
                            return
                        else:
                            print(timeout_warning.format(i))
                            time.sleep(1)
            if not response:
                self.stopGetDataList()
                return
            if response.status_code != httpx.codes.OK:
                print(http_warning.format('UserLikesTask.getDataList',
                                          response.status_code, getHttpText(response.status_code)))
                self.stopGetDataList()
                return
            self.pageContent = response.json()
            try:
                cursor, rest_id_list = parseData(
                    self.pageContent, self.total, self.userName, self.dataList, rest_id_list=rest_id_list, includeNonMedia=self.media)
            except KeyError:
                self.errFlag = True
                print(parse_warning)
                writeLog(f'{self.userName}_unexpectData',
                         f'{traceback.format_exc()}\n\n{json.dumps(self.pageContent)}')  # debug
            except Exception as _:
                self.errFlag = True
                print(crash_warning)
                writeLog(f'{self.userName}_crash',
                         traceback.format_exc())  # debug
            finally:
                if self.errFlag or not cursor:
                    self.stopGetDataList()
                    return
