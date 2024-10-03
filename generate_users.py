#! /bin/python3
import odoolib
import configparser
import random
import uuid
import hashlib

config = configparser.ConfigParser()
config.read("conf.ini")

connection = odoolib.get_connection(
    hostname=config["odoo"]["url"],
    database=config["odoo"]["db"],
    login=config["odoo"]["user"],
    password=config["odoo"]["pass"],
    port=443,
    protocol="jsonrpcs",
)
company_model = connection.get_model('res.company')
user_model = connection.get_model('res.users')
key_model = connection.get_model('res.users.apikeys')


# clean old api keys
key_ids = key_model.search([('user_id', '>', 10)])
if key_ids:
    key_model.unlink(key_ids)

# Set random user passwords
with open('usr.txt', 'w') as lst:
    for i in range(0, 1000):
        name = f"user_{i}"
        pwd = hashlib.md5(('%s/%s' % (uuid.uuid4(), random.randint(0, 2^32))).encode('UTF-8') ).hexdigest()
        user_id = user_model.create( {' login' : name, 'name': name, 'password': pwd})
        lst.write('%s:%s\n' % (name, pwd))
