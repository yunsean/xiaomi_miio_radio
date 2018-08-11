"""
Support for the Xiaomi Gateway Radio.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/radio.xiaomi_miio/
"""
import asyncio
import logging
import time
import json

from datetime import timedelta

import voluptuous as vol

from homeassistant.components.radio import (
    PLATFORM_SCHEMA, DOMAIN, RadioDevice)
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_TOKEN, CONF_TIMEOUT,
    ATTR_ENTITY_ID, ATTR_HIDDEN, CONF_COMMAND)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.util.dt import utcnow

REQUIREMENTS = ['python-miio==0.4.0', 'construct==2.9.41']

_LOGGER = logging.getLogger(__name__)

LEARN_COMMAND_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): vol.All(str),
})

COMMAND_SCHEMA = vol.Schema({
    vol.Required(CONF_COMMAND): vol.All(cv.ensure_list, [cv.string])
    })

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
}, extra=vol.ALLOW_EXTRA)


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the Xiaomi Gateway platform."""
    from miio import Device, DeviceException

    host = config.get(CONF_HOST)
    token = config.get(CONF_TOKEN)

    # Create handler
    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])

    # The Chuang Mi IR Radio Controller wants to be re-discovered every
    # 5 minutes. As long as polling is disabled the device should be
    # re-discovered (lazy_discover=False) in front of every command.
    device = Device(host, token, lazy_discover=False)

    # Check that we can communicate with device.
    try:
        device_info = device.info()
        model = device_info.model
        unique_id = "{}-{}".format(model, device_info.mac_address)
        _LOGGER.info("%s %s %s detected",
                     model,
                     device_info.firmware_version,
                     device_info.hardware_version)
    except DeviceException as ex:
        _LOGGER.error("Device unavailable or token incorrect: %s", ex)
        raise PlatformNotReady
    friendly_name = config.get(CONF_NAME, "miio_radio_" + host.replace('.', '_'))
    xiaomi_miio_radio = XiaomiMiioRadio(friendly_name, device, unique_id)
    async_add_devices([xiaomi_miio_radio])


class XiaomiMiioRadio(RadioDevice):
    """Representation of a Xiaomi Miio Radio device."""

    def __init__(self, friendly_name, device, unique_id):
        """Initialize the radio."""
        self._name = friendly_name
        self._device = device
        self._unique_id = unique_id
        self._state = False

    @property
    def name(self):
        """Return the name of the radio."""
        return self._name

    @property
    def device(self):
        """Return the radio object."""
        return self._device

    @property
    def is_on(self):
        """Return False if device is unreachable, else True."""
        from miio import DeviceException
        try:
            status = self._device.send("get_prop_fm", [])
            return status["current_status"] == "run"
        except DeviceException:
            return False

    @property
    def should_poll(self):
        """We should not be polled for device up state."""
        return True

    @property
    def device_state_attributes(self):
        """Hide radio by default."""
        attrs = {
            'hidden': 'true',
            'channels': self._device.send("get_channels", {"start": 0}),
            'space_free': self._device.send("get_music_free_space", [])
        }
        return attrs
        
    @asyncio.coroutine
    def async_toggle(self, **kwargs):
        """Toggle the device."""
        if self.is_on:
            self._device.send('play_fm', ["off"])
        else:
            self._device.send('play_fm', ["on"])

    # pylint: disable=R0201
    @asyncio.coroutine
    def async_turn_on(self, **kwargs):
        """Turn the device on."""
        self._device.send('play_fm', ["on"])

    @asyncio.coroutine
    def async_turn_off(self, **kwargs):
        """Turn the device off."""
        self._device.send('play_fm', ["off"])

    def _play_url(self, payload):
        """Play specified url on device."""
        if payload is None:
            _LOGGER.debug("Empty packet.")
            return True
        try:
            self._device.send('play_specify_fm', {'id': int(str(payload)), 'type': 0})
            _LOGGER.error(str(payload))
        except ValueError as error:
            _LOGGER.error(error)
            return False
        return True

    def play_url(self, url, **kwargs):
        """Wrapper for _play_url."""
#        _LOGGER.error(self._device.send("get_prop_fm", []))
#        _LOGGER.error(self._device.send("get_channels", {"start": 0}))
#        _LOGGER.error(self._device.send("get_lumi_dpf_aes_key", []))
#        _LOGGER.error(self._device.send("get_zigbee_channel", []))
#        _LOGGER.error(self._device.send("miIO.info", []))
#        _LOGGER.error(self._device.send("get_prop_fm", []))
        self._play_url(url)
            
    def _set_volume(self, payload):
        """Set volume to device."""
        if payload is None:
            _LOGGER.debug("Empty packet.")
            return True
        try:
            self._device.send('volume_ctrl_fm', [str(payload)])
            _LOGGER.info(str(payload))
        except ValueError as error:
            _LOGGER.error(error)
            return False
        return True
            
    def set_volume(self, volume, **kwargs):
        """Wrapper for _set_volume."""
        self._set_volume(volume)            
            
