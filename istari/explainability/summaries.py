"""Session summary generation."""

from typing import Dict, Any, List
from istari.core.session import Session
from istari.core.intent_state import IntentState


class SessionSummary:
    """Generates structured summaries of sessions."""
    
    def summarize(self, session: Session) -> Dict[str, Any]:
        """
        Generate a structured summary of a session.
        
        Args:
            session: Session to summarize
        
        Returns:
            Dictionary with summary information
        """
        current_state = session.get_current_intent_state()
        
        summary = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "duration_seconds": session.get_duration().total_seconds(),
            "event_count": session.get_event_count(),
            "current_intent_state": current_state.state_type if current_state else None,
            "current_confidence": current_state.confidence if current_state else None,
            "intent_trajectory": [
                {
                    "state": s.state_type,
                    "confidence": s.confidence,
                    "timestamp": s.timestamp.isoformat(),
                }
                for s in session.intent_states
            ],
            "transitions": len(session.transitions),
        }
        
        # Add signal summaries
        from istari.signals import (
            DwellSignal,
            NavigationSignal,
            ComparisonSignal,
            FrictionSignal,
            PriceSignal,
        )
        
        summary["signals"] = {
            "dwell": DwellSignal().extract(session),
            "navigation": NavigationSignal().extract(session),
            "comparison": ComparisonSignal().extract(session),
            "friction": FrictionSignal().extract(session),
            "price": PriceSignal().extract(session),
        }
        
        return summary
    
    def get_key_insights(self, session: Session) -> List[str]:
        """
        Extract key insights from a session.
        
        Args:
            session: Session to analyze
        
        Returns:
            List of insight strings
        """
        insights = []
        
        current_state = session.get_current_intent_state()
        if current_state:
            if current_state.confidence < 0.5:
                insights.append("Low confidence in current intent state - user behavior is ambiguous")
            
            if current_state.state_type == "abandonment_risk":
                insights.append("User shows signs of abandonment - intervention may be needed")
            
            if current_state.state_type == "purchase_ready":
                insights.append("User appears ready to purchase - conversion opportunity")
        
        # Check friction signals
        from istari.signals import FrictionSignal
        friction_data = FrictionSignal().extract(session)
        
        if friction_data.get("friction_score", 0) > 0.5:
            insights.append("High friction detected - user may be experiencing obstacles")
        
        # Check for rapid state changes
        if len(session.transitions) > 3:
            insights.append("Multiple state transitions detected - user intent is evolving rapidly")
        
        return insights

