"""Intent explanation example."""

from datetime import datetime, timedelta
from istari.core.events import Event
from istari.core.session import Session
from istari.inference.rules import RuleBasedInference
from istari.inference.heuristics import BrowsingRule, PurchaseReadyRule, AbandonmentRiskRule
from istari.core.explain import IntentExplanation
from istari.explainability.narratives import NarrativeGenerator
from istari.explainability.attributions import AttributionCalculator


def main():
    # Create a session
    session = Session(
        session_id="explain_session_001",
        user_id="user_999",
        started_at=datetime.utcnow() - timedelta(minutes=5),
    )
    
    # Add events
    base_time = datetime.utcnow() - timedelta(minutes=5)
    
    events = [
        Event(
            event_type="page_view",
            timestamp=base_time,
            user_id="user_999",
            session_id="explain_session_001",
            properties={"page": "/products"},
        ),
        Event(
            event_type="product_view",
            timestamp=base_time + timedelta(seconds=30),
            user_id="user_999",
            session_id="explain_session_001",
            properties={"product_id": "item_1", "price": 49.99},
        ),
        Event(
            event_type="product_view",
            timestamp=base_time + timedelta(seconds=60),
            user_id="user_999",
            session_id="explain_session_001",
            properties={"product_id": "item_2", "price": 59.99},
        ),
        Event(
            event_type="add_to_cart",
            timestamp=base_time + timedelta(seconds=120),
            user_id="user_999",
            session_id="explain_session_001",
            properties={"product_id": "item_1", "price": 49.99},
        ),
    ]
    
    session.add_events(events)
    
    # Infer intent state
    inference = RuleBasedInference()
    inference.add_rule(BrowsingRule())
    inference.add_rule(PurchaseReadyRule())
    inference.add_rule(AbandonmentRiskRule())
    
    intent_state = inference.infer(session)
    
    # Calculate attributions
    attribution_calc = AttributionCalculator()
    attributions = attribution_calc.calculate(intent_state, session)
    
    # Create explanation
    explanation = IntentExplanation(intent_state)
    
    # Add factors based on attributions
    for signal_name, contribution in attributions.items():
        description = f"{signal_name} signal contributed {contribution:.1%} to this inference"
        explanation.add_factor(signal_name, contribution, description)
    
    # Add evidence
    explanation.add_evidence(f"User viewed {len([e for e in events if e.event_type == 'product_view'])} products")
    explanation.add_evidence("User added item to cart")
    
    # Generate narrative
    narrative_gen = NarrativeGenerator()
    narrative = narrative_gen.generate_state_narrative(intent_state, session)
    
    print("=== Intent State Explanation ===")
    print("\n" + explanation.to_text())
    
    print("\n=== Narrative ===")
    print(narrative)
    
    print("\n=== Top Attributions ===")
    top_attrs = attribution_calc.get_top_attributions(attributions, top_n=3)
    for signal_name, score in top_attrs:
        print(f"{signal_name}: {score:.2%}")


if __name__ == "__main__":
    main()

