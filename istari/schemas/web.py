"""Web-specific event schemas."""

from typing import Dict, Any, Optional
from istari.schemas.base import BaseSchema
from istari.core.events import Event


class WebSchema(BaseSchema):
    """Schema for web events."""
    
    # Common web event types
    EVENT_TYPES = {
        "page_view": "page_view",
        "page_leave": "page_leave",
        "click": "click",
        "scroll": "scroll",
        "form_submit": "form_submit",
        "form_start": "form_start",
        "link_click": "link_click",
        "button_click": "button_click",
    }
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """Normalize web event."""
        timestamp = self.extract_timestamp(raw_event)
        user_id = self.extract_user_id(raw_event)
        session_id = self.extract_session_id(raw_event)
        event_type = self.extract_event_type(raw_event)
        properties = self.extract_properties(raw_event)
        
        # Normalize event type if needed
        event_type = self.EVENT_TYPES.get(event_type, event_type)
        
        return Event(
            event_type=event_type,
            timestamp=timestamp,
            user_id=user_id,
            session_id=session_id,
            properties=properties,
            source="web",
            raw_data=raw_event,
        )
    
    def extract_page_info(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract page information from event."""
        properties = self.extract_properties(raw_event)
        
        page_info = {}
        for key in ["page", "page_name", "pageName", "path", "url"]:
            if key in properties:
                page_info["page"] = properties[key]
                break
        
        for key in ["referrer", "referer", "referrer_url"]:
            if key in properties:
                page_info["referrer"] = properties[key]
                break
        
        return page_info
    
    def extract_scroll_depth(self, raw_event: Dict[str, Any]) -> Optional[float]:
        """Extract scroll depth percentage from event."""
        properties = self.extract_properties(raw_event)
        
        for key in ["scroll_depth", "scrollDepth", "scroll_percent", "scrollPercent"]:
            if key in properties:
                value = properties[key]
                if isinstance(value, (int, float)):
                    return float(value)
        
        return None

