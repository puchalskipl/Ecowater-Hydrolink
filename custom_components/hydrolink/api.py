# -*- coding: utf-8 -*-
"""EcoWater HydroLink API interface."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import logging
import requests
import websocket
import threading
import time

_LOGGER = logging.getLogger(__name__)


@dataclass
class Device:
    """Represents a HydroLink device."""

    id: str
    nickname: str
    system_type: str
    properties: Dict[str, Any]


class HydroLinkApi:
    """HydroLink API interface.

    Handles authentication, data retrieval, and WebSocket connections
    for EcoWater HydroLink water softeners.
    """

    DEFAULT_BASE_URL = "https://api.hydrolinkhome.com/v1"
    DEFAULT_WS_BASE_URL = "wss://api.hydrolinkhome.com"

    def __init__(self, email: str, password: str, region: str = "united_states") -> None:
        """Initialize the API."""
        from .const import REGIONS, REGION_US

        self.email: str = email
        self.password: str = password
        self.auth_cookie: Optional[str] = None
        self.ws_message_count: int = 0
        self.waiting_for_ws_thread_to_end: int = 1
        self.ws_uri: str = ""

        region_config = REGIONS.get(region, REGIONS[REGION_US])
        self.BASE_URL: str = region_config["base_url"]
        self.WS_BASE_URL: str = region_config["ws_base_url"]
        self.auth_cookie_name: str = region_config["auth_cookie_name"]

    def login(self) -> bool:
        """Authenticate with the HydroLink API.

        Raises:
            InvalidAuth: If the credentials are invalid.
            CannotConnect: If there is a connection or timeout error.
        """
        try:
            response = requests.post(
                f"{self.BASE_URL}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=10,
            )

            if response.status_code == 401:
                raise InvalidAuth("Invalid email or password")
            elif response.status_code == 429:
                raise CannotConnect("Rate limit exceeded")
            elif response.status_code >= 500:
                raise CannotConnect(f"Server error: {response.status_code}")

            response.raise_for_status()

            self.auth_cookie = response.cookies.get(self.auth_cookie_name)
            if not self.auth_cookie:
                raise CannotConnect("No authentication cookie received")

            _LOGGER.info("HydroLink login successful")
            return True

        except requests.Timeout:
            raise CannotConnect("Connection timed out") from None
        except requests.ConnectionError:
            raise CannotConnect("Failed to connect to HydroLink") from None
        except requests.RequestException as err:
            raise CannotConnect(f"Unknown error: {err}") from err

    def _start_ws(self) -> None:
        """Start the WebSocket client for real-time updates.

        Connects to the device WebSocket and closes after 17 messages
        to trigger a data refresh on the server side.
        """
        def on_message(ws: websocket.WebSocketApp, message: str) -> None:
            try:
                self.ws_message_count += 1
                if _LOGGER.isEnabledFor(logging.DEBUG):
                    data = json.loads(message)
                    _LOGGER.debug("WebSocket message: %s", data)
                if self.ws_message_count >= 17:
                    ws.close()
            except json.JSONDecodeError as err:
                _LOGGER.warning("Failed to parse WebSocket message: %s", err)

        def on_open(ws: websocket.WebSocketApp) -> None:
            _LOGGER.debug("WebSocket connection established")

        def on_close(ws: websocket.WebSocketApp, close_status_code: int,
                    close_msg: str) -> None:
            _LOGGER.debug("WebSocket closed: %s %s", close_status_code, close_msg)

        def on_error(ws: websocket.WebSocketApp, error: Exception) -> None:
            _LOGGER.error("WebSocket error: %s", error)

        try:
            self.ws_message_count = 0
            ws = websocket.WebSocketApp(
                self.ws_uri,
                on_message=on_message,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error,
            )
            ws.run_forever()
        except Exception as err:
            _LOGGER.error("WebSocket connection failed: %s", err)
            raise CannotConnect("WebSocket connection failed") from err
        finally:
            self.waiting_for_ws_thread_to_end = 0

    def get_data(self) -> List[Dict[str, Any]]:
        """Get the latest data from the HydroLink API.

        Fetches devices, opens a WebSocket per device to trigger fresh data,
        then fetches updated device data.

        Raises:
            InvalidAuth: If authentication has expired.
            CannotConnect: If there are connection issues.
        """
        if not self.auth_cookie:
            self.login()

        try:
            response = requests.get(
                f"{self.BASE_URL}/devices",
                params={"all": "false", "per_page": "200"},
                cookies={self.auth_cookie_name: self.auth_cookie},
                timeout=10,
            )

            if response.status_code == 401:
                self.auth_cookie = None
                raise InvalidAuth("Authentication expired")

            response.raise_for_status()
            devices = response.json().get("data", [])

            for device in devices:
                try:
                    device_id = device.get("id")
                    if not device_id:
                        _LOGGER.warning("Device without ID found, skipping")
                        continue

                    response = requests.get(
                        f"{self.BASE_URL}/devices/{device_id}/live",
                        cookies={self.auth_cookie_name: self.auth_cookie},
                        timeout=10,
                    )
                    response.raise_for_status()

                    ws_path = response.json().get("websocket_uri")
                    if not ws_path:
                        _LOGGER.warning("No WebSocket URI for device %s", device_id)
                        continue

                    self.ws_uri = f"{self.WS_BASE_URL}{ws_path}"
                    self.waiting_for_ws_thread_to_end = 1

                    ws_thread = threading.Thread(
                        target=self._start_ws,
                        name=f"HydroLink-WS-{device_id}",
                        daemon=True
                    )
                    ws_thread.start()

                    start_time = time.time()
                    while self.waiting_for_ws_thread_to_end:
                        time.sleep(0.5)
                        if time.time() - start_time > 15:
                            _LOGGER.warning("WebSocket timeout for device %s", device_id)
                            break

                    ws_thread.join(timeout=5)
                    if ws_thread.is_alive():
                        _LOGGER.warning("WebSocket thread did not terminate for device %s", device_id)

                except requests.RequestException as err:
                    _LOGGER.error("Error refreshing device %s: %s", device.get("id", "unknown"), err)

            response = requests.get(
                f"{self.BASE_URL}/devices",
                params={"all": "false", "per_page": "200"},
                cookies={self.auth_cookie_name: self.auth_cookie},
                timeout=10,
            )
            response.raise_for_status()

            return response.json().get("data", [])

        except requests.Timeout:
            raise CannotConnect("Connection timed out") from None
        except requests.ConnectionError:
            raise CannotConnect("Failed to connect to HydroLink") from None
        except requests.RequestException as err:
            raise CannotConnect(f"Error fetching device data: {err}") from err

    def trigger_regeneration(self, device_id: str) -> bool:
        """Trigger a manual regeneration for a specific device."""
        if not self.auth_cookie:
            self.login()

        try:
            response = requests.post(
                f"{self.BASE_URL}/devices/{device_id}/regenerate",
                cookies={self.auth_cookie_name: self.auth_cookie},
                timeout=10
            )

            if response.status_code == 401:
                self.auth_cookie = None
                raise InvalidAuth("Authentication expired")

            response.raise_for_status()
            return True

        except requests.Timeout:
            raise CannotConnect("Connection timed out") from None
        except requests.ConnectionError:
            raise CannotConnect("Failed to connect to HydroLink") from None
        except requests.RequestException as err:
            raise CannotConnect(f"Error triggering regeneration: {err}") from err


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
