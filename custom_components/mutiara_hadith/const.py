"""Constants for Mutiara Hadith (JAKIM)."""
from datetime import timedelta

DOMAIN = "mutiara_hadith"
VERSION = "0.4.1"
FRONTEND_URL = f"/{DOMAIN}_frontend"
CARD_FILENAME = "mutiara-hadith-card.js"
BASE_URL = "https://myhadith.islam.gov.my"
ATTRIBUTION = "Sumber: MyHadith, Jabatan Kemajuan Islam Malaysia (JAKIM)"

CONF_MODE = "mode"
CONF_API_KEY = "api_key"
CONF_SCAN_HOURS = "scan_hours"

MODE_SCRAPE = "scrape"
MODE_API = "api"

DEFAULT_SCAN_HOURS = 6
MIN_SCAN_HOURS = 1
MAX_SCAN_HOURS = 24

REQUEST_TIMEOUT = 30
USER_AGENT = "HomeAssistant-MutiaraHadith/0.4.1 (+https://github.com/zubir2k/homeassistant-mutiarahadith)"
STATE_MAX_LEN = 255
DEFAULT_INTERVAL = timedelta(hours=DEFAULT_SCAN_HOURS)
