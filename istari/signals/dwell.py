"""Dwell time signal extraction."""

from typing import List, Dict, Any
from datetime import timedelta
from istari.core.session import Session
from istari.core.events import Event


class DwellSignal:
    """Extracts dwell time signals from sessions."""
    
    def __init__(self, min_dwell_seconds: float = 5.0):
        """
        Initialize dwell signal extractor.
        
        Args:
            min_dwell_seconds: Minimum dwell time to consider significant
        """
        self.min_dwell_seconds = min_dwell_seconds
    
    def extract(self, session: Session) -> Dict[str, Any]:
        """
        Extract dwell time signals.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary with dwell time metrics
        """
        events = session.timeline.get_events()
        
        if len(events) < 2:
            return {
                "total_dwell_seconds": 0.0,
                "avg_dwell_seconds": 0.0,
                "max_dwell_seconds": 0.0,
                "long_dwell_count": 0,
            }
        
        # Calculate dwell times between events
        dwell_times = []
        for i in range(1, len(events)):
            gap = (events[i].timestamp - events[i-1].timestamp).total_seconds()
            dwell_times.append(gap)
        
        total_dwell = sum(dwell_times)
        avg_dwell = total_dwell / len(dwell_times) if dwell_times else 0.0
        max_dwell = max(dwell_times) if dwell_times else 0.0
        long_dwell_count = len([d for d in dwell_times if d >= self.min_dwell_seconds])
        
        return {
            "total_dwell_seconds": total_dwell,
            "avg_dwell_seconds": avg_dwell,
            "max_dwell_seconds": max_dwell,
            "long_dwell_count": long_dwell_count,
        }
    
    def get_page_dwell_times(self, session: Session) -> Dict[str, float]:
        """
        Get dwell times per page.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary mapping page names to dwell times in seconds
        """
        events = session.timeline.get_events()
        page_dwells = {}
        
        page_view_events = [e for e in events if e.event_type == "page_view"]
        
        for i in range(len(page_view_events)):
            current_page = page_view_events[i].properties.get("page", "unknown")
            
            if i < len(page_view_events) - 1:
                next_page_time = page_view_events[i + 1].timestamp
                dwell_time = (next_page_time - page_view_events[i].timestamp).total_seconds()
            else:
                # Last page - use session end or last event
                last_event = events[-1] if events else page_view_events[i]
                dwell_time = (last_event.timestamp - page_view_events[i].timestamp).total_seconds()
            
            if current_page not in page_dwells:
                page_dwells[current_page] = 0.0
            page_dwells[current_page] += dwell_time
        
        return page_dwells

