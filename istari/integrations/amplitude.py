"""Amplitude integration."""

from typing import List, Dict, Any
from istari.schemas.base import BaseSchema
from istari.core.events import Event
from istari.integrations.generic import GenericIntegration


class AmplitudeSchema(BaseSchema):
    """Schema for Amplitude events."""
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """Normalize Amplitude event."""
        # Amplitude format: {event_type, user_id, time, event_properties, ...}
        event_type = raw_event.get("event_type") or raw_event.get("event")
        user_id = raw_event.get("user_id") or raw_event.get("user")
        timestamp = self.extract_timestamp(raw_event)
        
        # Extract session ID
        session_id = raw_event.get("session_id") or raw_event.get("session")
        if not session_id:
            session_id = self.extract_session_id(raw_event)
        
        # Combine event properties
        properties = raw_event.get("event_properties", {})
        properties.update({k: v for k, v in raw_event.items() 
                          if k not in ["event_type", "event", "user_id", "user", 
                                       "time", "timestamp", "session_id", "session",
                                       "event_properties"]})
        
        return Event(
            event_type=event_type or "unknown",
            timestamp=timestamp,
            user_id=str(user_id),
            session_id=str(session_id),
            properties=properties,
            source="amplitude",
            raw_data=raw_event,
        )


class AmplitudeIntegration(GenericIntegration):
    """Integration for Amplitude analytics."""
    
    def __init__(self):
        """Initialize Amplitude integration."""
        super().__init__(schema=AmplitudeSchema())
    
    def import_from_amplitude(self, amplitude_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Import events from Amplitude format.
        
        Args:
            amplitude_events: List of Amplitude event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        return self.normalize_events(amplitude_events)

