"""Mixpanel integration."""

from typing import List, Dict, Any
from istari.schemas.base import BaseSchema
from istari.core.events import Event
from istari.integrations.generic import GenericIntegration


class MixpanelSchema(BaseSchema):
    """Schema for Mixpanel events."""
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """Normalize Mixpanel event."""
        # Mixpanel format: {event, properties: {time, distinct_id, ...}}
        event_type = raw_event.get("event") or raw_event.get("event_type")
        properties = raw_event.get("properties", {})
        
        # Extract timestamp (Mixpanel uses Unix timestamp in properties)
        timestamp = self.extract_timestamp({**raw_event, **properties})
        
        # Extract user ID (Mixpanel uses distinct_id)
        user_id = properties.get("distinct_id") or properties.get("user_id")
        if not user_id:
            user_id = self.extract_user_id(raw_event)
        
        # Extract session ID
        session_id = properties.get("session_id") or properties.get("$session_id")
        if not session_id:
            session_id = self.extract_session_id({**raw_event, **properties})
        
        return Event(
            event_type=event_type or "unknown",
            timestamp=timestamp,
            user_id=str(user_id),
            session_id=str(session_id),
            properties=properties,
            source="mixpanel",
            raw_data=raw_event,
        )


class MixpanelIntegration(GenericIntegration):
    """Integration for Mixpanel analytics."""
    
    def __init__(self):
        """Initialize Mixpanel integration."""
        super().__init__(schema=MixpanelSchema())
    
    def import_from_mixpanel(self, mixpanel_events: List[Dict[str, Any]]) -> List[Event]:
        """
        Import events from Mixpanel format.
        
        Args:
            mixpanel_events: List of Mixpanel event dictionaries
        
        Returns:
            List of normalized Event objects
        """
        return self.normalize_events(mixpanel_events)

