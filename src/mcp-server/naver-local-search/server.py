import os
import sys
import json
from dotenv import load_dotenv
import requests

# Use loguru for logging
from loguru import logger

# MCP Imports for FastMCP style
from mcp.server.fastmcp import FastMCP

# --- Configuration ---
NAVER_API_URL = "https://openapi.naver.com/v1/search/local.json"

# --- Logging Setup with Loguru ---
logger.remove()
logger.add(sys.stderr, format="{time} - {level} - {message}", level="INFO")

# --- FastMCP Server Definition ---
mcp = FastMCP("NaverMapSearch")


# --- Tool Definition using Decorator ---
@mcp.tool()
def search_naver_places(
    query: str, max_results: int = 5, sort_by: str = "reviews"
) -> list[dict[str, any]]:
    """
    Searches Naver Map for places (like restaurants, cafes) based on a query.
    Can prioritize popular places based on review counts ('reviews') or relevance ('accuracy').
    """
    logger.info(
        f"Executing search_naver_places: query='{query}', max_results={max_results}, sort_by='{sort_by}'"
    )

    # Access credentials inside the function
    naver_client_id = os.environ.get("X-NAVER-CLIENT-ID")
    naver_client_secret = os.environ.get("X-NAVER-CLIENT-SECRET")

    if not naver_client_id or not naver_client_secret:
        logger.error(
            "Naver API credentials (NAVER_CLIENT_ID, NAVER_CLIENT_SECRET) not found in environment."
        )
        return [{"error": "Server configuration error: Missing Naver API credentials."}]

    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret,
    }

    display = max(1, min(max_results if max_results is not None else 5, 5))
    sort_option = "comment" if sort_by == "reviews" else "random"

    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": sort_option,
    }

    try:
        response = requests.get(
            NAVER_API_URL, headers=headers, params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        logger.info(f"Received {len(data.get('items', []))} items from Naver API.")

        results: list[dict[str, any]] = []
        for item in data.get("items", []):
            title = item.get("title", "").replace("<b>", "").replace("</b>", "")
            results.append(
                {
                    "name": title,
                    "category": item.get("category", ""),
                    "address": item.get("address", ""),
                    "road_address": item.get("roadAddress", ""),
                }
            )
        return results if results else []

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Naver API: {e}")
        return [{"error": f"Failed to contact Naver API: {e}"}]
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding Naver API response: {e}")
        return [{"error": "Invalid response format from Naver API."}]
    except Exception:
        logger.exception("An unexpected error occurred during Naver API call")
        return [{"error": "An internal server error occurred processing the request."}]


# --- Main Execution ---
if __name__ == "__main__":
    load_dotenv()

    logger.info("Starting Naver Map MCP Server (FastMCP) via STDIO...")

    if not os.environ.get("X-NAVER-CLIENT-ID") or not os.environ.get(
        "X-NAVER-CLIENT-SECRET"
    ):
        logger.error(
            "CRITICAL: Naver API credentials (X-NAVER-CLIENT-ID, X-NAVER-CLIENT-SECRET) "
            "not provided in environment. Exiting."
        )
        sys.exit(1)

    mcp.run()

    logger.info("Naver Map MCP Server stopped.")
