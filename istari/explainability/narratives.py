"""Narrative generation for intent explanations."""

from typing import List, Dict, Any
from istari.core.session import Session
from istari.core.intent_state import IntentState
from istari.core.transition import Transition


class NarrativeGenerator:
    """Generates human-readable narratives for intent states and transitions."""
    
    def generate_state_narrative(self, state: IntentState, session: Session) -> str:
        """
        Generate a narrative explaining an intent state.
        
        Args:
            state: Intent state to explain
            session: Session context
        
        Returns:
            Human-readable narrative string
        """
        event_count = session.get_event_count()
        duration = session.get_duration().total_seconds()
        
        lines = [
            f"The user is currently in a '{state.state_type}' state "
            f"(confidence: {state.confidence:.1%}).",
        ]
        
        if state.attributions:
            top_attrs = sorted(
                state.attributions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]
            
            if top_attrs:
                attr_desc = ", ".join([
                    f"{name} ({score:.1%})" for name, score in top_attrs
                ])
                lines.append(f"This inference is primarily driven by: {attr_desc}.")
        
        if state.evidence:
            lines.append("")
            lines.append("Supporting evidence:")
            for evidence in state.evidence[:3]:
                lines.append(f"  - {evidence}")
        
        lines.append("")
        lines.append(f"Session context: {event_count} events over {duration:.0f} seconds.")
        
        return "\n".join(lines)
    
    def generate_transition_narrative(self, transition: Transition) -> str:
        """
        Generate a narrative explaining a state transition.
        
        Args:
            transition: Transition to explain
        
        Returns:
            Human-readable narrative string
        """
        duration = transition.get_duration()
        
        lines = [
            f"User transitioned from '{transition.from_state.state_type}' "
            f"to '{transition.to_state.state_type}'.",
        ]
        
        if duration < 10:
            lines.append("This was a rapid transition, suggesting immediate user action.")
        elif duration < 60:
            lines.append("This transition occurred within a minute.")
        else:
            lines.append(f"This transition took {duration:.0f} seconds, indicating gradual intent change.")
        
        if transition.transition_type == "abrupt":
            lines.append("The abrupt nature suggests a significant change in user intent.")
        elif transition.transition_type == "gradual":
            lines.append("The gradual transition indicates evolving user behavior.")
        
        return "\n".join(lines)
    
    def generate_session_narrative(self, session: Session) -> str:
        """
        Generate a narrative summarizing a session.
        
        Args:
            session: Session to summarize
        
        Returns:
            Human-readable narrative string
        """
        lines = [
            f"Session {session.session_id} for user {session.user_id}",
            f"Duration: {session.get_duration().total_seconds():.0f} seconds",
            f"Events: {session.get_event_count()}",
        ]
        
        if session.intent_states:
            lines.append("")
            lines.append("Intent trajectory:")
            for i, state in enumerate(session.intent_states, 1):
                lines.append(
                    f"  {i}. {state.state_type} "
                    f"(confidence: {state.confidence:.1%}, "
                    f"time: {state.timestamp.isoformat()})"
                )
        
        if session.transitions:
            lines.append("")
            lines.append("State transitions:")
            for i, transition in enumerate(session.transitions, 1):
                lines.append(
                    f"  {i}. {transition.from_state.state_type} → "
                    f"{transition.to_state.state_type}"
                )
        
        return "\n".join(lines)

