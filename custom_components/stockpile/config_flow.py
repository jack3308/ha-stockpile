"""Config flow for Stockpile."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_PILE_OF, CONF_PILE_SIZE, CONF_STEP_SIZE, DOMAIN

class StockpileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stockpile."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Generate unique ID from pile name
            await self.async_set_unique_id(user_input[CONF_PILE_OF])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input[CONF_PILE_OF],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PILE_OF): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_PILE_SIZE, default=0): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(CONF_STEP_SIZE, default=1.0): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.01,
                            step=0.01,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )