# -*-coding:utf-8-*-
import requests
from config import logger
import json
from config import SHOPIFY_CONFIG


class ProductsApi:
    def __init__(self, access_token, shop_uri):
        """
        :param client_id: api key
        :param access_token: api password
        :param shop_URI: 店铺uri
        :param scopes: 权限
        :param callback_uri: callback url
        :param code: 1 状态正确， 2 状态错误， -1 出现异常
        """
        self.client_id = SHOPIFY_CONFIG.get("client_id")
        self.access_token = access_token
        self.shop_uri = shop_uri
        self.scopes = SHOPIFY_CONFIG.get("scopes")
        self.callback_uri = SHOPIFY_CONFIG.get("callback_uri")
        self.version_url = "/admin/api/2019-04/"
        self.headers = {'Content-Type': 'application/json'}

    def get_custom_collections(self):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}smart_collections.json?limit=250"
        try:
            result = requests.get(shop_url)
            if result.status_code == 200:
                logger.info("get shopify info is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_shop_info(self):
        """
        获取用户信息
        :return:
        """
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}shop.json"
        try:
            result = requests.get(shop_url)
            if result.status_code == 200:
                logger.info("get shopify info is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_all_products(self, limit=250, since_id=""):
        """
        获取所有商品的信息
        :return:
        """
        if not since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?limit={limit}"
        if since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?limit={limit}&since_id={since_id}"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all products is success")
                # print(result.text)
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all products is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all products is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_product_id(self, id):
        """
        通过 id 获取商品的信息
        :param id: 商品id
        :return:
        """
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/{id}.json"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all prodects by id is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all prodects by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all prodects by id is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_order(self, create_start_time, create_end_time, key_word, financial_status="paid"):
        """
         获取订单
        :param create_start_time: 创建订单之前的时间
        :param create_end_time: 创建订单之后的时间
        :param key_word:  搜索关键字
        :param financial_status: 订单状态
             pending：付款待定。在这种状态下付款可能会失败。再次检查以确认付款是否已成功支付。
             authorized：付款已获得授权。
             partially_paid：订单已部分支付。
             paid：付款已付款。
             partial_refunded：付款已部分退还。
             refunded：付款已退款。
             voided：付款已无效
        :return:
        """
        order_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}orders.json" \
            f"?created_at_min={create_start_time}&created_at_max={create_end_time}&financial_status={financial_status}"
        try:
            result = requests.get(order_url)
            if result.status_code == 200:
                order_list = json.loads(result.text).get("orders", "")
                order_count = 0
                total_price = 0
                for order_info in order_list:
                    referring_site = str(order_info.get("referring_site"))
                    if str(key_word) in referring_site:
                        order_count += 1
                        order_price = float(order_info.get("total_price"))
                        total_price += order_price
                result_info = {"order_count": order_count, "total_price": round(total_price, 4)}
                # print(result_info)
                logger.info("get shopify all order by id is success")
                return {"code": 1, "msg": "", "data": result_info}
            else:
                logger.info("get shopify all order by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all order by id is failed; info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_all_collections(self):
        """
        获取collections_id的product
        # 接口  /admin/api/#{api_version}/products.json?collection_id=841564295
        # 连接地址 https://help.shopify.com/en/api/reference/products/product
        :return:
        """
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}custom_collections.json"
        shop_url2 = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}smart_collections.json"
        try:
            result = requests.get(shop_url)
            result2 = requests.get(shop_url2)

            if result.status_code and result2.status_code in [200, 201]:
                logger.info("get shopify all collections info is success")
                res_dict = json.loads(result.text)
                res_dict.update(json.loads(result2.text))
                print(res_dict)
                return {"code": 1, "msg": "", "data": res_dict}
            else:
                logger.info("get shopify all collections info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all collections info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    @classmethod
    def parse_collections(cls, data):
        all_collections = []
        for col in data["custom_collections"] + data["smart_collections"]:
            if "home" in col.get("title", "").lower():
                continue
            all_collections.append(
                {
                    "uuid": col.get("id", ""),
                    "meta_title": col.get("title", ""),
                    "address": "/collections/" + col.get("title", "").lower().replace("'", "").replace(" ", "-"),
                    "meta_description": col.get("body_html", ""),
                }
            )
        return all_collections

    def get_collections_products(self, collection_id, limit=250, since_id=""):
        """
        获取collections_id的product
        # 接口  /admin/api/2019-04/smart_collections.json
                /admin/api/2019-04/custom_collections.json
        # 连接地址 https://help.shopify.com/en/api/reference/products/product
        :return:
        """
        if not since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?collection_id={collection_id}&limit={limit}"
        if since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?collection_id={collection_id}&limit={limit}&since_id={since_id}"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all products is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all products is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all products is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}


if __name__ == '__main__':
    client_id = "7fced15ff9d1a461f10979c3eae2eca8"
    access_token = "b5e11d595f09d8e99ddb956f72eb8c84"
    shop = "ordersea.myshopify.com"
    scopes = "write_orders,read_customers"
    callback_uri = "http://www.orderplus.com/index.html"
    id = "3583116148816"
    shop_uri = "tiptopfree.myshopify.com"
    products_api = ProductsApi(access_token=access_token, shop_uri=shop_uri)
    # 获取所有的类目接口
    products_api.get_all_collections()
    # 获取cellection-id 的所有的产品接口
    products_api.get_collections_products(collection_id="80777805869", limit="250")

    # products_api.get_custom_collections()
    # products_api.get_all_products(limit="250", since_id="1833170796589")
    # products_api.get_order(create_start_time="2019-05-22T0:0:0-04:00", create_end_time="2019-05-28T0:0:0-04:00", key_word="google", financial_status="paid")
    # products_api.get_shop_info()
    # products_api.get_product_id()
