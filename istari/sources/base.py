"""Base classes for event sources."""

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional, Dict, Any
from istari.core.events import Event
from istari.exceptions import IntegrationError


class EventSource(ABC):
    """
    Abstract base class for event sources.
    
    Event sources are responsible for ingesting raw events from external
    systems and converting them into Istari's canonical event format.
    """
    
    @abstractmethod
    def parse(self, raw_data: Dict[str, Any]) -> Event:
        """
        Parse a single raw event into Istari canonical format.
        
        Args:
            raw_data: Raw event data from source
        
        Returns:
            Normalized Event object
        
        Raises:
            IntegrationError: If parsing fails
        """
        pass
    
    @abstractmethod
    def parse_batch(self, raw_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Parse multiple raw events.
        
        Args:
            raw_events: List of raw event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        pass
    
    def stream(self, event_iterator: Iterator[Dict[str, Any]]) -> Iterator[Event]:
        """
        Stream events from an iterator.
        
        Args:
            event_iterator: Iterator yielding raw event dictionaries
        
        Yields:
            Normalized Event objects
        """
        for raw_event in event_iterator:
            try:
                yield self.parse(raw_event)
            except Exception as e:
                raise IntegrationError(f"Failed to parse event: {e}") from e


class BaseEventSource(EventSource):
    """
    Base implementation of EventSource with common functionality.
    
    Subclasses should implement parse() and optionally override parse_batch()
    for better performance.
    """
    
    def __init__(self, source_name: str):
        """
        Initialize base event source.
        
        Args:
            source_name: Name of the event source (e.g., "clarity", "mixpanel")
        """
        self.source_name = source_name
    
    def parse_batch(self, raw_events: List[Dict[str, Any]]) -> List[Event]:
        """Parse multiple events by calling parse() on each."""
        return [self.parse(raw_event) for raw_event in raw_events]

