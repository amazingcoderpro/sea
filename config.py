#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-05-13
# Function: 

import logging
from log_config import log_config

log_config.init_log_config("logs", "sea")
logger = logging.getLogger()

SHOPIFY_CONFIG = {
    "client_id": "f9cd4d9b7362ae81038635518edfd98f",#ordersea
    "client_secret": "a7159ff763aadb8f6c047563dbbe73e1",
    # "client_id": "7fced15ff9d1a461f10979c3eae2eca8",  # pinbooster
    # "client_secret": "461a69b7c8c13a37416d79769175ce23",
    "redirect_uri": "https://pinbooster.seamarketings.com/api/v1/auth/shopify/callback/",
    "scopes": ["read_content", "write_content", "read_themes", "write_themes", "read_products",
               "write_products", "read_product_listings", "read_customers", "write_customers",
               "read_orders", "write_orders", "read_shipping", "write_draft_orders", "read_inventory",
               "write_inventory", "read_shopify_payments_payouts", "read_draft_orders", "read_locations",
               "read_script_tags", "write_script_tags", "read_fulfillments", "write_shipping", "read_analytics",
               "read_checkouts", "write_resource_feedbacks", "write_checkouts", "read_reports", "write_reports",
               "read_price_rules", "write_price_rules", "read_marketing_events", "write_marketing_events",
               "read_resource_feedbacks", "read_shopify_payments_disputes", "write_fulfillments"],
    "utm_format":"?utm_source=pinbooster&utm_medium={pinterest_account}&utm_campaign={board_name}&utm_keyword={product_id}"
}


PINTEREST_CONFIG = {
    "client_id": "5033349102128117330",
    "client_secret": "7578af0b0a9102815d71c822813e717b23362b0725e44e245e4296669124fe98",
    "scope": "read_public,write_public,read_relationships,write_relationships",
    "redirect_uri": "https://pinbooster.seamarketings.com/api/v1/auth/pinterest/callback/"
}

GA_CONFIG = {
    'google_developer': "test123@eternal-argon-241002.iam.gserviceaccount.com"
}