# URL
PHISHING_FEED_URL = "http://svn.code.sf.net/p/aper/code/phishing_reply_addresses"

# paths inside Docker container
DATA_DIR = "/opt/airflow/data"
PHISHING_CURRENT_FILE_PATH = f"{DATA_DIR}/phishing_current.csv"
PHISHING_PREVIOUS_FILE_PATH = f"{DATA_DIR}/phishing_previous.csv"

# Airflow Variable keys (persisted in Airflow metadata DB)
PHISHING_CURRENT_HASH_VARIABLE_KEY = "phishing_current_hash"
PHISHING_PREVIOUS_HASH_VARIABLE_KEY = "phishing_previous_hash"