#!/bin/python3
import random
import configparser
import logging

from locust import task, between, run_single_user
from OdooLocust import OdooLocustUser, crm, OdooTaskSet
from lt_webshop import WebShop

config = configparser.ConfigParser()
config.read("conf.ini")
_logger = logging.getLogger()


class Delivering(crm.quotation.SaleOrder):

    def _fields_view_get(self, model, view_mode):
        return ['id', 'name', 'state', 'partner_id']

    @task(5)
    def confirm_quotation(self):
        found = False
        retry=0
        while (not found and retry<5):
            retry += 1
            search_domain = [['state', '=', 'draft']]
            other_domain =  self._get_search_domain()
            if other_domain:
                search_domain = ['&'] + search_domain + other_domain
            
            nbr_records = self.model.search_count(search_domain)
            offset = random.randint(0, nbr_records % 80) if nbr_records > 80 else 0

            ids = self.model.search(search_domain, limit=80, offset=offset)
            if ids:
                found = True
                self.random_id = random.choice(ids)
                self.model.action_confirm(self.random_id)

    @task(5)
    def deliver_saleorder(self):
        found = False
        retry=0
        while (not found and retry<5):
            retry += 1
            domain = [[ "state", "not in", [ "draft", "sent", "cancel" ]], ['company_id', '=', 1]]
            ids = self.model.search(domain, limit=80)
            if ids:
                found = True
                self.random_id = random.choice(ids)
                saleorderline_model = self.client.get_model('sale.order.line')
                sol_ids = saleorderline_model.search_read([ ['order_id', '=', self.random_id] ], ['id', 'product_uom_qty'])
                for sol in sol_ids:
                    saleorderline_model.write(sol['id'], {'qty_delivered': sol['product_uom_qty']})
                payment_ctx = {
                    "active_model": "sale.order",
                    "active_ids": [self.random_id],
                    "active_id": self.random_id,
                }
                pay_model = self.client.get_model('sale.advance.payment.inv')
                payment_id = pay_model.create({'advance_payment_method': 'delivered'}, context=payment_ctx)
                res = pay_model.create_invoices(payment_id)
                invoice_id = res['res_id']
                invoice_model = self.client.get_model('account.move')
                invoice_model.action_post(invoice_id)


class InvoicePayment(OdooTaskSet.OdooGenericTaskSet):
    model_name='account.move'

    def _fields_view_get(self, model, view_mode):
        return ['id', 'name', 'res', 'state', 'date']

    @task(5)
    def register_payment(self):
        domain = [["move_type", "=", "out_invoice"], ['payment_state', '=', 'not_paid']]
        nbr_records = self.model.search_count(domain)
        offset = random.randint(0, nbr_records % 80) if nbr_records > 80 else 0
        inv_ids = self.model.search(domain, offset=offset, limit=80)
        if inv_ids:
            self.random_id = random.choice(inv_ids)
            res = self.model.action_register_payment(self.random_id)
            pay_model_name = res['res_model']
            pay_ctx = res['context']
            pay_model = self.client.get_model(pay_model_name)
            pay_id = pay_model.create({}, context=pay_ctx)
            pay_model.action_create_payments(pay_id)

                
class BackendSalesMen(OdooLocustUser.OdooLocustUser):
    weight = int(config["weight"].get('saleman', 1))
    wait_time = between(0.1, 1)
    database = config["odoo"]["db"]
    host = config["odoo"]["url"]
    login = "invalid"
    password = "invalid"
    port = 443
    protocol = "jsonrpcs"
    _user_list = []

    def __init__(self, *args, **kwargs):
        self._fill_users_from_usr_file()
        return super().__init__(*args, **kwargs)
    
    def _fill_users_from_usr_file(self):
        with open('usr.txt') as usr_file:
            for line in usr_file.readlines():
                self._user_list.append(line.strip('\n').split(':'))

    def on_start(self):
        usr = random.choice(self._user_list)
        self.login = usr[0]
        self.password = usr[1]
        _logger.info(f"Load testing with user {self.login}")
        return super().on_start()

    tasks = {
        crm.partner.ResPartner: 1,
        crm.lead.CrmLead: 2,
        Delivering: 4,
        InvoicePayment:1,
    }

if __name__ == "__main__":
    run_single_user(BackendSalesMen)
