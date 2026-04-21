import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("trading_bot.client")


class BinanceClientError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class NetworkError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self._api_key,
        })

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        logger.debug("HTTP %s %s", response.status_code, response.url)
        logger.debug("Response body: %s", response.text)
        try:
            data = response.json()
        except ValueError as exc:
            raise NetworkError(f"Non-JSON response: {response.text}") from exc
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(code=data["code"], message=data.get("msg", "Unknown error"))
        response.raise_for_status()
        return data

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        params["timestamp"] = self._timestamp()
        query_string = urlencode(params)
        signature = self._sign(query_string)
        full_url = f"{BASE_URL}{endpoint}?{query_string}&signature={signature}"
        logger.debug("GET %s", endpoint)
        try:
            response = self._session.get(full_url, timeout=10)
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network failure: {exc}") from exc
        return self._handle_response(response)

    def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        params["timestamp"] = self._timestamp()
        query_string = urlencode(params)
        signature = self._sign(query_string)
        full_url = f"{BASE_URL}{endpoint}"
        body = f"{query_string}&signature={signature}"
        logger.debug("POST %s", endpoint)
        try:
            response = self._session.post(
                full_url,
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"Network failure: {exc}") from exc
        return self._handle_response(response)