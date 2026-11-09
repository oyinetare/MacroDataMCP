from typing import TypedDict

from mcp.server.mcpserver import MCPServer

from world_bank import compare_countries, get_indicator, search_indicators


class Observation(TypedDict):
    year: int
    value: float | None


class IndicatorResult(TypedDict):
    country: str
    country_code: str
    indicator: str
    indicator_code: str
    observations: list[Observation]
    source: str


class CountryError(TypedDict):
    country: str
    message: str


class ComparisonResult(TypedDict):
    countries: list[IndicatorResult]
    errors: list[CountryError]
    partial: bool


mcp = MCPServer("MacroData MCP")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b


@mcp.tool(name="get_indicator")
def get_indicator_tool(
    country: str,
    indicator: str,
    start_year: int,
    end_year: int,
) -> IndicatorResult:
    """Retrieve World Bank economic data.

    Country must be a three-letter code, e.g. GBR or USA.
    Indicator must be a World Bank code, e.g. NY.GDP.MKTP.KD.ZG for GDP growth.
    """
    return get_indicator(country, indicator, start_year, end_year)


@mcp.tool(name="compare_countries")
def compare_countries_tool(
    countries: list[str],
    indicator: str,
    start_year: int,
    end_year: int,
) -> ComparisonResult:
    """Compare an economic indicator across multiple countries."""
    return compare_countries(
        countries,
        indicator,
        start_year,
        end_year,
    )


@mcp.tool(name="search_indicators")
def search_indicators_tool(query: str) -> list[dict]:
    """Search World Bank economic indicators by name."""
    return search_indicators(query)
