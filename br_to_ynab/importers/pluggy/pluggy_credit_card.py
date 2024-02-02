from typing import Iterable
import requests

from importers.data_importer import DataImporter
from importers.transaction import Transaction

class PluggyCreditCardData(DataImporter):

    def __init__(self, account_id: str, pluggy_client_id: str, pluggy_client_secret: str, pluggy_item_id: str, pluggy_account: str, start_import_date: str, sharedCreditCard: str):
        self.account_id = account_id
        self.pluggy_client_id = pluggy_client_id
        self.pluggy_client_secret = pluggy_client_secret
        self.pluggy_item_id = pluggy_item_id
        self.pluggy_account = pluggy_account
        self.start_import_date = start_import_date
        self.shared_credit_card = sharedCreditCard

    def get_data(self) -> Iterable[Transaction]:
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

        return map(self._card_data_to_transaction, transactions)

    def _card_data_to_transaction(self, card_transaction: dict) -> Transaction:
        payee = memo = card_transaction['description']

        if card_transaction['amountInAccountCurrency'] is not None:
            amount = int(card_transaction['amountInAccountCurrency'] * 1000)
        else:
            amount = int(card_transaction['amount'] * 1000) 

        # Customization: Set payee and memo according to the amount for transactions via Apple.
        if 'Apple.Com/Bill' == card_transaction['description']:
            apple_subscriptions = {
                350: "iCloud+", # $3.50 
                1190: "Apple Music", # $11.90 
                1490: "iCloud+", # $14.90
                8990: "TickTick", # $89.90 
                2690: "Erol Singers Studio", # $26.90
                27990: "Elsa Premium" # $279.90 
            }

            payee = memo = apple_subscriptions.get(card_transaction['amount'], card_transaction['description'])

        if card_transaction['creditCardMetadata']['cardNumber'] == self.shared_credit_card:
            memo = 'CARTÃO COLETIVO - ' + memo

        return {
            'transaction_id': card_transaction['id'],
            'account_id': self.account_id,
            'amount': amount * -1,
            'payee': payee,
            'date': card_transaction['date'][0:10],
            'memo': memo
        }