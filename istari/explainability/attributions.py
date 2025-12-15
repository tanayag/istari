"""Attribution calculation for intent states."""

from typing import Dict, List, Any
from istari.core.intent_state import IntentState
from istari.core.session import Session


class AttributionCalculator:
    """Calculates attributions for intent state inference."""
    
    def calculate(self, state: IntentState, session: Session) -> Dict[str, float]:
        """
        Calculate attributions for an intent state.
        
        Args:
            state: Intent state to calculate attributions for
            session: Session context
        
        Returns:
            Dictionary mapping signal names to attribution scores
        """
        attributions = {}
        
        # Extract signals
        from istari.signals import (
            DwellSignal,
            NavigationSignal,
            ComparisonSignal,
            FrictionSignal,
            PriceSignal,
        )
        
        dwell_signal = DwellSignal()
        nav_signal = NavigationSignal()
        comp_signal = ComparisonSignal()
        friction_signal = FrictionSignal()
        price_signal = PriceSignal()
        
        # Calculate signal values
        dwell_data = dwell_signal.extract(session)
        nav_data = nav_signal.extract(session)
        comp_data = comp_signal.extract(session)
        friction_data = friction_signal.extract(session)
        price_data = price_signal.extract(session)
        
        # Map signals to attributions based on state type
        if state.state_type == "browsing":
            attributions["navigation"] = min(1.0, nav_data.get("unique_pages", 0) / 5.0)
            attributions["dwell"] = min(1.0, dwell_data.get("avg_dwell_seconds", 0) / 30.0)
        
        elif state.state_type == "evaluating_options":
            attributions["comparison"] = comp_data.get("comparison_score", 0.0)
            attributions["navigation"] = min(1.0, nav_data.get("unique_pages", 0) / 5.0)
        
        elif state.state_type == "price_sensitive":
            attributions["price"] = price_data.get("price_sensitivity_score", 0.0)
            attributions["comparison"] = comp_data.get("comparison_score", 0.0)
        
        elif state.state_type == "trust_seeking":
            attributions["dwell"] = min(1.0, dwell_data.get("avg_dwell_seconds", 0) / 60.0)
            attributions["navigation"] = min(1.0, nav_data.get("unique_pages", 0) / 3.0)
        
        elif state.state_type == "purchase_ready":
            attributions["navigation"] = 1.0 if nav_data.get("unique_pages", 0) >= 2 else 0.5
            attributions["friction"] = 1.0 - friction_data.get("friction_score", 0.0)
        
        elif state.state_type == "abandonment_risk":
            attributions["friction"] = friction_data.get("friction_score", 0.0)
            attributions["dwell"] = min(1.0, dwell_data.get("max_dwell_seconds", 0) / 120.0)
        
        # Normalize attributions
        total = sum(attributions.values())
        if total > 0:
            attributions = {k: v / total for k, v in attributions.items()}
        
        return attributions
    
    def get_top_attributions(
        self,
        attributions: Dict[str, float],
        top_n: int = 3
    ) -> List[tuple]:
        """
        Get top N attributions.
        
        Args:
            attributions: Dictionary of attributions
            top_n: Number of top attributions to return
        
        Returns:
            List of (signal_name, score) tuples, sorted by score descending
        """
        sorted_attrs = sorted(
            attributions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_attrs[:top_n]

