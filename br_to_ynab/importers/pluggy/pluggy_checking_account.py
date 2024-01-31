import re
from typing import Iterable
import requests

from importers.data_importer import DataImporter
from importers.transaction import Transaction
from importers.util import deep_get

class PluggyCheckingAccountData(DataImporter):

    def __init__(self, account_id: str, pluggy_client_id: str, pluggy_client_secret: str, pluggy_item_id: str, pluggy_account: str, start_import_date: str):
        self.account_id = account_id
        self.pluggy_client_id = pluggy_client_id
        self.pluggy_client_secret = pluggy_client_secret
        self.pluggy_item_id = pluggy_item_id
        self.pluggy_account = pluggy_account
        self.start_import_date = start_import_date
        self.pluggy_auth = ""

    def get_data(self):
        # Get an api key from pluggy
        url = "https://api.pluggy.ai/auth"
        payload = "clientId=" + self.pluggy_client_id + "&clientSecret=" + self.pluggy_client_secret
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        self.pluggy_auth = response.json()['apiKey']

        # Get transactions
        url = "https://api.pluggy.ai/transactions/?page=1&page_size=500&from=" + self.start_import_date +  "&accountId=" + self.pluggy_account
        payload = {}
        headers = {
            'X-API-KEY': self.pluggy_auth
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        transactions = response.json()['results']

        return map(self._account_data_to_transaction, transactions)

    def _account_data_to_transaction(self, account_transaction: dict) -> Transaction:
        
        data_to_test = {
            'transaction_id': account_transaction['id'],
            'account_id': self.account_id,
            'amount': self._get_transaction_amount(account_transaction),
            'payee': self._get_payee_from_acct_transaction(account_transaction),
            'date': account_transaction['date'][0:10],
            'memo': self._get_payee_from_acct_transaction(account_transaction)
        }
        print(data_to_test)
        return data_to_test

    def _get_transaction_amount(self, account_transaction: dict) -> int:
        if account_transaction['amountInAccountCurrency'] is not None:
            amount = int(account_transaction['amountInAccountCurrency'] * 1000)
        else:
            amount = int(account_transaction['amount'] * 1000) 

        return amount

    def _get_payee_from_acct_transaction(self, account_transaction: dict) -> str:

        if account_transaction['description'] == 'Pagamento de fatura':
            payee = 'Nubank'
        elif account_transaction['description'] == 'Transferência Pix':
            if account_transaction['type'] == 'DEBIT':
                if account_transaction['paymentData']['receiver']['name']:
                    payee = account_transaction['paymentData']['receiver']['name']
                else:
                    payee = "PIX-" + account_transaction['paymentData']['receiver']['documentNumber']['type'] + "_" + account_transaction['paymentData']['receiver']['documentNumber']['value']
            else:
                if account_transaction['paymentData']['payer']['name']:
                    payee = account_transaction['paymentData']['payer']['name']
                else:
                    payee = "PIX-" + account_transaction['paymentData']['payer']['documentNumber']['type'] + "_" + account_transaction['paymentData']['payer']['documentNumber']['value']
        else:
            payee = account_transaction['description']
        # TODO detail = account_transaction['observations'].split(u'\n') quando tiver esse recurso no pluggy
            
        return payee