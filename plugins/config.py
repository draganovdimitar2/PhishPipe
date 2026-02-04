# URL
PHISHING_FEED_URL = "http://svn.code.sf.net/p/aper/code/phishing_reply_addresses"

# paths inside Docker container
DATA_DIR = "/opt/airflow/data"
CURRENT_FILE = f"{DATA_DIR}/phishing_current.csv"
PREVIOUS_FILE = f"{DATA_DIR}/phishing_previous.csv"