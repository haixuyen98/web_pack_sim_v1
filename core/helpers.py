from django_tenants.files.storage import TenantFileSystemStorage
from django.db import connection
import mimetypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import base64
import hashlib
from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ""
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
def uploadFileTenant(file):
    if file:
        fs = TenantFileSystemStorage()
        filename = fs.save(file.name, file)
        return fs.url(filename)
    else:
        return None

def formatCurrency(num):
    try:
        num = float(num)
    except (ValueError, TypeError):
        return "0"
    priceWithComma = "{:,.0f} ₫".format(num)
    priceWithDot = priceWithComma.replace(',', '.')
    return priceWithDot
def get_current_tenant():
    #  schema_name = connection.get_schema()
     tenant = connection.get_tenant()
     return tenant
def get_content_type(file_path):
    content_type, encoding = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

def decrypt_data(encrypted_data, secret_key):
    # Check if the encrypted data is empty
    if not encrypted_data:
        return ''

    # Check if the key is empty
    if not secret_key:
        raise ValueError("Secret key is empty.")

    # Convert the encrypted data from base64 to bytes
    encrypted_data_bytes = base64.b64decode(encrypted_data)

    # Create a valid AES key using the SHA-256 hash of the secret key
    key = hashlib.sha256(secret_key.encode()).digest()

    # Extract the IV from the encrypted data
    iv = encrypted_data_bytes[:AES.block_size]

    # Create a new AES cipher with the derived key and IV
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Perform the decryption, and remove the padding
    decrypted_data = unpad(cipher.decrypt(encrypted_data_bytes[AES.block_size:]), AES.block_size)

    # Convert the decrypted data to a string
    decrypted_data_str = decrypted_data.decode()

    return decrypted_data_str

def encrypt_data(data, secret_key):
    # Convert the data and secret key to bytes
    data_bytes = data.encode()
    secret_key_bytes = hashlib.sha256(secret_key.encode()).digest()  # Băm khóa
    # Generate a new AES cipher with the secret key
    cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
    # Pad the data to match the AES block size
    padded_data = pad(data_bytes, AES.block_size)
    # Perform the encryption
    encrypted_data = cipher.encrypt(padded_data)
    # Combine the IV and the encrypted data
    iv_and_encrypted_data = cipher.iv + encrypted_data
    # Base64 encode the encrypted data for easier storage or transmission
    encrypted_data_base64 = base64.b64encode(iv_and_encrypted_data).decode()
    return encrypted_data_base64

def autoClearCache(request):
    tenant = request.tenant
    try:
        cache_keys = cache.keys(tenant.schema_name+"*")  # Get all cache keys
        cache.delete_many(cache_keys)  # Delete all cache entries
    except Exception as e:
        print(e)
