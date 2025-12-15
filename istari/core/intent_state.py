"""Intent state definitions and management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class IntentStateType(str, Enum):
    """Standard intent state types."""
    BROWSING = "browsing"
    EVALUATING_OPTIONS = "evaluating_options"
    PRICE_SENSITIVE = "price_sensitive"
    TRUST_SEEKING = "trust_seeking"
    PURCHASE_READY = "purchase_ready"
    ABANDONMENT_RISK = "abandonment_risk"
    EXPLORING = "exploring"
    COMPARING = "comparing"
    HESITATING = "hesitating"
    READY_TO_ACT = "ready_to_act"


@dataclass
class IntentState:
    """
    Represents a user's intent state at a point in time.
    
    Intent states are:
    - time-aware: associated with a timestamp
    - probabilistic: have confidence scores
    - explainable: include attribution data
    - composable: can be combined across domains
    """
    state_type: str
    timestamp: datetime
    confidence: float  # 0.0 to 1.0
    
    # Explainability
    attributions: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Optional domain-specific properties
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate intent state after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert intent state to dictionary."""
        return {
            "state_type": self.state_type,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "attributions": self.attributions,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "properties": self.properties,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentState":
        """Create intent state from dictionary."""
        timestamp = data["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        return cls(
            state_type=data["state_type"],
            timestamp=timestamp,
            confidence=data["confidence"],
            attributions=data.get("attributions", {}),
            evidence=data.get("evidence", []),
            metadata=data.get("metadata", {}),
            properties=data.get("properties", {}),
        )
    
    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if state has high confidence."""
        return self.confidence >= threshold
    
    def add_attribution(self, source: str, score: float):
        """Add an attribution score for a signal source."""
        self.attributions[source] = score
    
    def add_evidence(self, evidence: str):
        """Add evidence string explaining why this state was inferred."""
        self.evidence.append(evidence)

