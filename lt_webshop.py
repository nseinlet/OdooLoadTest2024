#!/bin/python3
import names
import urllib.parse
import configparser

from bs4 import BeautifulSoup
from time import sleep
from random import randint, choice

from locust import task, run_single_user
from locust import FastHttpUser


config = configparser.ConfigParser()
config.read("conf.ini")

min_sleep = int(float(config['frontend']['min_sleep'] or 1) * 1000)
max_sleep = int(float(config['frontend']['max_sleep'] or 1) * 1000)
min_sleep = 1
max_sleep = 1

class WebShop(FastHttpUser):
    weight = int(config["weight"].get('webshop', 10))
    host = "https://" + config["odoo"]["url"] + '/'
    default_headers = {
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    def __init__(self, *args, **kwargs):
        with open('products.txt', 'r') as f:
            self.products = {int(p.split(' ')[0]): p.split(' ')[3] for p in f.readlines()}
        with open('products.txt', 'r') as f:
            self.products_ids = {int(p.split(' ')[0]): p.split(' ')[1] for p in f.readlines()}
        with open('products.txt', 'r') as f:
            self.products_template_ids = {int(p.split(' ')[0]): p.split(' ')[2] for p in f.readlines()}
        return super().__init__(*args, **kwargs)

    @task
    def t(self):
        self.client.client.clientpool.close()
        self.client.cookiejar.clear()
        product = {
            'url': '',
            'template_id': -1,
            'id': 1,
        }
        order_id = False
        csrf_token = False
        access_token = False
        user_speed = randint(min_sleep, max_sleep) / 1000.0

        with self.client.request(
            "GET",
            "/shop",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        sleep(user_speed)

        random_page = randint(1, 100)
        product['url'] = self.products[random_page]
        product['id'] = int(self.products_ids[random_page])
        product['template_id'] = int(self.products_template_ids[random_page])
        with self.client.request(
            "GET",
            f"/shop/page/{random_page}",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        sleep(user_speed)

        with self.client.request(
            "GET",
            product['url'],
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}shop",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        sleep(user_speed)

        for i in range(0, randint(0,6)):
            with self.rest(
                "POST",
                "/website_sale/get_combination_info",
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "origin": f"{self.host}",
                    "priority": "u=1, i",
                    "referer": f"{self.host}{product['url']}",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                },
                json={
                    "id": 0,
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "product_template_id": product['template_id'],
                        "product_id": product['id'],
                        "combination": [12859, 12876, 12864, 12871],
                        "add_qty": 1,
                        "parent_combination": [],
                    },
                },
            ) as resp:
                pass
            sleep(user_speed)

        with self.rest(
            "POST",
            "/shop/cart/update_json",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "origin": f"{self.host}",
                "priority": "u=1, i",
                "referer": f"{self.host}{product['url']}",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            json={
                "id": 10,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "product_id": product['id'],
                    "product_template_id": product['template_id'],
                    "product_custom_attribute_values": "[]",
                    #"variant_values": [12862, 12876, 12864, 12874],
                    #"no_variant_attribute_values": '[{"custom_product_template_attribute_value_id":12864,"attribute_value_name":"PAV_9542","value":"12864","attribute_name":"PA_73"}]',
                    "add_qty": 1,
                    "display": False,
                    "force_create": True,
                },
            },
        ) as resp:
            pass
        sleep(user_speed)

        with self.client.request(
            "GET",
            "/shop/cart",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}{product['url']}",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            order_id = soup.select_one("sup[data-order-id]")["data-order-id"]
            
        sleep(user_speed)

        with self.client.request(
            "GET",
            "/shop/checkout?express=1",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/cart",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        sleep(user_speed)

        with self.client.request(
            "GET",
            "/shop/address",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/cart",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            csrf_token = soup.select_one("input[name='csrf_token']")["value"]

        with self.rest(
            "POST",
            "/shop/country_info/20",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "origin": f"{self.host}",
                "priority": "u=1, i",
                "referer": f"{self.host}shop/address",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            json={
                "id": 0,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {"address_type": "billing"},
            },
        ) as resp:
            pass
        sleep(user_speed)

        first_name = urllib.parse.quote_plus(names.get_first_name())
        last_name = urllib.parse.quote_plus(names.get_last_name())
        name = urllib.parse.quote_plus(names.get_full_name())
        company_name = urllib.parse.quote_plus(names.get_full_name())

        with self.client.request(
            "POST",
            "/shop/address/submit",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "origin": f"{self.host}",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/address",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            data=f"name={name}&email={first_name}%40{last_name}.local&phone=gfdgsfdgs&company_name={company_name}&vat=&street=gsdggfgfgfsd&street2=gffgfgfds&zip=gfdsgff&city=gfdsdgfs&country_id=20&state_id=&use_same=1&csrf_token={csrf_token}&submitted=1&partner_id=-1&mode=billing&callback=&field_required=name%2Cstreet",
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/shop/confirm_order",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/address",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/shop/payment",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/address",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            access_token = soup.select_one("form[data-access-token]")["data-access-token"]
        sleep(user_speed)

        with self.rest(
            "POST",
            f"/shop/payment/transaction/{order_id}",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "origin": f"{self.host}",
                "priority": "u=1, i",
                "referer": f"{self.host}shop/payment",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            json={
                "id": 3,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "provider_id": 15,
                    "payment_method_id": 199,
                    "token_id": None,
                    "amount": None,
                    "flow": "redirect",
                    "tokenization_requested": False,
                    "landing_route": "/shop/payment/validate",
                    "is_validation": False,
                    "access_token": access_token,
                    "csrf_token": csrf_token,
                },
            },
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "/payment/status",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "referer": f"{self.host}shop/payment",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.rest(
            "POST",
            "/payment/status/poll",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "origin": f"{self.host}",
                "priority": "u=1, i",
                "referer": f"{self.host}payment/status",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            json={
                "id": 0,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "csrf_token": csrf_token
                },
            },
        ) as resp:
            pass
        sleep(user_speed)

        with self.client.request(
            "GET",
            "/shop/payment/validate",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}payment/status",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        sleep(user_speed)
        
        with self.client.request(
            "GET",
            "/shop/confirmation",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "priority": "u=0, i",
                "referer": f"{self.host}payment/status",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass


if __name__ == "__main__":
    run_single_user(WebShop)
