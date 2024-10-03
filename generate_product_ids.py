#! /bin/python3
import requests
from bs4 import BeautifulSoup
from random import choice
import configparser

config = configparser.ConfigParser()
config.read("conf.ini")
host = "https://" + config["odoo"]["url"] + '/'

with open('products.txt', 'wt') as p:
    for i in range(1,100):
        print(i)
        with requests.get(f"{host}/shop/page/{i}?") as resp:
            print("resp")
            soup = BeautifulSoup(resp.text, 'lxml')
            links = []
            for link in soup.select("a[itemprop]"):
                if 'oe_product_image_link' in link['class']:
                    links.append(link['href'])
            link = choice(links)
            with requests.get(f"{host}{link}") as p_det:
                soup_det = BeautifulSoup(p_det.text, 'lxml')
                product_id = int(soup_det.select_one("input[name='product_id']")['value'])
                product_template_id = int(soup_det.select_one("input[name='product_template_id']")['value'])
                p.write(f"{i} {product_id} {product_template_id} {link} \n")
