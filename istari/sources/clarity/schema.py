"""Clarity-specific event schema definitions."""

from typing import Dict, Any, Optional
from datetime import datetime
from istari.schemas.base import BaseSchema
from istari.core.events import Event


class ClaritySchema(BaseSchema):
    """
    Schema for Microsoft Clarity events.
    
    Clarity provides behavioral signals like rage clicks, dead clicks,
    scroll depth, navigation patterns, etc.
    """
    
    # Clarity event types
    EVENT_TYPES = {
        "rage_click": "rage_click",
        "dead_click": "dead_click",
        "scroll": "scroll",
        "navigation": "navigation",
        "hover": "hover",
        "click": "click",
        "session": "session",
        "page_view": "page_view",
    }
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """
        Normalize Clarity event into canonical format.
        
        Args:
            raw_event: Raw Clarity event data
        
        Returns:
            Normalized Event object
        """
        timestamp = self.extract_timestamp(raw_event)
        user_id = self.extract_user_id(raw_event)
        session_id = self.extract_session_id(raw_event)
        event_type = self.extract_event_type(raw_event)
        properties = self.extract_properties(raw_event)
        
        # Normalize event type
        event_type = self.EVENT_TYPES.get(event_type, event_type)
        
        return Event(
            event_type=event_type,
            timestamp=timestamp,
            user_id=user_id,
            session_id=session_id,
            properties=properties,
            source="clarity",
            raw_data=raw_event,
        )
    
    def extract_timestamp(self, raw_event: Dict[str, Any]) -> datetime:
        """Extract timestamp from Clarity event."""
        # Clarity uses various timestamp fields
        for field in ["timestamp", "time", "createdAt", "created_at", "ts"]:
            if field in raw_event:
                value = raw_event[field]
                if isinstance(value, datetime):
                    return value
                if isinstance(value, (int, float)):
                    return datetime.fromtimestamp(value / 1000 if value > 1e10 else value)
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        pass
        
        # Fallback to current time if not found
        return datetime.utcnow()
    
    def extract_user_id(self, raw_event: Dict[str, Any]) -> str:
        """Extract user ID from Clarity event."""
        for field in ["userId", "user_id", "user", "visitorId", "visitor_id"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        # Clarity may use session-based identification
        session_id = raw_event.get("sessionId") or raw_event.get("session_id")
        if session_id:
            return f"clarity_session_{session_id}"
        
        return "clarity_anonymous"
    
    def extract_session_id(self, raw_event: Dict[str, Any]) -> str:
        """Extract session ID from Clarity event."""
        for field in ["sessionId", "session_id", "session"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        # Generate from user_id + timestamp if not present
        user_id = self.extract_user_id(raw_event)
        timestamp = self.extract_timestamp(raw_event)
        return f"{user_id}_{int(timestamp.timestamp())}"
    
    def extract_event_type(self, raw_event: Dict[str, Any]) -> str:
        """Extract event type from Clarity event."""
        for field in ["event", "eventType", "event_type", "type", "action"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        return "unknown"
    
    def extract_clarity_specific_fields(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract Clarity-specific fields.
        
        Returns:
            Dictionary of Clarity-specific properties
        """
        clarity_fields = {}
        
        # Rage click fields
        event_type = self.extract_event_type(raw_event)
        if event_type == "rage_click" or "rageClick" in raw_event or "rage_click" in raw_event:
            clarity_fields["is_rage_click"] = True
            clarity_fields["click_count"] = raw_event.get("clickCount") or raw_event.get("click_count", 0)
        
        # Dead click fields
        if event_type == "dead_click" or "deadClick" in raw_event or "dead_click" in raw_event:
            clarity_fields["is_dead_click"] = True
        
        # Scroll depth
        if "scrollDepth" in raw_event or "scroll_depth" in raw_event:
            clarity_fields["scroll_depth"] = raw_event.get("scrollDepth") or raw_event.get("scroll_depth")
        
        # Hover duration
        if "hoverDuration" in raw_event or "hover_duration" in raw_event:
            clarity_fields["hover_duration"] = raw_event.get("hoverDuration") or raw_event.get("hover_duration")
        
        # Navigation timing
        if "navigationTiming" in raw_event or "navigation_timing" in raw_event:
            clarity_fields["navigation_timing"] = raw_event.get("navigationTiming") or raw_event.get("navigation_timing")
        
        # Page information
        if "url" in raw_event:
            clarity_fields["url"] = raw_event["url"]
        if "path" in raw_event:
            clarity_fields["path"] = raw_event["path"]
        
        return clarity_fields

