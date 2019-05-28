# -*- coding:utf-8 -*-
import requests
import json
from config import PINTEREST_CONFIG
from config import logger


class PinterestApi():
    """
    pinterest api接口
    """

    def __init__(self, access_token="", host=None):
        """
        :param access_token:
        :param host:
        """
        self.access_token = access_token
        self.pinterest_host = "https://api.pinterest.com/v1" if not host else host
        self.redirect_uri = PINTEREST_CONFIG.get("redirect_uri")
        self.client_id = PINTEREST_CONFIG.get("client_id")
        self.client_secret = PINTEREST_CONFIG.get("client_secret")
        self.scope = PINTEREST_CONFIG.get("scope")

    def get_pinterest_url(self, state):
        """
        获取授权code
        :param state: 自定义字段, 这可用于确保重定向回您的网站或应用程序不会被欺骗。
        :return:
        """
        url = f"https://api.pinterest.com/oauth/?response_type=code" \
            f"&redirect_uri={self.redirect_uri}" \
            f"&client_id={self.client_id}" \
            f"&scope={self.scope}&state={state}"
        return url

    def get_token(self, code):
        """
        # 获取token
        :param code:
        :return:
        """
        url = f"https://api.pinterest.com/v1/oauth/token?" \
            f"grant_type=authorization_code" \
            f"&client_id={self.client_id}&client_secret={self.client_secret}&code={code}"
        try:
            result = requests.post(url)
            if result.status_code == 200:
                logger.info("pinterest token success = {}".format(json.loads(result.text).get("access_token")))
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("pinterest token failed = {}".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def get_user_info(self):
        """
        返回当前用户的信息
        :return:
        """
        get_user_info_fields = ["first_name", "Cid", "Clast_name", "Curl", "Caccount_type", "Cbio", "Ccounts",
                                "Ccreated_at", "Cimage", "Cusername"]
        str_fields = "%2".join(get_user_info_fields)
        url = f"{self.pinterest_host}/me/?access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(url)
            if result.status_code == 200:
                logger.info("get user: {} info is success".format(json.loads(result.text)["data"]["username"]))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get user info failed".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def create_board(self, name, description):
        """
        创建board
        :param name:
        :param description:
        :return:
        """
        create_board_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription",
                               "Cimage", "Cprivacy", "Creason"]
        str_fields = "%2".join(create_board_fields)
        url = f"{self.pinterest_host}/boards/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "name": name,
            "description": description
        }
        try:
            result = requests.post(url, payload)
            if result.status_code == 200:
                logger.info("create user boards is success name={}".format(name))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("post user boards is failed:{}".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def get_user_boards(self):
        """
        获取用户的boards
        :param fields:
        :return:
        """
        get_user_boards_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription",
                                  "Cimage", "Cprivacy", "Creason"]
        str_fields = "%2".join(get_user_boards_fields)
        url = f"{self.pinterest_host}/me/boards/?access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(url)
            if result.status_code == 200:
                logger.info("get user boards is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get user boards failed: {}".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def get_board_id(self, board_id):
        """
        查询指定ID的board
        :param fields:
        :return:
        """
        get_board_id_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage",
                               "Cprivacy", "Creason"]
        str_fields = "%2".join(get_board_id_fields)
        url = f"{self.pinterest_host}/boards/{board_id}/?access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(url)
            if result.status_code == 200:
                logger.info("get by id board is success; board_id={}".format(board_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get by id board failed:{}".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def delete_board(self, board_id):
        """
        删除用户指定的board
        :param board_id:
        :return:
        """
        url = f"{self.pinterest_host}/boards/{board_id}/?access_token={self.access_token}"
        try:
            result = requests.delete(url)
            if result.status_code == 200:
                logger.info("delete board is success, board_id={}".format(board_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("delete board is failed: {}".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def edit_board_id(self, board_id, name, description):
        """
        编辑 board
        :param board_id:
        :param name:
        :param description:
        :return:
        """
        edit_board_id_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage",
                                "Cprivacy", "Creason"]
        str_fields = "%2".join(edit_board_id_fields)
        url = f"{self.pinterest_host}/boards/{board_id}/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "name": name,
            "description": description
        }
        try:
            result = requests.patch(url, payload)
            if result.status_code == 200:
                logger.info("edit board is success; board_id={},name={} ".format(board_id, name))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("edit board is failed".format(e))
            return {"code": -1, "msg": e, "data": ""}

    def create_pin(self, board_id, note, image_url, link):
        """
        创建 new pin
        :param board_id:
        :param note:
        :param image_url:
        :param link:
        :return: 发送的状态
        """
        create_pin_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Ccolor", "Cboard", "Ccounts",
                             "Ccreated_at", "Ccreator", "Cimage", "Cmedia", "Cmetadata", "Coriginal_link"]
        str_fields = "%2".join(create_pin_fields)
        api_request_url = f"{self.pinterest_host}/pins/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "board": board_id,
            "note": note,
            "image_url": image_url,
            "link": link
        }
        try:
            result = requests.post(api_request_url, json=payload)
            if result.status_code == 200:
                logger.info("create new pin is success; board_id={}".format(board_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.error("create new pin is failed; board_id={}".format(board_id))
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("create new pin is failed:{}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_user_pins(self):
        """
        获取当前用户的 pins
        :param fields:
        :return:
        """
        get_user_pins_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Cboard", "Ccolor", "Ccounts",
                                "Ccreated_at", "Ccreator", "Coriginal_link", "Cmedia", "Cmetadata", "Cimage"]
        str_fields = "%2".join(get_user_pins_fields)
        api_request_url = f"{self.pinterest_host}/me/pins/?cursor=&access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(api_request_url)
            if result.status_code == 200:
                logger.info("get user pins is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.error("get user pins is failed")
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get user pins is failed: {}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_pin_id(self, pin_id):
        """
        查询指定ID的pin信息
        :param pin_id:
        :param fields:
        :return:
        """
        get_pin_id_fields = ["id", "Cnote", "Curl", "Cattribution", "Cboard", "Ccounts", "Ccolor", "Ccreated_at",
                             "Ccreator", "Cimage", "Clink", "Cmedia", "Cmetadata", "Coriginal_link"]
        str_fields = "%2".join(get_pin_id_fields)
        api_request_url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(api_request_url)
            if result.status_code == 200:
                logger.info("get pin by id is success, pin_id={}".format(pin_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.info("get pin by id is failed, pin_id={}".format(pin_id))
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get pin by id is failed: {}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}

    def edit_pin_id(self, pin_id, board, note, link):
        """
        编辑 pin
        :param pin_id:
        :param board:
        :param note:
        :param link:
        :return:
        """
        edit_pin_id_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Cboard", "Ccolor", "Ccounts",
                              "Ccreated_at", "Ccreator", "Cmedia", "Cimage", "Cmetadata", "Coriginal_link"]
        str_fields = "%2".join(edit_pin_id_fields)
        api_request_url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "board": board,
            "note": note,
            "link": link
        }
        try:
            result = requests.patch(api_request_url, payload)
            if result.status_code == 200:
                logger.info("edit pin by id is success; pin_id={}".format(pin_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.info("edit pin by id is failed; pin_id={}".format(pin_id))
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("edit pin by id is failed: {}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}

    def delete_pin_id(self, pin_id):
        """
        # 删除 pin
        :param pin_id:
        :return:
        """
        url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}"
        try:
            result = requests.delete(url)
            if result.status_code == 200:
                logger.info("delete pin by id:{} is success".format(pin_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.info("delete pin by id:{} is failed".format(pin_id))
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("delete pin by id is failed: {}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_user_suggested(self, count):
        """
        :param count:
        :param fields:
        :return:
        """
        get_user_suggested_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription",
                                     "Cimage", "Cprivacy", "Creason"]
        str_fields = "%2".join(get_user_suggested_fields)
        url = f"{self.pinterest_host}/me/boards/suggested/?" \
              f"count={count}&access_token={self.access_token}&fields={str_fields}"
        try:
            result = requests.get(url)
            if result.status_code == 200:
                logger.info("get user suggest: {} is success".format(count))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("data", {})}
            else:
                logger.info("get user suggest: {} is failed".format(count))
                return {"code": 2, "msg": json.loads(result.text).get("message", ""), "data": ""}
        except Exception as e:
            logger.error("get user suggest is failed:{}".format(e))
            return {"code": -1, "msg": str(e), "data": ""}
            

if __name__ == '__main__':
    access_token = "ArVPxolYdQAXgzr0-FFoRGAF682xFaDsz-o3I1FF0n-lswCyYAp2ADAAAk1KRdOSuUEgxv0AAAAA"
    api_key = "5031224083375764064"
    api_password = "c3ed769d9c5802a98f7c4b949f234c482a19e5bf3a3ac491a0d20e44d7f7556e"
    code = "ae7fde7811cf4f17"
    all_pinterest_api = PinterestApi(access_token=access_token)
    # all_pinterest_api.get_user_pins(access_token=access_token)
    # all_pinterest_api.get_user_info()
    # all_pinterest_api.get_pinterest_url(state="twobercancan@gmail.com")
    # all_pinterest_api.delete_pin_id(pin_id="55451266411112")
    all_pinterest_api.get_user_pins()
    # all_pinterest_api.get_user_boards()
    # all_pinterest_api.get_pin_id(pin_id="753790056365099389")
    # all_pinterest_api.edit_board_id(board_id="753790125070479475", name="jjjjj", description="jjjjjjjjjjjjjjjjjjjjjjj")
    # all_pinterest_api.edit_pin_id(pin_id="753790056365099389", board="753790125070473943", note="tianchang", link="www.baidu.com")
