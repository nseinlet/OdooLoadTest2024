# OdooLoadTest2024

Code used for Odoo Experience 2024 about load testing

to launch the load test:
```
lt.sh lt_ebusiness.py 8 2000 60 0 50
```

This will launch Locust Web UI, on port 8089, with 8 local workers, 2000 simulated users, for 60 minutes, and add new users at the rythm of 50/s


## conf.ini

```
[odoo]
url=myserver.company.local
db=my_loadtest_db
user=admin
pass=admin
[weight]
saleman=10
webshop=200
[frontend]
min_sleep=5
max_sleep=20
```