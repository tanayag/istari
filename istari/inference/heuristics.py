"""Heuristic rules for intent inference."""

from typing import List, Optional
from abc import ABC, abstractmethod
from istari.core.session import Session
from istari.core.intent_state import IntentStateType


class HeuristicRule(ABC):
    """Base class for heuristic rules."""
    
    def __init__(self, name: str, weight: float = 1.0):
        """
        Initialize heuristic rule.
        
        Args:
            name: Name of the rule
            weight: Weight for scoring (default: 1.0)
        """
        self.name = name
        self.weight = weight
    
    @abstractmethod
    def matches(self, state_type: str, session: Session) -> bool:
        """
        Check if this rule applies to a state type and session.
        
        Args:
            state_type: Intent state type to check
            session: Session to analyze
        
        Returns:
            True if rule applies
        """
        pass
    
    @abstractmethod
    def evaluate(self, session: Session) -> float:
        """
        Evaluate the rule and return a score (0.0 to 1.0).
        
        Args:
            session: Session to evaluate
        
        Returns:
            Score between 0.0 and 1.0
        """
        pass
    
    def get_weight(self) -> float:
        """Get the weight of this rule."""
        return self.weight


class BrowsingRule(HeuristicRule):
    """Rule for detecting browsing intent."""
    
    def __init__(self):
        super().__init__("browsing_rule", weight=1.0)
    
    def matches(self, state_type: str, session: Session) -> bool:
        return state_type == IntentStateType.BROWSING.value
    
    def evaluate(self, session: Session) -> float:
        """Score browsing intent based on page views and low engagement."""
        events = session.timeline.get_events()
        page_views = len([e for e in events if e.event_type == "page_view"])
        
        if page_views >= 3:
            return 0.8
        elif page_views >= 1:
            return 0.5
        return 0.2


class PurchaseReadyRule(HeuristicRule):
    """Rule for detecting purchase-ready intent."""
    
    def __init__(self):
        super().__init__("purchase_ready_rule", weight=1.5)
    
    def matches(self, state_type: str, session: Session) -> bool:
        return state_type == IntentStateType.PURCHASE_READY.value
    
    def evaluate(self, session: Session) -> float:
        """Score purchase-ready intent based on checkout events."""
        events = session.timeline.get_events()
        
        has_add_to_cart = any(e.event_type == "add_to_cart" for e in events)
        has_checkout = any(e.event_type in ["checkout_started", "checkout_completed"] for e in events)
        
        if has_checkout:
            return 0.9
        elif has_add_to_cart:
            return 0.7
        return 0.1


class AbandonmentRiskRule(HeuristicRule):
    """Rule for detecting abandonment risk."""
    
    def __init__(self):
        super().__init__("abandonment_risk_rule", weight=1.2)
    
    def matches(self, state_type: str, session: Session) -> bool:
        return state_type == IntentStateType.ABANDONMENT_RISK.value
    
    def evaluate(self, session: Session) -> float:
        """Score abandonment risk based on cart actions and time gaps."""
        events = session.timeline.get_events()
        
        has_add_to_cart = any(e.event_type == "add_to_cart" for e in events)
        has_remove_from_cart = any(e.event_type == "remove_from_cart" for e in events)
        
        # Check for long time gaps
        gaps = session.timeline.get_time_gaps()
        long_gaps = [g for g in gaps if g.total_seconds() > 300]  # 5 minutes
        
        if has_remove_from_cart:
            return 0.8
        elif has_add_to_cart and long_gaps:
            return 0.7
        elif long_gaps:
            return 0.5
        return 0.2

