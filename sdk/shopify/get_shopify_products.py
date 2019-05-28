import requests
from config import logger
import json


class ProductsApi:
    def __init__(self, client_id, access_token, shop, scopes, callback_uri):
        """
        :param client_id: api key
        :param access_token: api password
        :param shop: 店铺名称
        :param scopes: 权限
        :param callback_uri: callback url
        """
        self.client_id = client_id
        self.access_token = access_token
        self.shop = shop
        self.scopes = scopes
        self.callback_uri = callback_uri
        self.id = id
        self.version_url = "/admin/api/2019-04/"

    def get_shop_info(self):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop}{self.version_url}shop.json"
        try:
            result = requests.get(shop_url)
            if result.status_code == 200:
                logger.info("get shopify info is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify info is failed")
                return {"code": 1, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify info is failed info={}".format(e))
            return {"code": 2, "msg": e, "data": ""}

    def get_all_products(self):
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop}{self.version_url}products.json"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all prodects is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all prodects is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all prodects is failed info={}".format(e))
            return {"code": 2, "msg": e, "data": ""}

    def get_product_id(self):
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop}{self.version_url}products/{self.id}.json"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all prodects by id is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all prodects by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all prodects by id is failed info={}".format(e))
            return {"code": 2, "msg": e, "data": ""}


if __name__ == '__main__':
    client_id = "f9cd4d9b7362ae81038635518edfd98f"
    access_token = "0e4143eb45f2519b6b40a57a2834acd0"
    shop = "ordersea.myshopify.com"
    scopes = "write_orders,read_customers"
    callback_uri = "http://www.orderplus.com/index.html"
    id = "3583116148816"
    products_api = ProductsApi(client_id, access_token, shop, scopes, callback_uri)
    # products_api.get_all_products()
    products_api.get_shop_info()
    # products_api.get_product_id()
