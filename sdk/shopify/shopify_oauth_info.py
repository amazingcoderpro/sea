import requests
from urllib import parse
import json
from config import logger


class ShopifyBase():
    """
    shopify授权的api
    """
    def __init__(self, shop_name):
        self.shop_name = shop_name
        self.client_id = "f9cd4d9b7362ae81038635518edfd98f"
        self.client_secret = "a7159ff763aadb8f6c047563dbbe73e1"
        self.redirect_uri = "https://pinbooster.seamarketings.com/api/v1/shopify/callback/"
        self.scopes = ["read_content", "write_content", "read_themes", "write_themes", "read_products", "write_products",
                       "read_product_listings", "read_customers", "write_customers", "read_orders", "write_orders", "read_shipping",
                       "write_draft_orders", "read_inventory", "write_inventory","read_shopify_payments_payouts", "read_draft_orders",
                       "read_locations", "read_script_tags", "write_script_tags", "read_fulfillments", "write_fulfillments",
                       "write_shipping", "read_analytics", "read_checkouts", "write_resource_feedbacks","write_checkouts",
                       "read_reports", "write_reports", "read_price_rules", "write_price_rules", "read_marketing_events",
                       "write_marketing_events", "read_resource_feedbacks", "read_shopify_payments_disputes"]

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
            result = requests.post(url, display)
            if result.status_code == 200:
                logger.info("get shopify token is successed, shopname={}".format(self.shop_name))
                return {"code": 1, "msg": "", "data": json.loads(result.text)["access_token"]}
            else:
                logger.error("get shopify token is failed, shopname={}".format(self.shop_name))
                return {"code": 2, "msg": "", "data": ""}
        except Exception as e:
            logger.error("get shopify token is failed".format(e))
            return {"code": 2, "msg": "", "data": ""}


if __name__ == '__main__':
    ShopifyBase = ShopifyBase(shop_name="ordersea")
    # ShopifyBase.reRequest(shop="ordersea", method="get", url="", headers=None, data=None)
    ShopifyBase.ask_permission(nonce="ordersea")
    ShopifyBase.get_token(code="23333584")
    # ShopifyBase.confirm_installation()
    # ShopifyBase.get_token(shop="ordersea")










