import requests


class products_api():

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
        shop_info = requests.get(shop_url)
        print(shop_info.status_code, shop_info.text)
        return shop_info.status_code, shop_info.text

    def get_all_products(self):
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop}{self.version_url}products.json"
        all_products_info = requests.get(products_url)
        print(all_products_info.status_code, all_products_info.text)
        return all_products_info.status_code, all_products_info.text

    def get_product_id(self):
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop}{self.version_url}products/{self.id}.json"
        if self.id == None:
            return None
        products_id_info = requests.get(products_url)
        print(products_id_info.status_code, products_id_info.text)
        return products_id_info.status_code, products_id_info.text


if __name__ == '__main__':
    client_id = "f9cd4d9b7362ae81038635518edfd98f"
    access_token = "0e4143eb45f2519b6b40a57a2834acd0"
    shop = "ordersea.myshopify.com"
    scopes = "write_orders,read_customers"
    callback_uri = "http://www.orderplus.com/index.html"
    id = "3583116148816"
    products_api = products_api(client_id, access_token, shop, scopes, callback_uri)
    products_api.get_all_products()
    products_api.get_shop_info()
    products_api.get_product_id()
