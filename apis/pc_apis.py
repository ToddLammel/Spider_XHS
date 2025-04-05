# encoding: utf-8
import asyncio
import csv
import json
import urllib
from dataclasses import dataclass, asdict
from enum import Enum, unique

import aiohttp

from loguru import logger
from encrypt import generate_params
from encrypt.misc_encrypt import MiscEncrypt


def splice_url(api, params):
    url = api + '?'
    for key, value in params.items():
        if value is None:
            value = ''
        url += key + '=' + value + '&'
    return url[:-1]


@dataclass(kw_only=True, slots=True)
class VideoInfo:
    title: str
    tag: str
    cover_url: str
    h265_url: str
    duration: int
    width: int
    height: int
    fps: int
    size: int


@unique
class ApiType(Enum):
    # 获取短信验证码
    GET_SMS_CODE = 0
    # 发送短信验证码
    SEND_SMS_CODE = 1
    # 获取主页所有频道
    GET_HOME_CATEGORY = 2
    # 获取主页推荐的频道
    GET_HOME_RECOMMEND = 3
    # 获取用户信息
    GET_USER_INFO = 4
    # 获取自己的信息
    GET_MY_INFO_V1 = 5
    # 获取自己的信息
    GET_MY_INFO_V2 = 6
    # 获取用户的笔记信息
    GET_USER_NOTE = 7
    # 获取用户笔记的详细信息
    GET_USER_POST_DETAIL = 8
    # 获取视频的详细信息
    GET_VIDEO_DETAIL = 9
    # 获取用户喜欢的笔记
    GET_USER_LIKE_NOTE = 10
    # 获取用户收藏的笔记
    GET_USER_COLLECT_NOTE = 11
    # 获取搜索关键词
    GET_SEARCH_KEY_WORD = 12
    # 通过搜索获取笔记
    GET_SEARCH_NOTE = 13
    # 通过搜索查找用户
    GET_SEARCH_USER = 14
    # 获取指定笔记的一级评论
    GET_NOTE_COMMENT = 15
    # 获取指定笔记的二级评论
    GET_NOTE_REPLY_COMMENT = 16
    # 获取未读消息
    GET_UNREAD_MESSAGE = 17
    # 获取评论和@提醒
    GET_COMMENT_AND_AT_REMIND = 18
    # 获取赞和收藏
    GET_LIKE_AND_COLLECT = 19
    # 获取新增关注
    GET_NEW_FOLLOW = 20


def get_url_by_api_type(api_type: ApiType):
    if api_type == ApiType.GET_SMS_CODE:
        return '/api/sns/web/v2/login/send_code'
    elif api_type == ApiType.SEND_SMS_CODE:
        return '/api/sns/web/v1/login/check_code'
    elif api_type == ApiType.GET_HOME_CATEGORY:
        return '/api/sns/web/v1/homefeed/category'
    elif api_type == ApiType.GET_HOME_RECOMMEND:
        return '/api/sns/web/v1/homefeed'
    elif api_type == ApiType.GET_USER_INFO:
        return '/api/sns/web/v1/user/otherinfo'
    elif api_type == ApiType.GET_MY_INFO_V1:
        return '/api/sns/web/v1/user/selfinfo'
    elif api_type == ApiType.GET_MY_INFO_V2:
        return '/api/sns/web/v2/user/me'
    elif api_type == ApiType.GET_USER_NOTE:
        return '/api/sns/web/v1/user_posted'
    elif api_type == ApiType.GET_USER_POST_DETAIL:
        return '/api/sns/web/v1/feed'
    elif api_type == ApiType.GET_VIDEO_DETAIL:
        return '/api/sns/web/v1/feed'
    elif api_type == ApiType.GET_USER_LIKE_NOTE:
        return '/api/sns/web/v1/note/like/page'
    elif api_type == ApiType.GET_USER_COLLECT_NOTE:
        return '/api/sns/web/v2/note/collect/page'
    elif api_type == ApiType.GET_SEARCH_KEY_WORD:
        return '/api/sns/web/v1/search/recommend'
    elif api_type == ApiType.GET_SEARCH_NOTE:
        return '/api/sns/web/v1/search/notes'
    elif api_type == ApiType.GET_SEARCH_USER:
        return '/api/sns/web/v1/search/usersearch'
    elif api_type == ApiType.GET_NOTE_COMMENT:
        return '/api/sns/web/v2/comment/page'
    elif api_type == ApiType.GET_NOTE_REPLY_COMMENT:
        return '/api/sns/web/v2/comment/sub/page'
    elif api_type == ApiType.GET_UNREAD_MESSAGE:
        return '/api/sns/web/unread_count'
    elif api_type == ApiType.GET_COMMENT_AND_AT_REMIND:
        return '/api/sns/web/v1/you/mentions'
    elif api_type == ApiType.GET_LIKE_AND_COLLECT:
        return '/api/sns/web/v1/you/likes'
    elif api_type == ApiType.GET_NEW_FOLLOW:
        return '/api/sns/web/v1/you/connections'

"""
    获小红书的api
    :param cookies_str: 你的cookies
"""
class XhsApi:
    def __init__(self, cookies: str = None, proxies: dict = None):
        if cookies:
            self._cookies = cookies
        else:
            raise Exception("请传入小红书的cookies")
        self._proxies = proxies
        self._base_url = "https://edith.xiaohongshu.com"

    async def get(self, api: str) -> (bool, str, dict):
        try:
            res_json = None
            async with (aiohttp.ClientSession() as s):
                _headers, _cookies, _data = await generate_params(api, data=None, cookies=self._cookies)
                url = self._base_url + api
                async with (
                    s.get(url, headers=_headers, cookies=_cookies, proxy=self._proxies) as response
                ):
                    res_json = await response.json()
                    success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, res_json

    async def post(self, api: str, data: dict) -> (bool, str, dict):
        try:
            res_json = None
            async with (aiohttp.ClientSession() as s):
                _headers, _cookies, _data = await generate_params(api, data, cookies=self._cookies)
                url = self._base_url + api
                async with (
                    s.post(url, headers=_headers, data=_data, cookies=_cookies, proxy=self._proxies) as response
                ):
                    res_json = await response.json()
                    success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, res_json

    async def get_sms_code(self, phone: str)  -> (bool, str, dict):
        """
        手机登录获取验证码
        :param phone: 手机号
        :return:
        """
        api = get_url_by_api_type(ApiType.GET_SMS_CODE).format(phone)
        params = {
            "phone": phone,
            "zone": "86",
            "type": "login"
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def login_by_sms_code(self, phone: str, sms_code: str) -> (bool, str, dict):
        """
        手机登录
        :param phone:
        :param sms_code:
        :return:
        """
        api = get_url_by_api_type(ApiType.SEND_SMS_CODE)
        params = {
            "phone": phone,
            "zone": "86",
            "code": sms_code
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_homefeed_all_channel(self) -> (bool, str, dict):
        """
            获取主页的所有频道
            返回主页的所有频道
        """
        api = get_url_by_api_type(ApiType.GET_HOME_CATEGORY)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    # TODO 这个接口不确定怎么用 抓包没看到
    async def get_homefeed_recommend(self, category, cursor_score, refresh_type, note_index):
        """
            获取主页推荐的笔记
            :param category: 你想要获取的频道
            :param cursor_score: 你想要获取的笔记的cursor 默认为''
            :param refresh_type: 你想要获取的笔记的刷新类型 默认为1
            :param note_index: 你想要获取的笔记的index    默认为0
            返回主页推荐的笔记
        """
        api = get_url_by_api_type(ApiType.GET_HOME_RECOMMEND)
        data = {
            "cursor_score": cursor_score,
            "num": 20,
            "refresh_type": refresh_type,
            "note_index": note_index,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": category,
            "search_key": "",
            "need_num": 10,
            "image_formats": [
                "jpg",
                "webp",
                "avif"
            ],
            "need_filter_image": False
        }
        success, msg, res_json = await self.post(api, data)
        return success, msg, res_json

    # TODO 这个接口不确定怎么用 抓包没看到
    def get_homefeed_recommend_by_num(self, category, require_num, cookies_str: str, proxies: dict = None):
        """
            根据数量获取主页推荐的笔记
            :param category: 你想要获取的频道
            :param require_num: 你想要获取的笔记的数量
            :param cookies_str: 你的cookies
            根据数量返回主页推荐的笔记
        """
        cursor_score, refresh_type, note_index = "", 1, 0
        note_list = []
        try:
            while True:
                success, msg, res_json = self.get_homefeed_recommend(category, cursor_score, refresh_type, note_index, cookies_str, proxies)
                if not success:
                    raise Exception(msg)
                if "items" not in res_json["data"]:
                    break
                notes = res_json["data"]["items"]
                note_list.extend(notes)
                cursor_score = res_json["data"]["cursor_score"]
                refresh_type = 3
                note_index += 20
                if len(note_list) > require_num:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        if len(note_list) > require_num:
            note_list = note_list[:require_num]
        return success, msg, note_list

    async def get_user_info(self, user_id: str) -> (bool, str, dict):
        """
            获取用户的信息
            :param user_id: 你想要获取的用户的id
            返回用户的信息
        """
        api = get_url_by_api_type(ApiType.GET_USER_INFO)
        params = {
            "target_user_id": user_id
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_self_info(self) -> (bool, str, dict):
        """
            获取用户自己的信息1
            返回用户自己的信息1
        """
        api = get_url_by_api_type(ApiType.GET_MY_INFO_V1)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_self_info_v2(self) -> (bool, str, dict):
        """
            获取用户自己的信息2
            返回用户自己的信息2
        """
        api = get_url_by_api_type(ApiType.GET_MY_INFO_V2)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_note_info(self, user_id: str, cursor: str, xsec_token='', xsec_source='') -> (bool, str, dict):
        """
            获取用户指定位置的笔记
            :param user_id: 你想要获取的用户的id
            :param cursor: 你想要获取的笔记的cursor
            :param xsec_token: 你想要获取的笔记的xsec_token 默认为空
            :param xsec_source: 你想要获取的笔记的xsec_source 默认为pc_search
            返回用户指定位置的笔记
        """
        api = get_url_by_api_type(ApiType.GET_USER_NOTE)
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_all_notes(self, user_url: str) -> (bool, str, list):
        """
           :param user_url: 你想要获取的用户的url
           返回用户的所有笔记
        """
        # 第一个cursor为空
        cursor = ''
        note_list = []
        try:
            urlParse = urllib.parse.urlparse(user_url)
            user_id = urlParse.path.split("/")[-1]
            kvs = urlParse.query.split('&')
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            xsec_token = kvDist['xsec_token'] if 'xsec_token' in kvDist else ""
            xsec_source = kvDist['xsec_source'] if 'xsec_source' in kvDist else "pc_search"
            while True:
                success, msg, res_json = await self.get_user_note_info(user_id, cursor, xsec_token, xsec_source)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, note_list

    async def get_note_info(self, note_id: str, xsec_source: str, xsec_token: str) -> (bool, str, dict):
        """
            获取笔记的详细
            :param note_id: 你想要获取的笔记的id
            :param xsec_source: 笔记的xsec_source 默认为pc_search pc_user pc_feed
            :param xsec_token: 笔记的xsec_token
            返回笔记的详细
        """
        api = get_url_by_api_type(ApiType.GET_VIDEO_DETAIL)
        data = {
            "source_note_id": note_id,
            "image_formats": [
                "jpg",
                "webp",
                "avif"
            ],
            "extra": {
                "need_body_topic": "1"
            },
            "xsec_source": xsec_source,
            "xsec_token": xsec_token
        }
        success, msg, res_json = await self.post(api, data)
        return success, msg, res_json

    async def get_video_urls(self, user_url: str) -> (bool, str, list):
        def handle_video_info(info: dict) -> VideoInfo:
            _video_info = VideoInfo(
                title=res_json['data']['items'][0]['note_card']['title'],
                tag=res_json['data']['items'][0]['note_card']['desc'],
                cover_url=res_json['data']['items'][0]['note_card']['image_list'][0]['url_pre'],
                duration=res_json['data']['items'][0]['note_card']['video']['media']['video']['duration'],
                fps=res_json['data']['items'][0]['note_card']['video']['media']['stream']['h265'][0]['fps'],
                width=res_json['data']['items'][0]['note_card']['video']['media']['stream']['h265'][0]['width'],
                height=res_json['data']['items'][0]['note_card']['video']['media']['stream']['h265'][0][
                    'height'],
                size=res_json['data']['items'][0]['note_card']['video']['media']['stream']['h265'][0]['size'],
                h265_url=res_json['data']['items'][0]['note_card']['video']['media']['stream']['h265'][0][
                    'master_url']
            )
            return _video_info

        success, msg, note_list = await self.get_user_all_notes(user_url)
        note_params = []
        # 提取必要参数 用于请求获取视频地址
        for note in note_list:
            if note['type'] == 'video':
                note_params.append((note['note_id'], note['xsec_token']))

        note_list = []
        for index, params in enumerate(note_params):
            note_id, xsec_token = params
            try:
                success, msg, res_json = await self.get_note_info(note_id, 'pc_user', xsec_token)
                video_info = handle_video_info(res_json)
                note_list.append(asdict(video_info))
            except Exception as e:
                success = False
                msg = str(e)
        return success, msg, note_list

    async def get_user_like_note_info(self, user_id: str, cursor: str, xsec_token='', xsec_source='') -> (bool, str, dict):
        """
            获取用户指定位置喜欢的笔记
            :param user_id: 你想要获取的用户的id
            :param cursor: 你想要获取的笔记的cursor
            :param xsec_token: 你想要获取的笔记的xsec_token 默认为空
            :param xsec_source: 你想要获取的笔记的xsec_source 默认为pc_search
            返回用户指定位置喜欢的笔记
        """
        api = get_url_by_api_type(ApiType.GET_USER_LIKE_NOTE)
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_all_like_note_info(self, user_url: str) -> (bool, str, list):
        """
            获取用户所有喜欢笔记
            注意：如果用户设置了隐私，则获取不到喜欢的笔记
            :param user_url: 你想要获取的用户的url
            返回用户的所有喜欢笔记
        """
        cursor = ''
        note_list = []
        try:
            urlParse = urllib.parse.urlparse(user_url)
            user_id = urlParse.path.split("/")[-1]
            kvs = urlParse.query.split('&')
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            xsec_token = kvDist['xsec_token'] if 'xsec_token' in kvDist else ""
            xsec_source = kvDist['xsec_source'] if 'xsec_source' in kvDist else "pc_user"
            while True:
                success, msg, res_json = await self.get_user_like_note_info(user_id, cursor, xsec_token, xsec_source)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, note_list

    async def get_user_collect_note_info(self, user_id: str, cursor: str, xsec_token='', xsec_source='') -> (bool, str, list):
        """
            获取用户指定位置收藏的笔记
            :param user_id: 你想要获取的用户的id
            :param cursor: 你想要获取的笔记的cursor
            :param xsec_token: 你想要获取的笔记的xsec_token 默认为空
            :param xsec_source: 你想要获取的笔记的xsec_source 默认为pc_search
            返回用户指定位置收藏的笔记
        """
        api = get_url_by_api_type(ApiType.GET_USER_COLLECT_NOTE)
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_user_all_collect_note_info(self, user_url: str) -> (bool, str, list):
        """
            获取用户所有收藏笔记
            注意：如果用户设置了隐私，则获取不到收藏的笔记
            :param user_url: 你想要获取的用户的url
            返回用户的所有收藏笔记
        """
        cursor = ''
        note_list = []
        try:
            urlParse = urllib.parse.urlparse(user_url)
            user_id = urlParse.path.split("/")[-1]
            kvs = urlParse.query.split('&')
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            xsec_token = kvDist['xsec_token'] if 'xsec_token' in kvDist else ""
            xsec_source = kvDist['xsec_source'] if 'xsec_source' in kvDist else "pc_search"
            while True:
                success, msg, res_json = await self.get_user_collect_note_info(user_id, cursor, xsec_token, xsec_source)
                if not success:
                    raise Exception(msg)
                notes = res_json["data"]["notes"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, note_list

    async def get_search_keyword(self, word: str) -> (bool, str, dict):
        """
            获取搜索关键词
            :param word: 你的关键词
            返回搜索关键词
        """
        api = get_url_by_api_type(ApiType.GET_SEARCH_KEY_WORD)
        params = {
            "keyword": urllib.parse.quote(word)
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def search_note(self, query: str, page: int=1, sort: str="general", note_type:int =0) -> (bool, str, dict):
        """
            获取搜索笔记的结果
            :param query: 搜索的关键词
            :param page: 搜索的页数
            :param sort: 排序方式 general:综合排序, time_descending:时间排序, popularity_descending:热度排序
            :param note_type: 笔记类型 0:全部, 1:视频, 2:图文
            返回搜索的结果
        """
        api = get_url_by_api_type(ApiType.GET_SEARCH_NOTE)
        data = {
            "keyword": query,
            "page": page,
            "page_size": 20,
            "search_id": await MiscEncrypt.x_b3_traceid(),
            "sort": sort,
            "note_type": note_type,
            "ext_flags": [],
            "image_formats": [
                "jpg",
                "webp",
                "avif"
            ]
        }
        success, msg, res_json = await self.post(api, data)
        return success, msg, res_json

    async def search_some_note(self, query: str, require_num: int, sort="general", note_type=0) -> (bool, str, list):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query: 搜索的关键词
            :param require_num: 搜索的数量
            :param sort: 排序方式 general:综合排序, time_descending:时间排序, popularity_descending:热度排序
            :param note_type: 笔记类型 0:全部, 1:视频, 2:图文
            返回搜索的结果
        """
        page = 1
        note_list = []
        try:
            while True:
                success, msg, res_json = await self.search_note(query, page, sort, note_type)
                if not success:
                    raise Exception(msg)
                if "items" not in res_json["data"]:
                    break
                notes = res_json["data"]["items"]
                note_list.extend(notes)
                page += 1
                if len(note_list) >= require_num or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        if len(note_list) > require_num:
            note_list = note_list[:require_num]
        return success, msg, note_list

    async def search_user(self, query: str, page: int=1) -> (bool, str, dict):
        """
            获取搜索用户的结果
            :param query: 搜索的关键词
            :param page: 搜索的页数
            返回搜索的结果
        """
        api = get_url_by_api_type(ApiType.GET_SEARCH_USER)
        data = {
            "search_user_request": {
                "keyword": query,
                "search_id": "2dn9they1jbjxwawlo4xd",
                "page": page,
                "page_size": 15,
                "biz_type": "web_search_user",
                "request_id": "22471139-1723999898524"
            }
        }
        success, msg, res_json = await self.post(api, data)
        return success, msg, res_json

    async def search_some_user(self, query: str, require_num: int) -> (bool, str, list):
        """
            指定数量搜索用户
            :param query: 搜索的关键词
            :param require_num: 搜索的数量
            返回搜索的结果
        """
        page = 1
        user_list = []
        try:
            while True:
                success, msg, res_json = await self.search_user(query, page)
                if not success:
                    raise Exception(msg)
                if "users" not in res_json["data"]:
                    break
                users = res_json["data"]["users"]
                user_list.extend(users)
                page += 1
                if len(user_list) >= require_num or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        if len(user_list) > require_num:
            user_list = user_list[:require_num]
        return success, msg, user_list

    async def get_note_out_comment(self, note_id: str, cursor: str, xsec_token: str):
        """
            获取指定位置的笔记一级评论
            :param note_id 笔记的id
            :param cursor 指定位置的评论的cursor
            :param xsec_token 笔记的xsec_token
            返回指定位置的笔记一级评论
        """
        api = get_url_by_api_type(ApiType.GET_NOTE_COMMENT)
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_note_all_out_comment(self, note_id: str, xsec_token: str) -> (bool, str, list):
        """
            获取笔记的全部一级评论
            :param note_id 笔记的id
            :param xsec_token 笔记的xsec_token
            返回笔记的全部一级评论
        """
        cursor = ''
        note_out_comment_list = []
        try:
            while True:
                success, msg, res_json = await self.get_note_out_comment(note_id, cursor, xsec_token)
                if not success:
                    raise Exception(msg)
                comments = res_json["data"]["comments"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                note_out_comment_list.extend(comments)
                if len(note_out_comment_list) == 0 or not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, note_out_comment_list

    async def get_note_inner_comment(self, comment: dict, cursor: str, xsec_token: str) -> (bool, str, dict):
        """
            获取指定位置的笔记二级评论
            :param comment: 笔记的一级评论
            :param cursor: 指定位置的评论的cursor
            :param xsec_token: 笔记的xsec_token
            返回指定位置的笔记二级评论
        """
        api = get_url_by_api_type(ApiType.GET_NOTE_REPLY_COMMENT)
        params = {
            "note_id": comment['note_id'],
            "root_comment_id": comment['id'],
            "num": "10",
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "top_comment_id": '',
            "xsec_token": xsec_token
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_note_all_inner_comment(self, comment: dict, xsec_token: str) -> (bool, str, list):
        """
            获取笔记的全部二级评论
            :param comment: 笔记的一级评论
            :param xsec_token: 笔记的xsec_token
            返回笔记的全部二级评论
        """
        try:
            if not comment['sub_comment_has_more']:
                return True, 'success', comment
            cursor = comment['sub_comment_cursor']
            inner_comment_list = []
            while True:
                success, msg, res_json = await self.get_note_inner_comment(comment, cursor, xsec_token)
                if not success:
                    raise Exception(msg)
                comments = res_json["data"]["comments"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                inner_comment_list.extend(comments)
                if not res_json["data"]["has_more"]:
                    break
            comment['sub_comments'].extend(inner_comment_list)
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, comment

    async def get_note_all_comment(self, url: str) -> (bool, str, list):
        """
            获取一篇文章的所有评论
            :param url: 你想要获取的笔记的url
            返回一篇文章的所有评论
        """
        out_comment_list = []
        try:
            urlParse = urllib.parse.urlparse(url)
            note_id = urlParse.path.split("/")[-1]
            kvs = urlParse.query.split('&')
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            success, msg, out_comment_list = await self.get_note_all_out_comment(note_id, kvDist['xsec_token'])
            if not success:
                raise Exception(msg)
            for comment in out_comment_list:
                success, msg, new_comment = self.get_note_all_inner_comment(comment, kvDist['xsec_token'])
                if not success:
                    raise Exception(msg)
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, out_comment_list

    async def get_unread_message(self) -> (bool, str, dict):
        """
            获取未读消息
            返回未读消息
        """
        api = get_url_by_api_type(ApiType.GET_UNREAD_MESSAGE)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_metions(self, cursor: str) -> (bool, str, dict):
        """
            获取评论和@提醒
            :param cursor: 你想要获取的评论和@提醒的cursor
            返回评论和@提醒
        """
        api = get_url_by_api_type(ApiType.GET_COMMENT_AND_AT_REMIND)
        params = {
            "num": "20",
            "cursor": cursor
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_all_metions(self) -> (bool, str, list):
        """
            获取全部的评论和@提醒
            返回全部的评论和@提醒
        """
        cursor = ''
        metions_list = []
        try:
            while True:
                success, msg, res_json = await self.get_metions(cursor)
                if not success:
                    raise Exception(msg)
                metions = res_json["data"]["message_list"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                metions_list.extend(metions)
                if not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, metions_list

    async def get_likes_and_collects(self, cursor: str) -> (bool, str, dict):
        """
            获取赞和收藏
            :param cursor: 你想要获取的赞和收藏的cursor
            返回赞和收藏
        """
        api = get_url_by_api_type(ApiType.GET_LIKE_AND_COLLECT)
        params = {
            "num": "20",
            "cursor": cursor
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_all_likes_and_collects(self) -> (bool, str, list):
        """
            获取全部的赞和收藏
            返回全部的赞和收藏
        """
        cursor = ''
        likes_and_collects_list = []
        try:
            while True:
                success, msg, res_json = await self.get_likes_and_collects(cursor)
                if not success:
                    raise Exception(msg)
                like_and_collect = res_json["data"]["message_list"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                likes_and_collects_list.extend(like_and_collect)
                if not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, likes_and_collects_list

    async def get_new_followers(self, cursor: str) -> (bool, str, dict):
        """
            获取新增关注
            :param cursor: 你想要获取的新增关注的cursor
            返回新增关注
        """
        api = get_url_by_api_type(ApiType.GET_NEW_FOLLOW)
        params = {
            "num": "20",
            "cursor": cursor
        }
        api = splice_url(api, params)
        success, msg, res_json = await self.get(api)
        return success, msg, res_json

    async def get_all_new_followers(self):
        """
            获取全部的新增关注
            返回全部的新增关注
        """
        cursor = ''
        connections_list = []
        try:
            while True:
                success, msg, res_json = await self.get_new_followers(cursor)
                if not success:
                    raise Exception(msg)
                connections = res_json["data"]["message_list"]
                if 'cursor' in res_json["data"]:
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                connections_list.extend(connections)
                if not res_json["data"]["has_more"]:
                    break
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, connections_list

    @staticmethod
    def get_note_no_water_img(img_url):
        """
            获取笔记无水印图片
            :param img_url: 你想要获取的图片的url
            返回笔记无水印图片
        """
        success = True
        msg = '成功'
        new_url = None
        try:
            if '.jpg' in img_url:
                img_id = '/'.join([split for split in img_url.split('/')[-3:]]).split('!')[0]
                new_url = f'https://sns-img-qc.xhscdn.com/{img_id}'

            elif 'spectrum' in img_url:
                img_id = '/'.join(img_url.split('/')[-2:]).split('!')[0]
                new_url = f'http://sns-webpic.xhscdn.com/{img_id}?imageView2/2/w/format/jpg'
            else:
                img_id = img_url.split('/')[-1].split('!')[0]
                new_url = f'https://sns-img-qc.xhscdn.com/{img_id}'
        except Exception as e:
            success = False
            msg = str(e)
        return success, msg, new_url


def write_video_info_to_csv(video_info_list, filename):
    """将 VideoInfo 列表写入 CSV 文件。"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'tag', 'cover_url', 'duration', 'width', 'height', 'fps', 'size', 'h265_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for video_info in video_info_list:
            writer.writerow({
                'title': video_info.title,
                'tag': video_info.tag,
                'cover_url': video_info.cover_url,
                'duration': video_info.duration,
                'width': video_info.width,
                'height': video_info.height,
                'fps': video_info.fps,
                'size': video_info.size,
                'h265_url': video_info.h265_url
            })


if __name__ == '__main__':
    """
        此文件为小红书api的使用示例
        所有涉及数据爬取的api都在此文件中
        数据注入的api违规请勿尝试
    """
    # cookies是登录后的cookies
    cookies = r'abRequestId=92fcc04b-656b-509f-8a1e-c3ac8e497f23; a1=1956beb135e5lv46l69faxnx5tbuna61jz5pwoev850000427689; webId=e78b2e096f0b8a5aab4ee52ffa364b7d; gid=yj2KDdDJdfVDyj2KDdDyquld2d21h4K1Kji02hYCIC29DU287I0KyE8884JWKYj8S8ySSW80; x-user-id-creator.xiaohongshu.com=5e24fb75000000000100509f; customerClientId=942161409810786; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517486023646732033249ppejtee9xgofm0jp; galaxy_creator_session_id=gMM7NUHERAH9g2VJs89BsXjoRkhcUTGcu5FV; galaxy.creator.beaker.session.id=1742975704346011423609; xsecappid=xhs-pc-web; web_session=0400698f50b83d5600c98361d9354b8bb5902b; webBuild=4.62.1; acw_tc=0a4a661517438347833435632e23dabb3dc4399a0de12944f921ceec5e715e; unread={%22ub%22:%2267e5cd6a000000001a007a3b%22%2C%22ue%22:%2267e23cbe000000000603e2cc%22%2C%22uc%22:18}; loadts=1743835074786; websectiga=9730ffafd96f2d09dc024760e253af6ab1feb0002827740b95a255ddf6847fc8; sec_poison_id=a51d1970-f16e-4338-9763-15f76e46de95'
    xhs_apis = XhsApi(cookies=cookies)

    async def test():
        success, msg, res_json = await xhs_apis.search_some_note('人口', require_num=10)
        logger.info(f'登录结果 {json.dumps(res_json, ensure_ascii=False)}: {success}, msg: {msg}')

    asyncio.run(test())


