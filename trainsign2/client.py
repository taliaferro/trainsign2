import logging
from urllib.parse import urljoin

import requests


class Open511Client:
    def __init__(
        self,
        url: str = "https://api.511.org",
        agency: str = None,
        api_key: str = None,
        rate_limit: int = 60,
        limit_remaining: int = 60,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.agency = agency

        # resets every hour, on the hour
        # these are initial values only -- the actual value is helpfully returned
        # in the response headers of every request
        self.rate_limit = rate_limit
        self.limit_remaining = limit_remaining

    def _api_get(
        self, endpoint: str, params: dict, raise_for_status: bool = True
    ) -> dict:
        params = {k: v for k, v in params.items() if v is not None}
        params.update({"api_key": self.api_key, "format": "json"})
        request_url = urljoin(self.url, endpoint)

        response = requests.get(request_url, params=params)

        if raise_for_status:
            response.raise_for_status()

        # update rate limit awareness
        self.rate_limit = int(response.headers.get("RateLimit-Limit", self.rate_limit))
        self.limit_remaining = int(
            response.headers.get("RateLimit-Remaining", self.limit_remaining)
        )

        # they sometimes return data in `utf-8-sig` encoding and don't mark it correctly
        if response.text[0] == "\ufeff":
            response.encoding = "utf-8-sig"
        return response

    def stop_monitoring(self, agency: str = None, stop_code: str = None) -> dict:
        params = {"agency": agency if agency else self.agency, "stop_code": stop_code}
        resp = self._api_get("transit/StopMonitoring", params=params)
        return resp.json()

    def vehicle_monitoring(self, agency: str, vehicle_id: str = None) -> dict:
        params = {"agency": agency if agency else self.agency, "vehicle_id": vehicle_id}
        return self._api_get("transit/VehicleMonitoring", params=params).json()

    def operators(self, operator_id: str = None) -> dict:
        params = {"operator_id": operator_id if operator_id else self.agency}
        resp = self._api_get("transit/operators", params=params)
        return resp.json()

    def lines(self, operator_id: str = None, line_id: str = None) -> dict:
        params = {
            "operator_id": operator_id if operator_id else self.agency,
            "line_id": line_id,
        }
        return self._api_get("transit/lines", params=params).json()

    def stops(
        self,
        operator_id: str = None,
        include_stop_areas=None,
        direction_id=None,
        stop_id=None,
        pattern_id=None,
    ) -> dict:
        params = {
            "operator_id": operator_id if operator_id else self.agency,
            "include_stop_areas": include_stop_areas,
            "direction_id": direction_id,
            "stop_id": stop_id,
            "pattern_id": pattern_id,
        }
        return self._api_get("transit/stops", params=params).json()

    def stop_places(self, operator_id: str = None, stop_id: str = None) -> dict:
        params = {
            "operator_id": operator_id if operator_id else self.agency,
            "stop_id": stop_id,
        }
        return self._api_get("transit/stopplaces", params=params).json()

    def patterns(
        self, line_id: str, operator_id: str = None, pattern_id: str = None
    ) -> dict:
        params = {
            "operator_id": operator_id,
            "line_id": line_id,
            "pattern_id": pattern_id,
        }
        return self._api_get("transit/patterns", params=params).json()

    def timetable(
        self,
        line_id: str,
        operator_id: str = None,
        includespecialservice: bool = None,
        exceptiondate: str = None,
    ) -> dict:
        params = {
            "operator_id": operator_id if operator_id else self.agency,
            "line_id": line_id,
            "includespecialservice": includespecialservice,
            "exceptiondate": exceptiondate,
        }
        return self._api_get("transit/timetable", params=params).json()

    def stop_timetable(
        self,
        monitoringref: str,
        operatorref: str = None,
        lineref: str = None,
        starttime: str = None,
        endtime: str = None,
    ):
        params = {
            "operatorref": operatorref if operatorref else self.agency,
            "monitoringref": monitoringref,
            "lineref": lineref,
            "starttime": starttime,
            "endtime": endtime,
        }
        return self._api_get("transit/stoptimetable", params=params).json()

    def holidays(self, operator_id: str = None):
        params = {"operator_id": operator_id if operator_id else self.agency}
        resp = self._api_get("transit/holidays", params=params)
        return resp.json()
