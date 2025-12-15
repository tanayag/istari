"""State machine for intent state transitions."""

from typing import List, Dict, Optional
from datetime import datetime
from istari.core.session import Session
from istari.core.intent_state import IntentState
from istari.core.transition import Transition
from istari.inference.rules import RuleBasedInference


class IntentStateMachine:
    """
    State machine that produces intent trajectories.
    
    Manages state transitions and maintains temporal consistency.
    """
    
    def __init__(self, inference_engine: Optional[RuleBasedInference] = None):
        """
        Initialize state machine.
        
        Args:
            inference_engine: Inference engine to use (defaults to RuleBasedInference)
        """
        self.inference_engine = inference_engine or RuleBasedInference()
        self.transition_rules: Dict[str, List[str]] = {}  # from_state -> [allowed_to_states]
    
    def add_transition_rule(self, from_state: str, to_states: List[str]):
        """
        Add a transition rule.
        
        Args:
            from_state: Source state
            to_states: List of allowed destination states
        """
        self.transition_rules[from_state] = to_states
    
    def infer_trajectory(self, session: Session) -> List[IntentState]:
        """
        Infer the full intent trajectory for a session.
        
        Args:
            session: Session to analyze
        
        Returns:
            List of intent states in chronological order
        """
        events = session.timeline.get_events()
        if not events:
            return []
        
        trajectory: List[IntentState] = []
        current_state: Optional[IntentState] = None
        
        # Process events in batches or at key points
        # For simplicity, infer state at each significant event
        significant_events = self._get_significant_events(events)
        
        for event in significant_events:
            # Create a temporary session up to this point
            temp_session = Session(
                session_id=session.session_id,
                user_id=session.user_id,
                started_at=session.started_at,
            )
            temp_session.add_events([e for e in events if e.timestamp <= event.timestamp])
            
            # Infer new state
            new_state = self.inference_engine.infer(temp_session)
            
            # Check if state actually changed
            if current_state is None or new_state.state_type != current_state.state_type:
                # Validate transition if we have rules
                if current_state and not self._is_valid_transition(current_state.state_type, new_state.state_type):
                    # If invalid, keep current state but update timestamp
                    new_state = IntentState(
                        state_type=current_state.state_type,
                        timestamp=new_state.timestamp,
                        confidence=new_state.confidence,
                        attributions=new_state.attributions,
                        evidence=new_state.evidence,
                    )
                else:
                    trajectory.append(new_state)
                    current_state = new_state
        
        return trajectory
    
    def _get_significant_events(self, events: List) -> List:
        """Get significant events for state inference."""
        significant_types = {
            "page_view",
            "add_to_cart",
            "remove_from_cart",
            "checkout_started",
            "checkout_completed",
            "purchase",
        }
        
        return [e for e in events if e.event_type in significant_types]
    
    def _is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid."""
        if from_state == to_state:
            return True
        
        if from_state not in self.transition_rules:
            return True  # No restrictions
        
        allowed = self.transition_rules[from_state]
        return to_state in allowed
    
    def create_transitions(self, states: List[IntentState]) -> List[Transition]:
        """
        Create transitions from a list of states.
        
        Args:
            states: List of intent states in chronological order
        
        Returns:
            List of transitions
        """
        transitions = []
        
        for i in range(1, len(states)):
            transition = Transition(
                from_state=states[i-1],
                to_state=states[i],
                timestamp=states[i].timestamp,
            )
            transitions.append(transition)
        
        return transitions

