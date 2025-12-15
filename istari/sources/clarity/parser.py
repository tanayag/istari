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

