# MacroData MCP

Very very very simple MCP server to provide AI apps w access to real economic data from World Bank Indicators API.

---

## Features

- [x] Search economic indicators by name
- [x] Retrieve country-level economic time series
- [x] Compare economic indicators across multiple countries
- [x] Return structured data with country and indicator metadata
- [x] Handle missing observations and API errors
- [x] Support local AI integration using Ollama

---

## Tech Stack

- Python 3.12+
- Official MCP Python SDK
- httpx
- pytest
- Astral uv
- Ollama (optional), I used `qwen3:1.7b`

---

## Architecture

This MCP seperates economic data retrieval from interacting w an AI model

- `world_bank.py` handles HTTP requests, validation,
  JSON parsing and data transformation.
- `main.py` registers the economic-data functions
  as MCP tools.
- `mcp_client_test.py` demonstrates how a Python MCP
  client connects the tools to a local Ollama model.

### Request Flow

1. A user asks the local AI assistant a question
2. Qwen3 selects an appropriate tool
3. The MCP client invokes the tool
4. MacroData MCP server
    - retrieves data from the World Bank API
    - then returns the structured economic data
5. Qwen 3 uses the resutls to generate an answer

- It's worth pinting out the MCP servr works independently of Ollama.


---

## Installation

### Pre-reqs

- Python 3.12 or newer
- Astral uv
- Node.js and npm (for MCP Inspector)

### Setup

Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/MacroDataMCP.git
cd MacroDataMCP
```

Install the project dependencies:

```bash
uv sync
```

### Run the MCP Server

Launch the MCP Inspector:

```bash
uv run mcp dev main.py
```

Open the local URL printed in your terminal.

The Inspector allows you to discover and test the
server's tools without requiring an LLM.

### Local AI Demo

Install Ollama and download Qwen3:

```bash
ollama pull qwen3:1.7b
```

Run the demonstration:

```bash
uv run python mcp_client_test.py
```

The Python client discovers the available MCP tools,
passes their definitions to Qwen3, executes requested
tool calls and returns the results to the model.

---

## MCP Tools

### 1. search_indicators(query)

Search World Development Indicators by name.

Example:

```json
{
  "query": "inflation"
}
```

Returns matching indicator codes, names and metadata.

### 2. get_indicator(country, indicator, start_year, end_year)

Retrieve an economic time series for one country.

Example:

```json
{
  "country": "GBR",
  "indicator": "NY.GDP.MKTP.KD.ZG",
  "start_year": 2020,
  "end_year": 2023
}
```

Returns country information, indicator metadata,
annual observations and source information.

### 3. compare_countries(countries, indicator, start_year, end_year)

Compare an economic indicator across multiple countries.

Example:

```json
{
  "countries": ["GBR", "FRA", "DEU"],
  "indicator": "FP.CPI.TOTL.ZG",
  "start_year": 2020,
  "end_year": 2023
}
```

Returns results for each successful country and
reports individual country errors.

A `partial` flag indicates whether any requests failed.

---

## Testing

Run the automated test suite:

```bash
uv run pytest -v
```

Tests use pytest and mocked dependencies to verify:

- Year-range validation
- Empty country-list validation
- HTTP error handling
- Missing economic observations
- Partial country failures
- Case-insensitive indicator searching

Tests run without requiring access to the World Bank API.

## Known Limitations

- Indicator search uses basic case-insensitive substring matching.
- The indicator catalogue is cached in memory without automatic expiration.
- Catalogue retrieval currently assumes all indicators fit on one API page.
- Country comparisons make sequential HTTP requests.
- Network failures may interrupt a comparison.
- Local LLMs can select incorrect tools or generate invalid arguments.
- Some World Bank observations are unavailable or revised over time.
- Remote deployment and authentication are not yet implemented.

## Data Source

Economic data is retrieved from the
[World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589).