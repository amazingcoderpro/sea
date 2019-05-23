import requests
from urllib import parse


class ShopifyBase():
    """
    shopify授权的api
    """
    def __init__(self, shop_name, client_id):
        self.shop_name = shop_name
        self.client_id = client_id

    def ask_permission(self, nonce, redirect_uri, scopes=[]):
        """
        获取授权页面
        :param nonce: 标注
        :param redirect_uri: callback url
        :param scopes: 权限
        :return: status_code, text
        """
        redirect_uri = parse.quote(redirect_uri)
        permission_url = f"https://{self.shop_name}.myshopify.com/admin/oauth/authorize" \
                         f"?client_id={self.client_id}" \
                         f"&scope={scopes}" \
                         f"&redirect_uri={redirect_uri}" \
                         f"&state={nonce}&grant_options[]="
        get_permission_code = requests.get(permission_url)
        return get_permission_code.status_code

    def confirm_installation(self, authorization_code, hmac, timestamp, nonce, shop):
        """
         # 获取授权码的code
        :param authorization_code:
        :param hmac:
        :param timestamp:
        :param nonce:
        :param shop:
        :return: status_code, text
        """
        url = "https://example.org/some/redirect/uri?" \
              f"code={authorization_code}" \
              f"&hmac={hmac}" \
              f"&timestamp={timestamp}" \
              f"&state={nonce}" \
              f"&shop={self.shop_name}"
        installation_code = requests.get(url)
        return installation_code.status_code, installation_code.text

    def get_token(self, client_secret, code):
        """
        获取shopify的永久性token
        :param client_secret:
        :param code:
        :return:
        """
        display = {
            "client_id": self.client_id,
            "client_secret": client_secret,
            "code": code
        }
        url = f"https://{self.shop_name}.myshopify.com/admin/oauth/access_token"
        get_access_token = requests.post(url, display)
        print(get_access_token.status_code, get_access_token.text)


if __name__ == '__main__':
    ShopifyBase = ShopifyBase()
    # ShopifyBase.reRequest(shop="ordersea", method="get", url="", headers=None, data=None)
    ShopifyBase.ask_permission()
    # ShopifyBase.confirm_installation()
    # ShopifyBase.get_token(shop="ordersea")









