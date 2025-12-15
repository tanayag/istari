"""Generic integration for any analytics platform."""

from typing import List, Dict, Any, Optional
from istari.schemas.base import BaseSchema
from istari.core.events import Event
from istari.exceptions import IntegrationError


class GenericIntegration:
    """Generic integration that works with any event format."""
    
    def __init__(self, schema: Optional[BaseSchema] = None):
        """
        Initialize generic integration.
        
        Args:
            schema: Schema to use for normalization (defaults to BaseSchema)
        """
        self.schema = schema or BaseSchema()
    
    def normalize_events(self, raw_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Normalize raw events into canonical format.
        
        Args:
            raw_events: List of raw event dictionaries
        
        Returns:
            List of normalized Event objects
        
        Raises:
            IntegrationError: If normalization fails
        """
        normalized = []
        
        for raw_event in raw_events:
            try:
                event = self.schema.normalize(raw_event)
                normalized.append(event)
            except Exception as e:
                raise IntegrationError(f"Failed to normalize event: {e}") from e
        
        return normalized
    
    def stream_events(self, event_source, callback):
        """
        Stream events from a source and call callback for each normalized event.
        
        Args:
            event_source: Source of events (iterable)
            callback: Function to call with each normalized Event
        """
        for raw_event in event_source:
            try:
                event = self.schema.normalize(raw_event)
                callback(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Failed to normalize event: {e}")

