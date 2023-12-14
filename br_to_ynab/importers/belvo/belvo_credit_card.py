from typing import Iterable
import requests

from importers.data_importer import DataImporter
from importers.transaction import Transaction

class BelvoCreditCardData(DataImporter):    
    def __init__(self, account_id: str, belvo_auth: str, belvo_link: str, belvo_account: str, start_import_date: str):
        self.account_id = account_id
        self.belvo_auth = belvo_auth
        self.belvo_link = belvo_link
        self.belvo_account = belvo_account
        self.start_import_date = start_import_date

    def get_data(self) -> Iterable[Transaction]:
        url = "https://development.belvo.com/api/transactions/?page=1&page_size=1000&value_date__gte=" + self.start_import_date + "&link=" + self.belvo_link + "&account=" + self.belvo_account + "&fields=id,amount,description,observations,value_date,type"
        payload = {}
        headers = {
            'Authorization': self.belvo_auth
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        transactions = response.json()['results']

        return map(self._card_data_to_transaction, transactions)

    def _card_data_to_transaction(self, card_transaction: dict) -> Transaction:
        payee = memo = card_transaction['description']
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

        return {
            'transaction_id': card_transaction['id'],
            'account_id': self.account_id,
            'amount': amount * -1,
            'payee': payee,
            'date': card_transaction['value_date'],
            'memo': memo
        }