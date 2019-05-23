# -*- coding:utf-8 -*-
import requests


class PinterestApi():
    """
    pinterest api接口
    """

    def __init__(self, access_token="", host=None):
        self.access_token = access_token
        self.pinterest_host = "https://api.pinterest.com/v1" if not host else host
        self.redirect_uri = "http://sns.seamarketings.com/api/v1/pinterest/callback/"
        self.client_id = "5031224083375764064"
        self.client_secret = "c3ed769d9c5802a98f7c4b949f234c482a19e5bf3a3ac491a0d20e44d7f7556e"
        self.scope = "read_public,write_public,read_relationships,write_relationships"

    def get_pinterest_url(self, state):
        """
        获取授权code
        :param state: 自定义字段, 这可用于确保重定向回您的网站或应用程序不会被欺骗。
        :return:
        """
        url = f"https://api.pinterest.com/oauth/?response_type=code" \
            f"&redirect_uri={self.redirect_uri}" \
            f"&client_id={self.client_id}" \
            f"&scope={self.scope}&state= {state}"
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
        token_info = requests.post(url)
        return token_info.status_code, token_info.text

    def get_user_info(self):
        """
        返回当前用户的信息
        :return:
        """
        get_user_info_fields = ["first_name", "Cid", "Clast_name", "Curl", "Caccount_type", "Cbio", "Ccounts",
                                "Ccreated_at", "Cimage", "Cusername"]
        str_fields = "%2".join(get_user_info_fields)
        url = f"{self.pinterest_host}/me/?access_token={self.access_token}&fields={str_fields}"
        user_info = requests.get(url)
        print(user_info.status_code, user_info.text)
        return user_info.status_code, user_info.text

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
        new_bord = requests.post(url, payload)
        print(new_bord.status_code, new_bord.text)
        return new_bord.status_code, new_bord.text

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
        user_info = requests.get(url)
        print(user_info.status_code, user_info.text)
        return user_info.status_code, user_info.text

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
        user_info = requests.get(url)
        print(user_info.status_code, user_info.text)
        return user_info.status_code, user_info.text

    def delete_board(self, board_id):
        """
        删除用户指定的board
        :param board_id:
        :return:
        """
        url = f"{self.pinterest_host}/boards/{board_id}/?access_token={self.access_token}"
        delete_boards = requests.delete(url)
        return delete_boards.status_code

    def edit_doard(self, board_id):
        edit_board_id_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage",
                                "Cprivacy", "Creason"]
        str_fields = "%2".join(edit_board_id_fields)
        url = f"{self.pinterest_host}/boards/{board_id}/?access_token={self.access_token}&fields={str_fields}"
        user_info = requests.get(url)
        print(user_info.status_code, user_info.text)
        return user_info.status_code, user_info.text

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
        new_pin = requests.post(api_request_url, json=payload)
        print(new_pin.status_code, new_pin.text)
        return new_pin.status_code, new_pin.text

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
        new_pin = requests.get(api_request_url)
        print(new_pin.status_code, new_pin.text)
        return new_pin.status_code, new_pin.text

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
        new_pin = requests.get(api_request_url)
        print(new_pin.status_code, new_pin.text)
        return new_pin.status_code, new_pin.text

    def edit_pin_id(self, pin_id):
        """
        修改 pin
        :param pin_id:
        :return:
        """
        edit_pin_id_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Cboard", "Ccolor", "Ccounts",
                              "Ccreated_at", "Ccreator",
                              "Cmedia", "Cimage", "Cmetadata", "Coriginal_link"]
        str_fields = "%2".join(edit_pin_id_fields)
        api_request_url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}&fields={str_fields}"
        new_pin = requests.patch(api_request_url)
        return new_pin.status_code, new_pin.text

    def delete_pin_id(self, pin_id):
        """
        # 删除pin
        :param pin_id:
        :return:
        """
        url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}"
        delete_pin = requests.delete(url)
        return delete_pin.status_code, delete_pin.text

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
        user_suggested = requests.get(url)
        return user_suggested.status_code, user_suggested.text


if __name__ == '__main__':
    access_token = "ArVPxolYdQAXgzr0-FFoRGAF682xFaDsz-o3I1FF0n-lswCyYAp2ADAAAk1KRdOSuUEgxv0AAAAA"
    api_key = "5031224083375764064"
    api_password = "c3ed769d9c5802a98f7c4b949f234c482a19e5bf3a3ac491a0d20e44d7f7556e"
    code = "ae7fde7811cf4f17"
    all_pinterest_api = PinterestApi(access_token=access_token)
    # all_pinterest_api.get_user_pins(access_token=access_token)
    all_pinterest_api.get_pin_id(pin_id="753790056365099389")