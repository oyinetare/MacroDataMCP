from functools import lru_cache

import httpx


def compare_countries(
    countries: list[str],
    indicator: str,
    start_year: int,
    end_year: int,
) -> dict:
    if not countries:  # guard clause
        raise ValueError("At least one country is required")

    if start_year > end_year:
        raise ValueError("start_year cannot be greater than end_year")

    results = []
    errors = []

    for country in countries:
        try:
            result = get_indicator(
                country,
                indicator,
                start_year,
                end_year,
            )
            results.append(result)
        except ValueError as error:
            errors.append(
                {
                    "country": country,
                    "message": str(error),
                }
            )

    return {
        "countries": results,
        "errors": errors,
        "partial": bool(errors),
    }


def get_indicator(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
) -> dict:
    if start_year > end_year:
        raise ValueError("start_year cannot be greater than end_year")

    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
    }

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()  # raise if server returns unsuvvesful HTTP status (4xx or 5xx)

    data = response.json()

    if (
        isinstance(data, list)
        and len(data) == 1
        and isinstance(data[0], dict)
        and "message" in data[0]
    ):
        raise ValueError("World Bank API rejected the request")

    raw_observations = data[1]

    if not raw_observations:
        raise ValueError("No observations found for the requested indicator")

    observations = []

    for item in raw_observations:
        observation = {
            "year": int(item["date"]),
            "value": item["value"],
        }
        observations.append(observation)

    return {
        "country": raw_observations[0]["country"]["value"],
        "country_code": country,
        "indicator": raw_observations[0]["indicator"]["value"],
        "indicator_code": indicator,
        "observations": observations,
        "source": "World Bank",
    }


@lru_cache(maxsize=1)
def get_catalogue() -> list[dict]:
    url = "https://api.worldbank.org/v2/indicator"

    params = {
        "format": "json",
        "source": 2,
        "per_page": 2000,
    }

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    indicators = data[1]

    return indicators


def search_indicators(query: str) -> list[dict]:
    indicators = get_catalogue()
    matches = []

    for indicator in indicators:
        name = indicator["name"]

        if query.lower() in name.lower():
            matches.append(indicator)

    return matches
