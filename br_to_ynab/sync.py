import base64
import json
from typing import TypedDict, List

from pynubank import Nubank
from ynab_sdk import YNAB
from ynab_sdk.utils.clients.cached_client import CachedClient
from ynab_sdk.utils.configurations.cached import CachedConfig

from importers.nubank.nubank_checking_account import NubankCheckingAccountData
from importers.nubank.nubank_credit_card import NubankCreditCardData
from importers.util import find_budget_by_name, find_account_by_name
from ynab.ynab_transaction_importer import YNABTransactionImporter


class ImporterConfig(TypedDict):
    ynab_token: str
    ynab_budget: str
    banks: List[str]
    start_import_date: str
    # Nubank
    nubank_login: str
    nubank_token: str
    nubank_user: str
    nubank_pw: str
    nubank_cert: str
    nubank_card_account: str
    nubank_checking_account: str


if __name__ == '__main__':
    importer_config: ImporterConfig = json.load(open('br-to-ynab.json'))

    ynab = YNAB(importer_config['ynab_token'])

    budget = find_budget_by_name(ynab.budgets.get_budgets().data.budgets, importer_config['ynab_budget'])
    ynab_accounts = ynab.accounts.get_accounts(budget.id).data.accounts

    ynab_importer = YNABTransactionImporter(ynab, budget.id, importer_config['start_import_date'])

    with open('cert.p12', 'wb') as f:
        cert_content = base64.b64decode(importer_config['nubank_cert'])
        f.write(cert_content)

    if 'Nubank' in importer_config['banks']:
        # nu = Nubank(client=MockHttpClient())
        nu = Nubank()
        #nu.authenticate_with_refresh_token(importer_config['nubank_token'], './cert.p12')
        nu.authenticate_with_cert(importer_config['nubank_user'], importer_config['nubank_pw'], './cert.p12')

        if importer_config['nubank_card_account']:
            account = find_account_by_name(ynab_accounts, importer_config['nubank_card_account'])
            nu_card_data = NubankCreditCardData(nu, account.id)
            ynab_importer.get_transactions_from(nu_card_data)

        if importer_config['nubank_checking_account']:
            account = find_account_by_name(ynab_accounts, importer_config['nubank_checking_account'])
            nu_checking_account = NubankCheckingAccountData(nu, account.id)
            ynab_importer.get_transactions_from(nu_checking_account)

    response = ynab_importer.save()
    print(ynab_importer.transactions)
    print(response)

    # print(f'{len(response["importers"]["transaction_ids"])} new transactions imported')
