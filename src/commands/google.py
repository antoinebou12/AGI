import json

from click import BaseCommand
from duckduckgo_search import ddg

from configs import Config

cfg = Config()


class GoogleCommand(BaseCommand):
    def execute(self):
        # Check if the Google API key is set and use the official search method
        # If the API key is not set or has only whitespaces, use the unofficial search method
        if cfg.google_api_key and (
            cfg.google_api_key.strip() if cfg.google_api_key else None
        ):
            return self.google_official_search(self.arguments["input"])
        else:
            return self.google_search(self.arguments["input"])

    def google_search(self, query, num_results=8):
        """Return the results of a google search"""
        search_results = list(ddg(query, max_results=num_results))
        return json.dumps(search_results, ensure_ascii=False, indent=4)

    def google_official_search(self, query, num_results=8):
        """Return the results of a google search using the official Google API"""
        import json

        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        try:
            # Get the Google API key and Custom Search Engine ID from the config file
            api_key = cfg.google_api_key
            custom_search_engine_id = cfg.custom_search_engine_id

            # Initialize the Custom Search API service
            service = build("customsearch", "v1", developerKey=api_key)

            # Send the search query and retrieve the results
            result = (
                service.cse()
                .list(q=query, cx=custom_search_engine_id, num=num_results)
                .execute()
            )

            # Extract the search result items from the response
            search_results = result.get("items", [])

            # Create a list of only the URLs from the search results
            search_results_links = [item["link"] for item in search_results]

        except HttpError as e:
            # Handle errors in the API call
            error_details = json.loads(e.content.decode())

            # Check if the error is related to an invalid or missing API key
            if error_details.get("error", {}).get(
                "code"
            ) == 403 and "invalid API key" in error_details.get("error", {}).get(
                "message", ""
            ):
                return "Error: The provided Google API key is invalid or missing."
            else:
                return f"Error: {e}"

        # Return the list of search result URLs
        return search_results_links
