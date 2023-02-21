from setuptools import setup, find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='br_to_ynab',
    version='0.0.1',
    packages=find_packages(),
    package_data={'pynubank': ['queries/*.gql', 'utils/mocked_responses/*.json']},
)