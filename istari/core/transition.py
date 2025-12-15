"""State transition modeling."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from istari.core.intent_state import IntentState


@dataclass
class Transition:
    """
    Represents a transition between two intent states.
    
    Captures the change in user intent over time.
    """
    from_state: IntentState
    to_state: IntentState
    timestamp: datetime
    
    # Transition metadata
    transition_type: str = "normal"  # normal, abrupt, gradual
    confidence: float = 1.0
    
    def __post_init__(self):
        """Validate transition."""
        if self.from_state.timestamp > self.to_state.timestamp:
            raise ValueError("from_state timestamp must be <= to_state timestamp")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def get_duration(self) -> float:
        """Get duration of transition in seconds."""
        delta = self.to_state.timestamp - self.from_state.timestamp
        return delta.total_seconds()
    
    def is_state_change(self) -> bool:
        """Check if this represents an actual state change."""
        return self.from_state.state_type != self.to_state.state_type
    
    def to_dict(self) -> dict:
        """Convert transition to dictionary."""
        return {
            "from_state": self.from_state.to_dict(),
            "to_state": self.to_state.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "transition_type": self.transition_type,
            "confidence": self.confidence,
        }

