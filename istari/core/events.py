"""Event normalization and canonical schema."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from istari.exceptions import EventValidationError


@dataclass
class Event:
    """
    Canonical event representation.
    
    All raw events are normalized into this schema before processing.
    """
    event_type: str
    timestamp: datetime
    user_id: str
    session_id: str
    
    # Contextual properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    source: Optional[str] = None  # e.g., "mixpanel", "amplitude", "custom"
    raw_data: Optional[Dict[str, Any]] = None  # Original event data
    
    def __post_init__(self):
        """Validate event after initialization."""
        if not self.event_type:
            raise EventValidationError("event_type cannot be empty")
        if not self.user_id:
            raise EventValidationError("user_id cannot be empty")
        if not self.session_id:
            raise EventValidationError("session_id cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "properties": self.properties,
            "source": self.source,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary."""
        timestamp = data["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        return cls(
            event_type=data["event_type"],
            timestamp=timestamp,
            user_id=data["user_id"],
            session_id=data["session_id"],
            properties=data.get("properties", {}),
            source=data.get("source"),
            raw_data=data.get("raw_data"),
        )

