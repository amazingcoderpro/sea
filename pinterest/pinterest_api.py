# -*- coding:utf-8 -*-
import requests


class All_Pinterest_Api():
    """
    pinterest api接口
    """
    def __init__(self, access_token, host=None):
        self.access_token = access_token
        self.pinterest_host = "https://api.pinterest.com/v1" if not host else host
        self.get_user_info_fields = ["first_name", "Cid", "Clast_name", "Curl", "Caccount_type", "Cbio", "Ccounts", "Ccreated_at", "Cimage", "Cusername"]
        self.create_board_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage", "Cprivacy", "Creason"]
        self.get_board_id_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage", "Cprivacy", "Creason"]
        self.get_user_boards_fields = ["id", "Cname", "url", "created_at", "description", "image", "privacy", "Creason"]
        self.get_user_suggested_fields = ["id", "Cname", "Curl", "Ccounts", "Ccreated_at", "Ccreator", "Cdescription", "Cimage", "Cprivacy", "Creason"]
        self.create_pin_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Ccolor", "Cboard", "Ccounts", "Ccreated_at", "Ccreator", "Cimage", "Cmedia", "Cmetadata", "Coriginal_link"]
        self.get_pin_id_fields = ["id", "Cnote", "Curl", "Cattribution", "Cboard", "Ccounts", "Ccolor", "Ccreated_at", "Ccreator", "Cimage", "Clink", "Cmedia", "Cmetadata", "Coriginal_link"]
        self.get_user_pins_fields = ["id", "Clink", "Cnote", "Curl", "Cattribution", "Cboard", "Ccolor", "Ccounts", "Ccreated_at", "Ccreator", "Coriginal_link", "Cmedia", "Cmetadata", "Cimage"]

    def get_pinterest_code(self, redirect_uri, client_id, scope, state):
        """
        获取授权code
        :param redirect_uri: 重定向的url
        :param client_id: app id
        :param scope: 权限范围
        :param state: 自定义字段, 这可用于确保重定向回您的网站或应用程序不会被欺骗。
        :return:
        """
        url = "https://api.pinterest.com/oauth/?response_type=code" \
              "&redirect_uri={}" \
              "&client_id={}" \
              "&scope={}&state= {}".format(redirect_uri, client_id, scope, state)
        code = requests.get(url)
        return code

    def get_user_info(self, fields=[]):
        """
        返回当前用户的信息
        :return:
        """
        if not fields:
            fields = self.get_user_info_fields
        str_fields = "%2".join(fields)
        url = f"{self.pinterest_host}/me/?access_token={self.access_token}&fields={str_fields}"
        user_info = requests.get(url)
        return user_info.status_code, user_info.text

    def create_board(self, name, description, fields=[]):
        """
        创建board
        :return: board的发送状态
        """
        if not fields:
            fields = self.create_board_fields
        str_fields = "%2".join(fields)
        url = f"{self.pinterest_host}/boards/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "name": name,
            "description": description
        }
        new_bord = requests.post(url, payload)
        print(new_bord.status_code, new_bord.text)
        return new_bord.status_code, new_bord.text

    def get_user_boards(self, fields=[]):
        """
        获取用户的boards
        :param fields:
        :return:
        """
        if not fields:
            fields = self.get_user_boards_fields
        str_fields = "%2".join(fields)
        url = f"{self.pinterest_host}/me/boards/?access_token={self.access_token}&fields={str_fields}"
        user_info = requests.get(url)
        print(user_info.status_code, user_info.text)
        return user_info.status_code, user_info.text

    def get_board_id(self, board_id, fields=[]):
        """
        查询指定ID的board
        :param fields:
        :return:
        """
        if not fields:
            fields = self.get_board_id_fields
        str_fields = "%2".join(fields)
        "{}/boards/{}/?access_token={}&fields={}"
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

    def create_pin(self, board_id, note, image_url, link, fields=[]):
        """
        创建 new pin
        :param board_id:
        :param note:
        :param image_url:
        :param link:
        :return: 发送的状态
        """
        if not fields:
            fields = self.create_pin_fields
        str_fields = "%2".join(fields)
        api_request_url = f"{self.pinterest_host}/pins/?access_token={self.access_token}&fields={str_fields}"
        payload = {
            "board": board_id,
            "note": note,
            "image_url": image_url,
            "link": link
        }
        new_pin = requests.post(api_request_url, json=payload)
        return new_pin.status_code, new_pin.text

    def get_user_pins(self, fields=[]):
        """
        获取当前用户的 pins
        :param fields:
        :return:
        """
        if not fields:
            fields = self.get_user_pins_fields
        str_fields = "%2".join(fields)
        api_request_url = f"{self.pinterest_host}/me/pins/?cursor=&access_token={self.access_token}&fields={str_fields}"
        new_pin = requests.get(api_request_url)
        return new_pin.status_code, new_pin.text

    def get_pin_id(self, pin_id, fields=[]):
        """
        查询指定ID的pin信息
        :param pin_id:
        :param fields:
        :return:
        """
        if not fields:
            fields = self.get_pin_id_fields
        str_fields = "%2".join(fields)
        api_request_url = f"{self.pinterest_host}/pins/{pin_id}/?access_token={self.access_token}&fields={str_fields}"
        new_pin = requests.get(api_request_url)
        return new_pin.status_code, new_pin.text

    def get_user_suggested(self, count, fields=[]):
        """
        :param count:
        :param fields:
        :return:
        """
        if not fields:
            fields = self.get_user_suggested_fields
        str_fields = "%2".join(fields)
        url = "{}/me/boards/suggested/?" \
              "count={}&access_token={}&fields={}".format(self.pinterest_host, count, self.access_token, str_fields)
        user_suggested = requests.get(url)
        return user_suggested.status_code, user_suggested.text


if __name__ == '__main__':
    access_token = "AtsPh53aHL__3xdZbsGmJon87XsrFZ1-0tDJSSBF0n-lswCyYAp2ADAAAk1KRdOSuUEgxv0AAAAA"
    all_pinterest_api = All_Pinterest_Api(access_token=access_token)
    # all_pinterest_api.get_code()
    # all_pinterest_api.get_token(code="1ced3e0fcf90f53d")
    # all_pinterest_api.get_user_boards()
    # all_pinterest_api.create_board(name="xiaowawa", description=u"时间可以将最好的产物输出")
    # all_pinterest_api.delete_board(board_id="753790125070473979")
    all_pinterest_api.get_board_id(board_id="753790125070473940")



