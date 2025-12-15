"""Rule-based intent inference."""

from typing import List, Dict, Any, Optional
from istari.core.session import Session
from istari.core.intent_state import IntentState
from istari.core.scoring import Score, Scorer
from istari.inference.heuristics import HeuristicRule


class RuleBasedInference:
    """
    Rule-based inference engine for intent states.
    
    Uses deterministic rules and heuristics to infer intent states.
    """
    
    def __init__(self, rules: Optional[List[HeuristicRule]] = None):
        """
        Initialize rule-based inference engine.
        
        Args:
            rules: List of heuristic rules to apply
        """
        self.rules = rules or []
        self.scorer = RuleScorer()
    
    def add_rule(self, rule: HeuristicRule):
        """Add a heuristic rule."""
        self.rules.append(rule)
    
    def infer(self, session: Session) -> IntentState:
        """
        Infer intent state for a session.
        
        Args:
            session: Session to analyze
        
        Returns:
            Most likely intent state
        """
        # Score all possible states
        scores = []
        for state_type in self._get_possible_states():
            score = self.scorer.score(state_type, {
                "session": session,
                "rules": self.rules,
            })
            scores.append(score)
        
        # Select highest scoring state
        best_score = max(scores, key=lambda s: s.confidence)
        
        # Create intent state
        current_time = session.timeline.get_events()[-1].timestamp if not session.timeline.is_empty() else session.started_at
        
        state = IntentState(
            state_type=best_score.state_type,
            timestamp=current_time,
            confidence=best_score.confidence,
            attributions={factor: score for factor, score in best_score.factors.items()},
            evidence=best_score.explanation.split(". ") if best_score.explanation else [],
        )
        
        return state
    
    def _get_possible_states(self) -> List[str]:
        """Get list of possible intent state types."""
        from istari.core.intent_state import IntentStateType
        return [state.value for state in IntentStateType]


class RuleScorer(Scorer):
    """Scorer for rule-based inference."""
    
    def score(self, state_type: str, context: Dict[str, Any]) -> Score:
        """Score a potential intent state."""
        session = context["session"]
        rules = context["rules"]
        
        score = Score(
            state_type=state_type,
            score=0.0,
            confidence=0.0,
        )
        
        total_weight = 0.0
        
        # Apply all rules
        for rule in rules:
            if rule.matches(state_type, session):
                weight = rule.get_weight()
                contribution = rule.evaluate(session)
                
                score.add_factor(rule.name, contribution)
                score.score += contribution * weight
                total_weight += weight
        
        # Normalize confidence
        if total_weight > 0:
            score.confidence = self.normalize_confidence(
                score.score / total_weight if total_weight > 0 else 0.0
            )
        else:
            score.confidence = 0.0
        
        # Generate explanation
        factors_str = ", ".join([
            f"{name} ({score:.2%})" 
            for name, score in score.factors.items()
        ])
        score.explanation = f"Inferred {state_type} based on: {factors_str}"
        
        return score

