"""Confidence calculation for intent states."""

from typing import Dict, Any, List, Optional
from istari.core.intent_state import IntentState
from istari.core.session import Session


class ConfidenceCalculator:
    """Calculates confidence scores for intent states."""
    
    def calculate(
        self,
        state: IntentState,
        session: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate confidence score for an intent state.
        
        Args:
            state: Intent state to calculate confidence for
            session: Session context
            context: Additional context
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from state itself
        base_confidence = state.confidence
        
        # Adjust based on evidence strength
        evidence_factor = self._calculate_evidence_factor(state, session)
        
        # Adjust based on attribution consistency
        attribution_factor = self._calculate_attribution_factor(state)
        
        # Combine factors
        confidence = base_confidence * evidence_factor * attribution_factor
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_evidence_factor(self, state: IntentState, session: Session) -> float:
        """Calculate evidence strength factor."""
        if not state.evidence:
            return 0.7  # Lower confidence without evidence
        
        # More evidence = higher confidence
        evidence_count = len(state.evidence)
        if evidence_count >= 3:
            return 1.0
        elif evidence_count >= 2:
            return 0.9
        elif evidence_count >= 1:
            return 0.8
        return 0.7
    
    def _calculate_attribution_factor(self, state: IntentState) -> float:
        """Calculate attribution consistency factor."""
        if not state.attributions:
            return 0.8  # Moderate confidence without attributions
        
        # Check if attributions are consistent (not too spread out)
        values = list(state.attributions.values())
        if not values:
            return 0.8
        
        # If one attribution dominates, higher confidence
        max_attr = max(values)
        total_attr = sum(values)
        
        if total_attr == 0:
            return 0.8
        
        dominance = max_attr / total_attr
        return 0.7 + (dominance * 0.3)  # Scale between 0.7 and 1.0

