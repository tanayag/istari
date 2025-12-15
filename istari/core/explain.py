"""Explainability primitives for intent inference."""

from typing import List, Dict, Any
from istari.core.intent_state import IntentState
from istari.core.transition import Transition


class Explanation:
    """Base class for explanations."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert explanation to dictionary."""
        raise NotImplementedError
    
    def to_text(self) -> str:
        """Convert explanation to human-readable text."""
        raise NotImplementedError


class IntentExplanation(Explanation):
    """Explanation for an intent state inference."""
    
    def __init__(self, state: IntentState):
        """
        Initialize explanation for an intent state.
        
        Args:
            state: The intent state being explained
        """
        self.state = state
        self.primary_factors: List[Dict[str, Any]] = []
        self.supporting_evidence: List[str] = []
    
    def add_factor(self, name: str, contribution: float, description: str):
        """Add a contributing factor."""
        self.primary_factors.append({
            "name": name,
            "contribution": contribution,
            "description": description,
        })
    
    def add_evidence(self, evidence: str):
        """Add supporting evidence."""
        self.supporting_evidence.append(evidence)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert explanation to dictionary."""
        return {
            "state_type": self.state.state_type,
            "confidence": self.state.confidence,
            "timestamp": self.state.timestamp.isoformat(),
            "primary_factors": self.primary_factors,
            "supporting_evidence": self.supporting_evidence,
            "attributions": self.state.attributions,
        }
    
    def to_text(self) -> str:
        """Convert explanation to human-readable text."""
        lines = [
            f"Intent State: {self.state.state_type}",
            f"Confidence: {self.state.confidence:.2%}",
            f"Timestamp: {self.state.timestamp.isoformat()}",
            "",
            "Primary Factors:",
        ]
        
        for factor in self.primary_factors:
            lines.append(
                f"  - {factor['name']}: {factor['contribution']:.2%} "
                f"({factor['description']})"
            )
        
        if self.supporting_evidence:
            lines.append("")
            lines.append("Supporting Evidence:")
            for evidence in self.supporting_evidence:
                lines.append(f"  - {evidence}")
        
        return "\n".join(lines)


class TransitionExplanation(Explanation):
    """Explanation for a state transition."""
    
    def __init__(self, transition: Transition):
        """
        Initialize explanation for a transition.
        
        Args:
            transition: The transition being explained
        """
        self.transition = transition
        self.trigger_events: List[str] = []
        self.reason: Optional[str] = None
    
    def add_trigger_event(self, event_type: str):
        """Add an event that triggered this transition."""
        self.trigger_events.append(event_type)
    
    def set_reason(self, reason: str):
        """Set the reason for this transition."""
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert explanation to dictionary."""
        return {
            "from_state": self.transition.from_state.state_type,
            "to_state": self.transition.to_state.state_type,
            "timestamp": self.transition.timestamp.isoformat(),
            "transition_type": self.transition.transition_type,
            "trigger_events": self.trigger_events,
            "reason": self.reason,
        }
    
    def to_text(self) -> str:
        """Convert explanation to human-readable text."""
        lines = [
            f"Transition: {self.transition.from_state.state_type} → "
            f"{self.transition.to_state.state_type}",
            f"Timestamp: {self.transition.timestamp.isoformat()}",
            f"Type: {self.transition.transition_type}",
        ]
        
        if self.trigger_events:
            lines.append("")
            lines.append("Trigger Events:")
            for event_type in self.trigger_events:
                lines.append(f"  - {event_type}")
        
        if self.reason:
            lines.append("")
            lines.append(f"Reason: {self.reason}")
        
        return "\n".join(lines)

