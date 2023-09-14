
import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase
import boto3
import os

ssm = boto3.client('ssm')
lambda_client = boto3.client('lambda')

def get_parameter_from_ssm(parameter_name):
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

API_KEY = get_parameter_from_ssm('cb_deposit_apiKey')
API_SECRET = get_parameter_from_ssm('cb_deposit_apiSecret')
DEPOSIT_ID = get_parameter_from_ssm('cb_deposit_depositId')
PAYMENT_METHOD = get_parameter_from_ssm('cb_deposit_paymentMethod')
#Change your deposit amount and fiat currency
DEPOSIT_AMOUNT = 200
DEPOSIT_CURRENCY = 'USD'


#Coinbase API Endpoints
DEPOSIT_ENDPOINT = f'https://api.coinbase.com/v2/accounts/{DEPOSIT_ID}/deposits'
PAYMENT_METHOD_ENDPOINT = 'https://api.coinbase.com/v2/payment-methods'

#Authenticate with Coinbase API
class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request

#Function to List Payment Methods - need this for getting DEPOSIT_ID and Payment_Method
def list_payment_methods():
    # print('API_KEY: ', API_KEY, 'DEPOSIT_ID: ', DEPOSIT_ID)
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    response = requests.get(PAYMENT_METHOD_ENDPOINT, auth=auth)
    print('repsonse: ', response)
    data = response.json()
    print('data: ', data)
    payment_methods = [{
        'id': item['fiat_account']['id'] if item['type'] == 'fiat_account' else item['id'],
        'name': item['name'],
        'currency': item['currency'],
        'type': item['type'],
        'description': (item['limits']['buy'][0]['description']
                        if 'limits' in item and 'buy' in item['limits'] and item['limits']['buy']
                        else None)
    } for item in data['data']]

    for method in payment_methods:
        print(method)

# Function to Deposit USD
def deposit_fiat(amount):
    auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
    data = {
        'type': 'deposit',
        'amount': amount,
        'currency': DEPOSIT_CURRENCY,
        'payment_method': PAYMENT_METHOD
    }

    response = requests.post(DEPOSIT_ENDPOINT, data=data, auth=auth)
    if response.status_code == 201:
        print(f'You deposited {amount} {DEPOSIT_CURRENCY} into your Coinbase account!')
        print(response.json())
        return response.json()
    else:
        raise Exception(f'Error: {response.text}')

def lambda_handler(event, context):
    # list_payment_methods()
    deposit_fiat(DEPOSIT_AMOUNT)

