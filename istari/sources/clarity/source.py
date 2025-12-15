"""Clarity event source implementation."""

from typing import List, Dict, Any, Iterator, Optional
from istari.sources.base import BaseEventSource
from istari.sources.clarity.parser import ClarityParser
from istari.sources.clarity.mapper import ClarityMapper
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

