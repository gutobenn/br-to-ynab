import unittest
from datetime import datetime
from typing import List
from unittest.mock import Mock

from pybradesco import Bradesco, BradescoTransaction

from br_to_ynab.importers.bradesco.bradesco_credit_card import BradescoCreditCard


def fake_transactions() -> List[BradescoTransaction]:
    return [
        BradescoTransaction(datetime.now(), 'Some Mall', 22.50),
        BradescoTransaction(datetime.now(), 'Some Store', 32.1),
        BradescoTransaction(datetime.now(), 'Some Parking Lot', 5),
    ]


class TestBradescoCreditCard(unittest.TestCase):

    def test_should_get_transactions(self):
        fake_bradesco = Mock(Bradesco)
        fake_bradesco.get_credit_card_statements.return_value = fake_transactions()

        importer = BradescoCreditCard(fake_bradesco, '1234')

        transactions = list(importer.get_data())

        self.assertEqual(len(transactions), len(fake_transactions()))

        transaction = transactions[0]
        fake_transaction = fake_transactions()[0]

        self.assertEqual(transaction['account_id'], '1234')
        self.assertEqual(transaction['amount'], fake_transaction.amount * 1000)
        self.assertEqual(transaction['date'], fake_transaction.date.strftime('%Y-%m-%d'))
        self.assertEqual(transaction['payee'], fake_transaction.description)
        self.assertIsInstance(transaction['transaction_id'], str)
