"""Timeline management for event sequences."""

from datetime import datetime, timedelta
from typing import List, Optional
from istari.core.events import Event


class Timeline:
    """
    Manages a chronologically ordered sequence of events.
    
    Provides temporal analysis and pattern extraction capabilities.
    """
    
    def __init__(self, events: Optional[List[Event]] = None):
        """
        Initialize timeline with events.
        
        Args:
            events: List of events to initialize with (will be sorted by timestamp)
        """
        self._events: List[Event] = []
        if events:
            self.add_events(events)
    
    def add_event(self, event: Event):
        """Add a single event and maintain chronological order."""
        self._events.append(event)
        self._events.sort(key=lambda e: e.timestamp)
    
    def add_events(self, events: List[Event]):
        """Add multiple events and maintain chronological order."""
        self._events.extend(events)
        self._events.sort(key=lambda e: e.timestamp)
    
    def get_events(self) -> List[Event]:
        """Get all events in chronological order."""
        return self._events.copy()
    
    def get_events_in_range(
        self, 
        start: Optional[datetime] = None, 
        end: Optional[datetime] = None
    ) -> List[Event]:
        """
        Get events within a time range.
        
        Args:
            start: Start timestamp (inclusive)
            end: End timestamp (inclusive)
        
        Returns:
            List of events in the specified range
        """
        events = self._events
        
        if start:
            events = [e for e in events if e.timestamp >= start]
        if end:
            events = [e for e in events if e.timestamp <= end]
        
        return events
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type."""
        return [e for e in self._events if e.event_type == event_type]
    
    def get_duration(self) -> Optional[timedelta]:
        """
        Get the total duration of the timeline.
        
        Returns:
            Duration between first and last event, or None if < 2 events
        """
        if len(self._events) < 2:
            return None
        return self._events[-1].timestamp - self._events[0].timestamp
    
    def get_time_gaps(self) -> List[timedelta]:
        """
        Get time gaps between consecutive events.
        
        Returns:
            List of timedelta objects representing gaps
        """
        if len(self._events) < 2:
            return []
        
        gaps = []
        for i in range(1, len(self._events)):
            gap = self._events[i].timestamp - self._events[i-1].timestamp
            gaps.append(gap)
        
        return gaps
    
    def get_event_count(self) -> int:
        """Get total number of events."""
        return len(self._events)
    
    def is_empty(self) -> bool:
        """Check if timeline is empty."""
        return len(self._events) == 0

