"""Scoring mechanisms for intent states."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from istari.core.intent_state import IntentState


@dataclass
class Score:
    """
    Represents a score for an intent state hypothesis.
    
    Used during inference to rank potential states.
    """
    state_type: str
    score: float  # Raw score (not normalized)
    confidence: float  # Normalized confidence (0.0 to 1.0)
    
    # Scoring metadata
    factors: Dict[str, float] = None  # Contribution of each factor
    explanation: Optional[str] = None
    
    def __post_init__(self):
        """Initialize factors if not provided."""
        if self.factors is None:
            self.factors = {}
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def add_factor(self, name: str, contribution: float):
        """Add a scoring factor contribution."""
        self.factors[name] = contribution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary."""
        return {
            "state_type": self.state_type,
            "score": self.score,
            "confidence": self.confidence,
            "factors": self.factors,
            "explanation": self.explanation,
        }


class Scorer:
    """Base class for intent state scoring."""
    
    def score(self, state_type: str, context: Dict[str, Any]) -> Score:
        """
        Score a potential intent state.
        
        Args:
            state_type: The intent state type to score
            context: Contextual information (events, signals, etc.)
        
        Returns:
            Score object
        """
        raise NotImplementedError("Subclasses must implement score()")
    
    def normalize_confidence(self, raw_score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
        """
        Normalize a raw score to confidence (0.0 to 1.0).
        
        Args:
            raw_score: Raw score value
            min_score: Minimum possible score
            max_score: Maximum possible score
        
        Returns:
            Normalized confidence value
        """
        if max_score == min_score:
            return 0.5
        
        normalized = (raw_score - min_score) / (max_score - min_score)
        return max(0.0, min(1.0, normalized))

