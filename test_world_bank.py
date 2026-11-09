import httpx
import pytest

import world_bank
from world_bank import compare_countries, get_indicator, search_indicators


def test_invalid_year_range():
    with pytest.raises(ValueError):
        get_indicator(
            "GBR",
            "NY.GDP.MKTP.KD.ZG",
            2025,
            2000,
        )


def test_empty_country_list():
    with pytest.raises(ValueError):
        compare_countries(
            [],
            "FP.CPI.TOTL.ZG",
            2020,
            2023,
        )


def test_http_error(monkeypatch):
    def fake_get(*args, **kwargs):
        return httpx.Response(
            500,
            request=httpx.Request("GET", "https://api.worldbank.org"),
        )

    monkeypatch.setattr(world_bank.httpx, "get", fake_get)

    with pytest.raises(httpx.HTTPStatusError):
        get_indicator(
            "GBR",
            "NY.GDP.MKTP.KD.ZG",
            2020,
            2023,
        )


def test_missing_value(monkeypatch):
    payload = [
        {"total": 1},
        [
            {
                "country": {"value": "United Kingdom"},
                "indicator": {"value": "GDP growth (annual %)"},
                "date": "2023",
                "value": None,
            }
        ],
    ]

    def fake_get(*args, **kwargs):
        return httpx.Response(
            200,
            json=payload,
            request=httpx.Request("GET", "https://api.worldbank.org"),
        )

    monkeypatch.setattr(world_bank.httpx, "get", fake_get)

    result = get_indicator("GBR", "NY.GDP.MKTP.KD.ZG", 2023, 2023)

    assert result["observations"] == [{"year": 2023, "value": None}]


def test_partial_failure(monkeypatch):
    def fake_get_indicator(country, indicator, start_year, end_year):
        if country == "FRA":
            raise ValueError("Invalid country")

        return {"country_code": country}

    monkeypatch.setattr(world_bank, "get_indicator", fake_get_indicator)

    result = compare_countries(
        ["GBR", "FRA", "DEU"],
        "FP.CPI.TOTL.ZG",
        2020,
        2023,
    )

    assert len(result["countries"]) == 2
    assert result["partial"] is True
    assert result["errors"][0]["country"] == "FRA"


def test_search_indicators(monkeypatch):
    fake_catalogue = [
        {"id": "GDP", "name": "GDP growth"},
        {"id": "INF", "name": "Inflation, consumer prices"},
        {"id": "POP", "name": "Total population"},
    ]

    monkeypatch.setattr(world_bank, "get_catalogue", lambda: fake_catalogue)

    results = search_indicators("INFLATION")

    assert len(results) == 1
    assert results[0]["id"] == "INF"
