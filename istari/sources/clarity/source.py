"""Clarity event source implementation."""

from typing import List, Dict, Any, Iterator, Optional
from datetime import datetime, timedelta
from istari.sources.base import BaseEventSource
from istari.sources.clarity.parser import ClarityParser
from istari.sources.clarity.mapper import ClarityMapper
from istari.sources.clarity.api_client import (
    ClarityAPIClient,
    ClarityAPIError,
    ClarityAuthenticationError,
)
from istari.core.events import Event


class ClaritySource(BaseEventSource):
    """
    Microsoft Clarity event source.
    
    Ingests Clarity events/exports and converts them to Istari canonical format.
    Also provides signal mapping from Clarity behavioral signals to Istari signals.
    """
    
    def __init__(self):
        """Initialize Clarity source."""
        super().__init__(source_name="clarity")
        self.parser = ClarityParser()
        self.mapper = ClarityMapper()
    
    def parse(self, raw_data: Dict[str, Any]) -> Event:
        """
        Parse a single Clarity event.
        
        Args:
            raw_data: Raw Clarity event data
        
        Returns:
            Normalized Event object
        """
        return self.parser.parse(raw_data)
    
    def parse_batch(self, raw_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Parse multiple Clarity events.
        
        Args:
            raw_events: List of raw Clarity event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        return self.parser.parse_batch(raw_events)
    
    def parse_export(self, export_data: Dict[str, Any]) -> List[Event]:
        """
        Parse a Clarity export.
        
        Args:
            export_data: Clarity export data structure
        
        Returns:
            List of normalized Event objects
        """
        return self.parser.parse_export(export_data)
    
    def map_to_signals(self, events: List[Event]) -> Dict[str, Any]:
        """
        Map Clarity events to Istari signal categories.
        
        Args:
            events: List of normalized Clarity events
        
        Returns:
            Dictionary mapping Istari signal categories to values
        """
        return self.mapper.map_batch(events)
    
    def process(self, raw_data: List[Dict[str, Any]]) -> tuple[List[Event], Dict[str, Any]]:
        """
        Process raw Clarity data: parse events and extract signals.
        
        Args:
            raw_data: List of raw Clarity event dictionaries
        
        Returns:
            Tuple of (normalized_events, signal_mappings)
        """
        events = self.parse_batch(raw_data)
        signals = self.map_to_signals(events)
        
        return events, signals
    
    def stream(self, event_iterator: Iterator[Dict[str, Any]]) -> Iterator[Event]:
        """
        Stream parse events from an iterator.
        
        Args:
            event_iterator: Iterator yielding raw Clarity event dictionaries
        
        Yields:
            Normalized Event objects
        """
        return self.parser.stream_parse(event_iterator)
    
    def fetch_from_api(
        self,
        api_key: str,
        project_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch data directly from Clarity API.
        
        Args:
            api_key: Clarity API access token
            project_id: Clarity project ID (optional)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            **kwargs: Additional API parameters
        
        Yields:
            Raw Clarity insight data dictionaries
        
        Raises:
            ClarityAuthenticationError: If authentication fails
            ClarityAPIError: For other API errors
        
        Example:
            >>> source = ClaritySource()
            >>> for insight in source.fetch_from_api(
            ...     api_key="your-api-key",
            ...     project_id="project-123",
            ...     start_date="2024-01-01",
            ...     end_date="2024-01-31"
            ... ):
            ...     print(insight)
        """
        client = ClarityAPIClient(api_key=api_key)
        return client.fetch_live_insights(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
    
    def import_from_api(
        self,
        api_key: str,
        project_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> tuple[List[Event], Dict[str, Any]]:
        """
        Fetch data from Clarity API, parse, and extract signals.
        
        This is a convenience method that combines fetch_from_api, parsing, and mapping.
        
        Args:
            api_key: Clarity API access token
            project_id: Clarity project ID (optional)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            **kwargs: Additional API parameters
        
        Returns:
            Tuple of (normalized_events, signal_mappings)
        
        Raises:
            ClarityAuthenticationError: If authentication fails
            ClarityAPIError: For other API errors
        
        Example:
            >>> source = ClaritySource()
            >>> events, signals = source.import_from_api(
            ...     api_key="your-api-key",
            ...     project_id="project-123",
            ...     start_date="2024-01-01"
            ... )
            >>> print(f"Imported {len(events)} events")
            >>> print(f"Signals: {signals}")
        """
        # Fetch raw data from API
        raw_insights = list(self.fetch_from_api(
            api_key=api_key,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        ))
        
        if not raw_insights:
            return [], {}
        
        # Parse insights into events
        # Clarity API returns aggregated insights, not individual events
        # We need to transform them using parse_insight
        events = []
        for insight in raw_insights:
            if isinstance(insight, dict):
                # Check if this is an aggregated insight (has metricName)
                if "metricName" in insight:
                    # Parse as insight (aggregated metric)
                    insight_events = self.parser.parse_insight(insight)
                    events.extend(insight_events)
                else:
                    # Parse as regular event
                    events.append(self.parse(insight))
            elif isinstance(insight, list):
                # Handle list of insights
                for item in insight:
                    if isinstance(item, dict) and "metricName" in item:
                        insight_events = self.parser.parse_insight(item)
                        events.extend(insight_events)
                    else:
                        events.append(self.parse(item))
        
        # Extract signals
        signals = self.map_to_signals(events)
        
        return events, signals

