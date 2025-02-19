from datetime import datetime
from typing import List

from ynab_sdk import YNAB
from ynab_sdk.api.models.requests.transaction import TransactionRequest

from typing import TypedDict, Iterable
import abc

class Transaction(TypedDict):
    transaction_id: str
    account_id: str
    payee: str
    amount: int
    date: str

class DataImporter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_data(self) -> Iterable[Transaction]:
        raise NotImplementedError
    


class YNABTransactionImporter:
    def __init__(self, ynab: YNAB, budget_id: str, starting_date: str):
        self.ynab = ynab
        self.budget_id = budget_id
        self.starting_date = datetime.strptime(starting_date, '%Y-%m-%d')
        self.transactions: List[TransactionRequest] = []

    def get_transactions_from(self, transaction_importer: DataImporter):
        transactions = transaction_importer.get_data()
        transactions = filter(self._filter_transaction, transactions)
        transformed = map(self._create_transaction_request, transactions)
        self.transactions.extend(transformed)
        return self

    def save(self):
        return self.ynab.transactions.create_transactions(self.budget_id, self.transactions)

    def _create_transaction_request(self, transaction: Transaction) -> TransactionRequest:
        return TransactionRequest(
            transaction['account_id'],
            transaction['date'],
            transaction['amount'],
            payee_name=transaction['payee'],
            import_id=transaction['transaction_id'],
            memo=transaction["memo"]
        )

    def _filter_transaction(self, transaction: Transaction) -> bool:
        transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d')

        return transaction_date >= self.starting_date

