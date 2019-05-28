import requests
from urllib import parse
import json
from config import logger
from config import SHOPIFY_CONFIG


class ShopifyBase():
    """
    shopify授权的api
    """
    def __init__(self, shop_name):
        """
        :param code: 1 状态正确， 2 状态错误， -1 出现异常
        :param shop_name: 店铺名称
        """
        self.shop_name = shop_name
        self.client_id = SHOPIFY_CONFIG.get("client_id")
        self.client_secret = SHOPIFY_CONFIG.get("client_secret")
        self.redirect_uri = SHOPIFY_CONFIG.get("redirect_uri")
        self.scopes = SHOPIFY_CONFIG.get("scopes")
        self.headers = {'Content-Type': 'application/json'}

    def ask_permission(self, nonce):
        """
        获取授权页面
        :param nonce: 标注
        :param redirect_uri: callback url
        :param scopes: 权限
        :return: status_code, text
        """
        redirect_uri = parse.quote(self.redirect_uri)
        scopes_info = ",".join(self.scopes)
        permission_url = f"https://{self.shop_name}.myshopify.com/admin/oauth/authorize" \
                         f"?client_id={self.client_id}" \
                         f"&scope={scopes_info}" \
                         f"&redirect_uri={redirect_uri}" \
                         f"&state={nonce}&grant_options[]="
        return permission_url

    def get_token(self, code):
        """
        获取shopify的永久性token
        :param client_secret:
        :param code:
        :return:
        """
        display = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        url = f"https://{self.shop_name}.myshopify.com/admin/oauth/access_token"
        try:
            result = requests.post(url, display, headers=self.headers)
            # print(result.status_code)
            if result.status_code == 200:
                logger.info("get shopify token is successed, shopname={}".format(self.shop_name))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("access_token")}
            else:
                logger.err("get shopify token is successed, shopname={}".format(self.shop_name))
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify token is failed".format(e))
            return {"code": -1, "msg": str(e), "data": ""}


if __name__ == '__main__':
    ShopifyBase = ShopifyBase(shop_name="ordersea")
    # ShopifyBase.reRequest(shop="ordersea", method="get", url="", headers=None, data=None)
    # ShopifyBase.ask_permission(nonce="ordersea")

    ShopifyBase.get_token(code="ec370ccb56986acb1a76db0e3fecd798")
