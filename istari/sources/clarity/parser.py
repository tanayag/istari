"""Parser for Clarity event exports."""

from typing import List, Dict, Any, Optional, Iterator
from istari.sources.clarity.schema import ClaritySchema
from istari.core.events import Event
from istari.exceptions import IntegrationError


class ClarityParser:
    """
    Parser for Microsoft Clarity event exports.
    
    Handles conversion of Clarity raw events/exports into Istari canonical events.
    No SDK coupling required - works with exported data.
    """
    
    def __init__(self, schema: Optional[ClaritySchema] = None):
        """
        Initialize Clarity parser.
        
        Args:
            schema: Clarity schema instance (defaults to new instance)
        """
        self.schema = schema or ClaritySchema()
    
    def parse(self, raw_event: Dict[str, Any]) -> Event:
        """
        Parse a single Clarity event.
        
        Args:
            raw_event: Raw Clarity event dictionary
        
        Returns:
            Normalized Event object
        
        Raises:
            IntegrationError: If parsing fails
        """
        try:
            # Extract Clarity-specific fields and merge into properties
            clarity_fields = self.schema.extract_clarity_specific_fields(raw_event)
            
            # Normalize to canonical event
            event = self.schema.normalize(raw_event)
            
            # Merge Clarity-specific fields into properties
            event.properties.update(clarity_fields)
            
            return event
        except Exception as e:
            raise IntegrationError(f"Failed to parse Clarity event: {e}") from e
    
    def parse_batch(self, raw_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Parse multiple Clarity events.
        
        Args:
            raw_events: List of raw Clarity event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        return [self.parse(raw_event) for raw_event in raw_events]
    
    def parse_export(self, export_data: Dict[str, Any]) -> List[Event]:
        """
        Parse a Clarity export file/data structure.
        
        Args:
            export_data: Clarity export data (may contain events array, etc.)
        
        Returns:
            List of normalized Event objects
        """
        # Handle different export formats
        if "events" in export_data:
            events = export_data["events"]
        elif "data" in export_data:
            events = export_data["data"]
        elif isinstance(export_data, list):
            events = export_data
        else:
            # Single event
            return [self.parse(export_data)]
        
        return self.parse_batch(events)
    
    def parse_insight(self, insight: Dict[str, Any]) -> List[Event]:
        """
        Parse a Clarity API insight (aggregated metric) into events.
        
        Clarity API returns aggregated insights like:
        {
            "metricName": "DeadClickCount",
            "information": [{"sessionsCount": "2", ...}]
        }
        
        This method transforms insights into individual events.
        
        Args:
            insight: Clarity insight dictionary
        
        Returns:
            List of normalized Event objects
        """
        from datetime import datetime, timezone
        
        metric_name = insight.get("metricName", "unknown")
        information = insight.get("information", [])
        
        events = []
        
        # Map metric names to event types
        metric_to_event_type = {
            "DeadClickCount": "dead_click",
            "RageClickCount": "rage_click",
            "ScrollDepth": "scroll",
            "QuickBackCount": "navigation",
            "HoverDuration": "hover",
        }
        
        event_type = metric_to_event_type.get(metric_name, metric_name.lower())
        
        # Create events from information array
        for info in information:
            # Create a synthetic event from the aggregated data
            event_data = {
                "event": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metricName": metric_name,
                "sessionsCount": info.get("sessionsCount", "0"),
                "pagesViews": info.get("pagesViews", "0"),
                "sessionsWithMetricPercentage": info.get("sessionsWithMetricPercentage", 0),
                "sessionsWithoutMetricPercentage": info.get("sessionsWithoutMetricPercentage", 0),
                "subTotal": info.get("subTotal", "0"),
            }
            
            # Add any additional fields from info
            for key, value in info.items():
                if key not in event_data:
                    event_data[key] = value
            
            events.append(self.parse(event_data))
        
        return events
    
    def stream_parse(self, event_iterator: Iterator[Dict[str, Any]]) -> Iterator[Event]:
        """
        Stream parse events from an iterator.
        
        Args:
            event_iterator: Iterator yielding raw Clarity event dictionaries
        
        Yields:
            Normalized Event objects
        """
        for raw_event in event_iterator:
            try:
                yield self.parse(raw_event)
            except Exception as e:
                # Log but continue processing
                print(f"Warning: Failed to parse Clarity event: {e}")
                continue

