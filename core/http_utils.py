import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create a session
session = requests.Session()

# Configure retries
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

# Create an HTTPS adapter with connection pooling
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=100, max_retries=retries)

# Mount the HTTPS adapter to the session
session.mount('https://', adapter)
