"""Constants for stockpile."""
from logging import Logger, getLogger
from importlib.metadata import version

LOGGER: Logger = getLogger(__package__)
DOMAIN = "stockpile"

# Configuration
CONF_PILE_OF = "pile_of"
CONF_PILE_SIZE = "pile_size"
CONF_STEP_SIZE = "step_size"

# Services
SERVICE_EXPEND_STOCK = "expend_stock"

# Version displayed in UI
try:
    VERSION = version(DOMAIN)
except Exception:  # pylint: disable=broad-except
    VERSION = "2024.1.0"  # fallback if installed incorrectly
