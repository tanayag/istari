"""API client for Microsoft Clarity Data Export API."""

import time
from typing import Dict, Any, Iterator, Optional, List
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import urllib.parse
import json
from istari.exceptions import IntegrationError


class ClarityAPIError(IntegrationError):
    """Raised when Clarity API operations fail."""
    pass


class ClarityAuthenticationError(ClarityAPIError):
    """Raised when Clarity API authentication fails."""
    pass


class ClarityRateLimitError(ClarityAPIError):
    """Raised when Clarity API rate limit is exceeded."""
    pass


class ClarityAPIClient:
    """
    Client for Microsoft Clarity Data Export API.
    
    Documentation: https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api
    
    Authentication: Bearer token in Authorization header
    Endpoint: https://www.clarity.ms/export-data/api/v1/project-live-insights
    """
    
    BASE_URL = "https://www.clarity.ms/export-data/api/v1"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Clarity API client.
        
        Args:
            api_key: Clarity API access token (Bearer token)
            base_url: Base URL for API (defaults to official endpoint)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def fetch_live_insights(
        self,
        project_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch live insights from Clarity API.
        
        Args:
            project_id: Clarity project ID (optional, may be inferred from token)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            **kwargs: Additional query parameters
        
        Yields:
            Dictionary containing insight data
        
        Raises:
            ClarityAuthenticationError: If authentication fails
            ClarityRateLimitError: If rate limit is exceeded
            ClarityAPIError: For other API errors
        """
        endpoint = f"{self.base_url}/project-live-insights"
        
        # Build query parameters
        params = {}
        if project_id:
            params["projectId"] = project_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        params.update(kwargs)
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                response_data = self._make_request(endpoint, params)
                
                # Handle pagination if response contains multiple pages
                if isinstance(response_data, dict):
                    # Check if response has pagination structure
                    if "data" in response_data:
                        data = response_data["data"]
                        if isinstance(data, list):
                            for item in data:
                                yield item
                        else:
                            yield data
                    elif "insights" in response_data:
                        insights = response_data["insights"]
                        if isinstance(insights, list):
                            for insight in insights:
                                yield insight
                        else:
                            yield insights
                    else:
                        # Single object response
                        yield response_data
                elif isinstance(response_data, list):
                    # Direct list response
                    for item in response_data:
                        yield item
                else:
                    yield response_data
                
                return  # Success, exit retry loop
                
            except ClarityRateLimitError:
                if attempt < self.max_retries - 1:
                    # Exponential backoff for rate limits
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                raise
            except ClarityAPIError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Clarity API.
        
        Args:
            endpoint: API endpoint URL
            params: Query parameters
        
        Returns:
            JSON response as dictionary
        
        Raises:
            ClarityAuthenticationError: If authentication fails (401)
            ClarityRateLimitError: If rate limit exceeded (429)
            ClarityAPIError: For other HTTP errors
        """
        # Build URL with query parameters
        url = endpoint
        if params:
            query_string = "&".join([
                f"{key}={urllib.parse.quote(str(value))}"
                for key, value in params.items()
                if value is not None
            ])
            if query_string:
                url = f"{endpoint}?{query_string}"
        
        # Create request with authentication header
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Istari/0.1.0")
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    response_text = response.read().decode('utf-8')
                    return json.loads(response_text)
                else:
                    self._handle_error_response(response)
        except urllib.error.HTTPError as e:
            self._handle_error_response(e)
        except urllib.error.URLError as e:
            raise ClarityAPIError(f"Network error: {e}") from e
        except json.JSONDecodeError as e:
            raise ClarityAPIError(f"Invalid JSON response: {e}") from e
        except Exception as e:
            raise ClarityAPIError(f"Unexpected error: {e}") from e
    
    def _handle_error_response(self, response: Any):
        """
        Handle error responses from API.
        
        Args:
            response: HTTP response object or HTTPError
        
        Raises:
            ClarityAuthenticationError: For 401 errors
            ClarityRateLimitError: For 429 errors
            ClarityAPIError: For other errors
        """
        status_code = getattr(response, 'code', getattr(response, 'status', None))
        
        if status_code == 401:
            raise ClarityAuthenticationError(
                "Authentication failed. Please check your API key."
            )
        elif status_code == 403:
            raise ClarityAuthenticationError(
                "Access forbidden. Please check your API key permissions."
            )
        elif status_code == 429:
            raise ClarityRateLimitError(
                "Rate limit exceeded. Please wait before retrying."
            )
        elif status_code == 404:
            raise ClarityAPIError(
                "Endpoint not found. Please check the API endpoint URL."
            )
        else:
            error_msg = f"API request failed with status {status_code}"
            try:
                error_body = response.read().decode('utf-8')
                error_data = json.loads(error_body)
                if "message" in error_data:
                    error_msg = error_data["message"]
                elif "error" in error_data:
                    error_msg = error_data["error"]
            except:
                pass
            
            raise ClarityAPIError(error_msg)
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            True if connection successful
        
        Raises:
            ClarityAPIError: If connection fails
        """
        try:
            # Try to fetch insights (may return empty if no data)
            list(self.fetch_live_insights())
            return True
        except ClarityAuthenticationError:
            raise
        except ClarityAPIError as e:
            # Other errors might be acceptable (e.g., no data)
            return True

