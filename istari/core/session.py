"""Session modeling and management."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from istari.core.events import Event
from istari.core.timeline import Timeline
from istari.core.intent_state import IntentState
from istari.core.transition import Transition
from istari.exceptions import SessionError


class Session:
    """
    Represents a user session with events and inferred intent trajectory.
    
    Models sessions as continuous intent trajectories over time.
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        started_at: Optional[datetime] = None,
    ):
        """
        Initialize a session.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            started_at: Session start timestamp (defaults to now)
        """
        self.session_id = session_id
        self.user_id = user_id
        self.started_at = started_at or datetime.utcnow()
        
        self.timeline = Timeline()
        self.intent_states: List[IntentState] = []
        self.transitions: List[Transition] = []
        
        # Session metadata
        self.metadata: Dict[str, Any] = {}
    
    def add_event(self, event: Event):
        """
        Add an event to the session.
        
        Args:
            event: Event to add
        
        Raises:
            SessionError: If event doesn't match session
        """
        if event.session_id != self.session_id:
            raise SessionError(
                f"Event session_id {event.session_id} doesn't match "
                f"session {self.session_id}"
            )
        if event.user_id != self.user_id:
            raise SessionError(
                f"Event user_id {event.user_id} doesn't match "
                f"session user {self.user_id}"
            )
        
        self.timeline.add_event(event)
    
    def add_events(self, events: List[Event]):
        """Add multiple events to the session."""
        for event in events:
            self.add_event(event)
    
    def add_intent_state(self, state: IntentState):
        """Add an inferred intent state."""
        self.intent_states.append(state)
        self.intent_states.sort(key=lambda s: s.timestamp)
    
    def add_transition(self, transition: Transition):
        """Add a state transition."""
        self.transitions.append(transition)
        self.transitions.sort(key=lambda t: t.timestamp)
    
    def get_current_intent_state(self) -> Optional[IntentState]:
        """
        Get the most recent intent state.
        
        Returns:
            Most recent intent state, or None if no states exist
        """
        if not self.intent_states:
            return None
        return self.intent_states[-1]
    
    def get_intent_trajectory(self) -> List[IntentState]:
        """
        Get the full intent trajectory (chronologically ordered).
        
        Returns:
            List of intent states in chronological order
        """
        return self.intent_states.copy()
    
    def get_duration(self) -> timedelta:
        """Get session duration."""
        if self.timeline.is_empty():
            return timedelta(0)
        
        events = self.timeline.get_events()
        if len(events) == 0:
            return timedelta(0)
        
        end_time = events[-1].timestamp
        return end_time - self.started_at
    
    def get_event_count(self) -> int:
        """Get total number of events in session."""
        return self.timeline.get_event_count()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat(),
            "duration_seconds": self.get_duration().total_seconds(),
            "event_count": self.get_event_count(),
            "intent_states": [s.to_dict() for s in self.intent_states],
            "transitions": [t.to_dict() for t in self.transitions],
            "metadata": self.metadata,
        }

