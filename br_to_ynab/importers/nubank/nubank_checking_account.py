import re
from pynubank import Nubank

from importers.data_importer import DataImporter
from importers.transaction import Transaction
from importers.util import deep_get

class NubankCheckingAccountData(DataImporter):

    def __init__(self, nubank: Nubank, account_id: str):
        self.nu = nubank
        self.account_id = account_id

    def get_data(self):
        transactions = self.nu.get_account_feed_paginated()['edges']

        return map(self._account_data_to_transaction, transactions)

    def _account_data_to_transaction(self, account_transaction: dict) -> Transaction:
        account_transaction = account_transaction['node']
        
        return {
            'transaction_id': account_transaction['id'],
            'account_id': self.account_id,
            'amount': self._get_transaction_amount(account_transaction),
            'payee': self._get_payee_from_acct_transaction(account_transaction),
            'date': account_transaction['postDate'],
            'memo': self._get_payee_from_acct_transaction(account_transaction)
        }

    def _get_transaction_amount(self, account_transaction: dict) -> int:
        amount = int(account_transaction['amount'] * 1000)
        if account_transaction['kind'] != 'POSITIVE':
            amount *= -1
        return amount

    def _get_payee_from_acct_transaction(self, account_transaction: dict) -> str:
        # TODO implementar devolucao pix?

        if account_transaction['title'] == 'Pagamento da fatura':
            payee = 'Nubank'
        elif account_transaction['title'] == 'Compra no débito':
            payee = re.sub(r'^Compra no débito ', '', account_transaction['detail'])
            payee, detail = payee.split(u'\n')
        else:
            try:
                payee, detail = account_transaction['detail'].split(u'\n')
            except ValueError as e:
                payee = account_transaction['detail']
            
        return payee