"""Constants for stockpile."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
DOMAIN = "stockpile"

# Configuration
CONF_PILE_OF = "pile_of"
CONF_PILE_SIZE = "pile_size"
CONF_STEP_SIZE = "step_size"

# Services
SERVICE_EXPEND_STOCK = "expend_stock"

# Version displayed in UI
from homeassistant.util import package

from importlib.metadata import version

DOMAIN = "stockpile"
try:
    VERSION = version(DOMAIN)
except Exception:  # pylint: disable=broad-except
    VERSION = "2024.10.06"  # fallback if installed incorrectly

# Remove DISPLAY_VERSION since we'll use VERSION instead