from typing import Iterable

from pynubank import Nubank

from importers.data_importer import DataImporter
from importers.transaction import Transaction


class NubankCreditCardData(DataImporter):

    def __init__(self, nubank: Nubank, account_id: str):
        self.nu = nubank
        self.account_id = account_id

    def get_data(self) -> Iterable[Transaction]:
        transactions = self.nu.get_card_statements()

        return map(self._card_data_to_transaction, transactions)

    def _card_data_to_transaction(self, card_transaction: dict) -> Transaction:
        payee = memo = card_transaction['description']

        # Customization: Set payee and memo according to the amount for transactions via Apple.
        if 'Apple' == card_transaction['description']:
            apple_subscriptions = {
                3.50: "iCloud+",
                11.90: "Apple Music",
                89.90: "TickTick",
                26.90: "Erol Singers",
                279.90: "Elsa Premium"
            }

            payee = memo = apple_subscriptions.get(amount, card_transaction['description'])

        return {
            'transaction_id': card_transaction['id'],
            'account_id': self.account_id,
            'amount': card_transaction['amount'] * 10 * -1,
            'payee': payee,
            'date': card_transaction['time'][:10],
            'memo': memo
        }
