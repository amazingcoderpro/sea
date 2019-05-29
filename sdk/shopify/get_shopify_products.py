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

    def get_all_products(self):
        """
        获取所有商品的信息
        :return:
        """
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all prodects is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all prodects is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all prodects is failed info={}".format(str(e)))
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
                print(result_info)
                logger.info("get shopify all order by id is success")
                return {"code": 1, "msg": "", "data": result_info}
            else:
                logger.info("get shopify all order by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all order by id is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}


if __name__ == '__main__':
    client_id = "f9cd4d9b7362ae81038635518edfd98f"
    access_token = "fa7fadd554e238cc6aafc0f15b9553f9"
    shop = "ordersea.myshopify.com"
    scopes = "write_orders,read_customers"
    callback_uri = "http://www.orderplus.com/index.html"
    id = "3583116148816"
    shop_uri = "arealook.myshopify.com"
    products_api = ProductsApi(access_token=access_token, shop_uri=shop_uri)
    # products_api.get_all_products()
    products_api.get_order(create_start_time="2019-05-22T0:0:0-04:00", create_end_time="2019-05-28T0:0:0-04:00", key_word="google", financial_status="paid")
    # products_api.get_shop_info()
    # products_api.get_product_id()
