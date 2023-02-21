import re
from pynubank import Nubank

from importers.data_importer import DataImporter
from importers.transaction import Transaction
from importers.util import deep_get

OUTFLOW_EVENT_TYPES = (
    'TransferOutEvent',
    'PixTransferOutEvent',
    'TransferOutReversalEvent',
    'BarcodePaymentEvent',
    'DebitPurchaseEvent',
    'DebitPurchaseReversalEvent',
    'BillPaymentEvent',
    'DebitWithdrawalFeeEvent',
    'DebitWithdrawalEvent',
)


class NubankCheckingAccountData(DataImporter):

    def __init__(self, nubank: Nubank, account_id: str):
        self.nu = nubank
        self.account_id = account_id

    def get_data(self):
        transactions = self.nu.get_account_statements()
        transactions = filter(self._filter_transaction, transactions)
        transactions = map(self._account_data_to_transaction, transactions)
        return transactions

    def _account_data_to_transaction(self, account_transaction: dict) -> Transaction:
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
        if account_transaction['__typename'] in OUTFLOW_EVENT_TYPES:
            amount *= -1
        return amount

    def _get_payee_from_acct_transaction(self, account_transaction: dict) -> str:
        transaction_type_map = {
            'BarcodePaymentEvent': 'detail',
            'TransferOutEvent': 'destinationAccount.name',
            'TransferInEvent': 'originAccount.name',
            'PixTransferOutEvent': 'destinationAccount.name',
            'PixTransferInEvent': 'originAccount.name',
            'BillPaymentEvent': 'title',
        }

        # Customizacao Pix
        if account_transaction['__typename'] == 'PixTransferOutEvent':
            payee, detail = account_transaction['detail'].split(u'\n')
            account_transaction['destinationAccount'] = {'name': payee}
        elif account_transaction['__typename'] in [ 'PixTransferInEvent', 'PixTransferOutReversalEvent' ]:
            try:
                payee, detail = account_transaction['detail'].split(u'\n')
            except ValueError as e:
                payee = 'Unknown'
                detail = account_transaction['detail']    
            account_transaction['originAccount'] = {'name': payee}
        
        # Customization: remove prefix and suffix for debit transactions
        if 'destinationAccount' in account_transaction and account_transaction['destinationAccount']['name'].startswith('Compra no débito '):
            destinationAccountName = account_transaction['destinationAccount']['name']
            # remove "Compra no débito " prefix
            string = re.sub(r'^Compra no débito ', '', string)
            # remove amount suffix
            string = re.sub(r' - R\$ \d+,\d{2}$', '', string)

            account_transaction['destinationAccount']['name'] = destinationAccountName
        
        field = transaction_type_map.get(account_transaction['__typename'])
        if field:
            return deep_get(account_transaction, field)

        return f'{account_transaction["title"]} {account_transaction["detail"]}'

    def _filter_transaction(self, account_transaction: dict) -> bool:
        return account_transaction['__typename'] != 'PixTransferScheduledEvent'