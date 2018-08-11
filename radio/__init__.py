"""
Component to interface with universal radio control devices.

For more details about this component, please refer to the documentation
at https://home-assistant.io/components/radio/
"""
import asyncio
from datetime import timedelta
import functools as ft
import logging

import voluptuous as vol

from homeassistant.loader import bind_hass
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.entity import ToggleEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    STATE_ON, SERVICE_TURN_ON, SERVICE_TURN_OFF, SERVICE_TOGGLE,
    ATTR_ENTITY_ID)
from homeassistant.components import group
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA  # noqa

_LOGGER = logging.getLogger(__name__)

ATTR_ACTIVITY = 'activity'
ATTR_URL = 'url'
ATTR_VOLUME = 'volume'

DOMAIN = 'radio'
DEPENDENCIES = ['group']
SCAN_INTERVAL = timedelta(seconds=30)

ENTITY_ID_ALL_RADIOS = group.ENTITY_ID_FORMAT.format('all_radios')
ENTITY_ID_FORMAT = DOMAIN + '.{}'

GROUP_NAME_ALL_RADIOS = 'all radios'

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)

SERVICE_PLAY_URL = 'play_url'
SERVICE_SET_VOLUME = 'set_volume'
SERVICE_PLAY_NEXT = 'play_next'
SERVICE_PLAY_PREV = 'play_prev'
SERVICE_SYNC = 'sync'

DEFAULT_NUM_REPEATS = 1
DEFAULT_DELAY_SECS = 0.4

RADIO_SERVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
})

RADIO_SERVICE_ACTIVITY_SCHEMA = RADIO_SERVICE_SCHEMA.extend({
    vol.Optional(ATTR_ACTIVITY): cv.string
})

RADIO_SERVICE_PLAY_URL_SCHEMA = RADIO_SERVICE_SCHEMA.extend({
    vol.Required(ATTR_URL): cv.string,
})

RADIO_SERVICE_SET_VOLUME_SCHEMA = RADIO_SERVICE_SCHEMA.extend({
    vol.Required(ATTR_VOLUME): cv.string,
})

@bind_hass
def is_on(hass, entity_id=None):
    """Return if the radio is playing."""
    entity_id = entity_id or ENTITY_ID_ALL_RADIOS
    return hass.states.is_state(entity_id, STATE_ON)


@bind_hass
def turn_on(hass, activity=None, entity_id=None):
    """Turn all or specified radio on."""
    data = {
        key: value for key, value in [
            (ATTR_ACTIVITY, activity),
            (ATTR_ENTITY_ID, entity_id),
        ] if value is not None}
    hass.services.call(DOMAIN, SERVICE_TURN_ON, data)


@bind_hass
def turn_off(hass, activity=None, entity_id=None):
    """Turn all or specified radio off."""
    data = {}
    if activity:
        data[ATTR_ACTIVITY] = activity
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_TURN_OFF, data)


@bind_hass
def toggle(hass, activity=None, entity_id=None):
    """Toggle all or specified radio."""
    data = {}
    if activity:
        data[ATTR_ACTIVITY] = activity
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_TOGGLE, data)


@bind_hass
def play_next(hass, activity=None, entity_id=None):
    """Turn all or specified radio off."""
    data = {}
    if activity:
        data[ATTR_ACTIVITY] = activity
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_PLAY_NEXT, data)
    

@bind_hass
def play_prev(hass, activity=None, entity_id=None):
    """Turn all or specified radio off."""
    data = {}
    if activity:
        data[ATTR_ACTIVITY] = activity
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_PLAY_PREV, data)

@bind_hass
def play_url(hass, url, entity_id=None):
    """Play a url to a device."""
    data = {ATTR_URL: url}
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_PLAY_URL, data)

@bind_hass
def set_volume(hass, volume, entity_id=None):
    """Set volume of a device."""
    data = {ATTR_VOLUME: volume}
    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id
    hass.services.call(DOMAIN, SERVICE_SEND_COMMAND, data)

@asyncio.coroutine
def async_setup(hass, config):
    """Track states and offer events for radios."""
    component = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL, GROUP_NAME_ALL_RADIOS)
    yield from component.async_setup(config)

    @asyncio.coroutine
    def async_handle_radio_service(service):
        """Handle calls to the radio services."""
        target_radios = component.async_extract_from_service(service)
        kwargs = service.data.copy()

        update_tasks = []
        for radio in target_radios:
            if service.service == SERVICE_TURN_ON:
                yield from radio.async_turn_on(**kwargs)
            elif service.service == SERVICE_TOGGLE:
                yield from radio.async_toggle(**kwargs)
            elif service.service == SERVICE_PLAY_NEXT:
                yield from radio.async_play_next(**kwargs)
            elif service.service == SERVICE_PLAY_PREV:
                yield from radio.async_play_prev(**kwargs)
            elif service.service == SERVICE_PLAY_URL:
                yield from radio.async_play_url(**kwargs)
            elif service.service == SERVICE_SET_VOLUME:
                yield from radio.async_set_volume(**kwargs)
            else:
                yield from radio.async_turn_off(**kwargs)
            if not radio.should_poll:
                continue
            update_tasks.append(radio.async_update_ha_state(True))
        if update_tasks:
            yield from asyncio.wait(update_tasks, loop=hass.loop)

    hass.services.async_register(
        DOMAIN, SERVICE_TURN_OFF, async_handle_radio_service,
        schema=RADIO_SERVICE_ACTIVITY_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_TURN_ON, async_handle_radio_service,
        schema=RADIO_SERVICE_ACTIVITY_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_NEXT, async_handle_radio_service,
        schema=RADIO_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_PREV, async_handle_radio_service,
        schema=RADIO_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_TOGGLE, async_handle_radio_service,
        schema=RADIO_SERVICE_ACTIVITY_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_URL, async_handle_radio_service,
        schema=RADIO_SERVICE_PLAY_URL_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_SET_VOLUME, async_handle_radio_service,
        schema=RADIO_SERVICE_SET_VOLUME_SCHEMA)

    return True


class RadioDevice(ToggleEntity):
    """Representation of a radio."""

    def play_url(self, url, **kwargs):
        """Play url on a device."""
        raise NotImplementedError()
    def async_play_url(self, url, **kwargs):
        """Play url on a device.
        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.async_add_job(ft.partial(
            self.play_url, url, **kwargs))
            
    def set_volume(self, volume, **kwargs):
        """Play url on a device."""
        raise NotImplementedError()
    def async_set_volume(self, volume, **kwargs):
        """Play url on a device.
        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.async_add_job(ft.partial(
            self.set_volume, volume, **kwargs))
            
    def play_next(self, **kwargs):
        """Play next on a device."""
        raise NotImplementedError()
    def async_play_next(self, **kwargs):
        """Play next on a device.
        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.async_add_job(ft.partial(
            self.play_next, **kwargs))
            
    def play_prev(self, **kwargs):
        """Play prev on a device."""
        raise NotImplementedError()
    def async_play_prev(self, **kwargs):
        """Play prev on a device.
        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.async_add_job(ft.partial(
            self.play_prev, **kwargs))
