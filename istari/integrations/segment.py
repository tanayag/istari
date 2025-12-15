"""Segment integration."""

from typing import List, Dict, Any
from istari.schemas.base import BaseSchema
from istari.core.events import Event
from istari.integrations.generic import GenericIntegration


class SegmentSchema(BaseSchema):
    """Schema for Segment events."""
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """Normalize Segment event."""
        # Segment format: {type, userId, timestamp, event, properties, ...}
        event_type = raw_event.get("event") or raw_event.get("type")
        user_id = raw_event.get("userId") or raw_event.get("user_id")
        timestamp = self.extract_timestamp(raw_event)
        
        # Extract session ID
        session_id = raw_event.get("sessionId") or raw_event.get("session_id")
        if not session_id:
            # Segment often uses anonymousId + timestamp
            anonymous_id = raw_event.get("anonymousId")
            if anonymous_id:
                session_id = f"{anonymous_id}_{int(timestamp.timestamp())}"
            else:
                session_id = self.extract_session_id(raw_event)
        
        # Combine properties and context
        properties = raw_event.get("properties", {})
        context = raw_event.get("context", {})
        properties.update(context)
        
        return Event(
            event_type=event_type or "unknown",
            timestamp=timestamp,
            user_id=str(user_id),
            session_id=str(session_id),
            properties=properties,
            source="segment",
            raw_data=raw_event,
        )


class SegmentIntegration(GenericIntegration):
    """Integration for Segment analytics."""
    
    def __init__(self):
        """Initialize Segment integration."""
        super().__init__(schema=SegmentSchema())
    
    def import_from_segment(self, segment_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Import events from Segment format.
        
        Args:
            segment_events: List of Segment event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        return self.normalize_events(segment_events)

