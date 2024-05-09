import hmac
import hashlib
import base64
from .constants import verifyUserInfoEndpoint
import requests

def b64encode(encodeString, secret):
    # Convert the secret key to bytes
    secret_bytes = secret.encode('utf-8')

    # Calculate the HMAC SHA256 hash
    hash_object = hmac.new(secret_bytes, encodeString.encode('utf-8'), hashlib.sha256)
    hash_digest = hash_object.digest()

    # Encode the hash digest using base64
    sig = base64.b64encode(hash_digest).decode('utf-8')
    return sig
def getKeepingFee(price, keeping_percent):
    keeping_percent = int(keeping_percent)
    if keeping_percent>0:
        return price * keeping_percent/100
    else:
        return price
def get_mb_user_info(login_token, tenant):
    config = tenant.config
    mb_bank_base_api = config.get("mb_bank_base_api", None)
    mb_bank_merchant_secret = config.get("mb_bank_merchant_secret", None)
    mb_bank_merchant_code = config.get("mb_bank_merchant_code", None)
    allow_sale_via_bank = config.get("allow_sale_via_bank", 'off')
    verify_user_url = f"{mb_bank_base_api}{verifyUserInfoEndpoint}"
    headers = {
        'Content-Type': 'application/json',
        'MERCHANT_CODE': mb_bank_merchant_code,
        'MERCHANT_SECRET': mb_bank_merchant_secret,
    }
    body_request = {
        "token":login_token
    }
    response = requests.post(url=verify_user_url, headers=headers, json=body_request)
    json_data = response.json()
    if response.status_code == 200:
        return json_data
        
    return None
