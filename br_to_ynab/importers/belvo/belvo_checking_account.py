import re
from typing import Iterable
import requests

from importers.data_importer import DataImporter
from importers.transaction import Transaction
from importers.util import deep_get

class BelvoCheckingAccountData(DataImporter):

    def __init__(self, account_id: str, belvo_auth: str, belvo_link: str, belvo_account: str, start_import_date: str):
        self.account_id = account_id
        self.belvo_auth = belvo_auth
        self.belvo_link = belvo_link
        self.belvo_account = belvo_account
        self.start_import_date = start_import_date

    def get_data(self):
        url = "https://development.belvo.com/api/transactions/?page=1&page_size=1000&value_date__gte=" + self.start_import_date + "&link=" + self.belvo_link + "&account=" + self.belvo_account + "&fields=id,amount,description,observations,value_date,type"
        payload = {}
        headers = {
            'Authorization': self.belvo_auth
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        transactions = response.json()['results']

        return map(self._account_data_to_transaction, transactions)

    def _account_data_to_transaction(self, account_transaction: dict) -> Transaction:
        
        return {
            'transaction_id': account_transaction['id'],
            'account_id': self.account_id,
            'amount': self._get_transaction_amount(account_transaction),
            'payee': self._get_payee_from_acct_transaction(account_transaction),
            'date': account_transaction['value_date'],
            'memo': self._get_payee_from_acct_transaction(account_transaction)
        }

    def _get_transaction_amount(self, account_transaction: dict) -> int:
        amount = int(account_transaction['amount'] * 1000)
        if account_transaction['type'] != 'INFLOW':
            amount *= -1
        return amount

    def _get_payee_from_acct_transaction(self, account_transaction: dict) -> str:
        # TODO implementar devolucao pix?

        if account_transaction['description'] == 'Pagamento da fatura':
            payee = 'Nubank'
        elif account_transaction['description'] == 'Compra no débito':
            payee = re.sub(r'^Compra no débito ', '', account_transaction['observations'])
            payee, detail = payee.split(u'\n')
        else:
            try:
                payee, detail = account_transaction['observations'].split(u'\n')
            except ValueError as e:
                payee = account_transaction['observations']
            
        return payee