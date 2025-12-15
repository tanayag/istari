"""Basic intent inference example."""

from datetime import datetime, timedelta, timezone
from istari.core.events import Event
from istari.core.session import Session
from istari.inference.rules import RuleBasedInference
from istari.inference.heuristics import BrowsingRule, PurchaseReadyRule, AbandonmentRiskRule


def main():
    # Create a session
    session = Session(
        session_id="session_123",
        user_id="user_456",
        started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    
    # Add some events
    base_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    events = [
        Event(
            event_type="page_view",
            timestamp=base_time,
            user_id="user_456",
            session_id="session_123",
            properties={"page": "/home"},
        ),
        Event(
            event_type="page_view",
            timestamp=base_time + timedelta(seconds=30),
            user_id="user_456",
            session_id="session_123",
            properties={"page": "/products"},
        ),
        Event(
            event_type="product_view",
            timestamp=base_time + timedelta(seconds=45),
            user_id="user_456",
            session_id="session_123",
            properties={"product_id": "prod_1", "price": 29.99},
        ),
        Event(
            event_type="add_to_cart",
            timestamp=base_time + timedelta(seconds=120),
            user_id="user_456",
            session_id="session_123",
            properties={"product_id": "prod_1", "price": 29.99},
        ),
    ]
    
    session.add_events(events)
    
    # Set up inference engine with rules
    inference = RuleBasedInference()
    inference.add_rule(BrowsingRule())
    inference.add_rule(PurchaseReadyRule())
    inference.add_rule(AbandonmentRiskRule())
    
    # Infer intent state
    intent_state = inference.infer(session)
    
    print(f"Inferred Intent State: {intent_state.state_type}")
    print(f"Confidence: {intent_state.confidence:.2%}")
    print(f"Attributions: {intent_state.attributions}")
    print(f"Evidence: {intent_state.evidence}")


if __name__ == "__main__":
    main()

