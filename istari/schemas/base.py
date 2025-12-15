"""Base schema for event normalization."""

from typing import Dict, Any, Optional
from datetime import datetime
from istari.core.events import Event
from istari.exceptions import SchemaError


class BaseSchema:
    """Base class for event schema normalization."""
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """
        Normalize a raw event into the canonical Event format.
        
        Args:
            raw_event: Raw event data from source
        
        Returns:
            Normalized Event object
        
        Raises:
            SchemaError: If normalization fails
        """
        raise NotImplementedError("Subclasses must implement normalize()")
    
    def extract_timestamp(self, raw_event: Dict[str, Any]) -> datetime:
        """
        Extract timestamp from raw event.
        
        Args:
            raw_event: Raw event data
        
        Returns:
            Datetime object
        
        Raises:
            SchemaError: If timestamp cannot be extracted
        """
        # Try common timestamp fields
        for field in ["timestamp", "time", "created_at", "event_time", "ts"]:
            if field in raw_event:
                value = raw_event[field]
                if isinstance(value, datetime):
                    return value
                if isinstance(value, (int, float)):
                    # Unix timestamp
                    return datetime.fromtimestamp(value)
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        pass
        
        raise SchemaError("Could not extract timestamp from event")
    
    def extract_user_id(self, raw_event: Dict[str, Any]) -> str:
        """
        Extract user ID from raw event.
        
        Args:
            raw_event: Raw event data
        
        Returns:
            User ID string
        
        Raises:
            SchemaError: If user_id cannot be extracted
        """
        for field in ["user_id", "userId", "user", "distinct_id", "userId"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        raise SchemaError("Could not extract user_id from event")
    
    def extract_session_id(self, raw_event: Dict[str, Any]) -> str:
        """
        Extract session ID from raw event.
        
        Args:
            raw_event: Raw event data
        
        Returns:
            Session ID string
        
        Raises:
            SchemaError: If session_id cannot be extracted
        """
        for field in ["session_id", "sessionId", "session", "session_id"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        # Generate session ID from user_id + timestamp if not present
        user_id = self.extract_user_id(raw_event)
        timestamp = self.extract_timestamp(raw_event)
        return f"{user_id}_{int(timestamp.timestamp())}"
    
    def extract_event_type(self, raw_event: Dict[str, Any]) -> str:
        """
        Extract event type from raw event.
        
        Args:
            raw_event: Raw event data
        
        Returns:
            Event type string
        
        Raises:
            SchemaError: If event_type cannot be extracted
        """
        for field in ["event", "event_type", "eventType", "name", "action"]:
            if field in raw_event:
                value = raw_event[field]
                if value:
                    return str(value)
        
        raise SchemaError("Could not extract event_type from event")
    
    def extract_properties(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract properties from raw event.
        
        Args:
            raw_event: Raw event data
        
        Returns:
            Dictionary of properties
        """
        # Common property fields
        for field in ["properties", "props", "attributes", "data", "context"]:
            if field in raw_event and isinstance(raw_event[field], dict):
                return raw_event[field].copy()
        
        # If no properties field, return all non-standard fields
        standard_fields = {
            "timestamp", "time", "created_at", "event_time", "ts",
            "user_id", "userId", "user", "distinct_id",
            "session_id", "sessionId", "session",
            "event", "event_type", "eventType", "name", "action",
            "properties", "props", "attributes", "data", "context",
        }
        
        properties = {}
        for key, value in raw_event.items():
            if key not in standard_fields:
                properties[key] = value
        
        return properties

