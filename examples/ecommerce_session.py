"""E-commerce session analysis example."""

from datetime import datetime, timedelta
from istari.core.events import Event
from istari.core.session import Session
from istari.inference.rules import RuleBasedInference
from istari.inference.heuristics import BrowsingRule, PurchaseReadyRule, AbandonmentRiskRule
from istari.inference.state_machine import IntentStateMachine
from istari.explainability.summaries import SessionSummary


def main():
    # Create a session
    session = Session(
        session_id="ecommerce_session_001",
        user_id="customer_789",
        started_at=datetime.utcnow() - timedelta(minutes=15),
    )
    
    # Simulate an e-commerce session
    base_time = datetime.utcnow() - timedelta(minutes=15)
    
    events = [
        # Initial browsing
        Event(
            event_type="page_view",
            timestamp=base_time,
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={"page": "/"},
        ),
        Event(
            event_type="page_view",
            timestamp=base_time + timedelta(seconds=20),
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={"page": "/products"},
        ),
        
        # Product exploration
        Event(
            event_type="product_view",
            timestamp=base_time + timedelta(seconds=45),
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={"product_id": "laptop_001", "price": 999.99, "category": "electronics"},
        ),
        Event(
            event_type="product_view",
            timestamp=base_time + timedelta(seconds=90),
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={"product_id": "laptop_002", "price": 1299.99, "category": "electronics"},
        ),
        
        # Add to cart
        Event(
            event_type="add_to_cart",
            timestamp=base_time + timedelta(seconds=180),
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={"product_id": "laptop_001", "price": 999.99},
        ),
        
        # Checkout process
        Event(
            event_type="checkout_started",
            timestamp=base_time + timedelta(seconds=240),
            user_id="customer_789",
            session_id="ecommerce_session_001",
            properties={},
        ),
    ]
    
    session.add_events(events)
    
    # Set up inference
    inference = RuleBasedInference()
    inference.add_rule(BrowsingRule())
    inference.add_rule(PurchaseReadyRule())
    inference.add_rule(AbandonmentRiskRule())
    
    # Use state machine to infer trajectory
    state_machine = IntentStateMachine(inference_engine=inference)
    trajectory = state_machine.infer_trajectory(session)
    
    # Add states to session
    for state in trajectory:
        session.add_intent_state(state)
    
    # Create transitions
    transitions = state_machine.create_transitions(trajectory)
    for transition in transitions:
        session.add_transition(transition)
    
    # Generate summary
    summary = SessionSummary()
    session_data = summary.summarize(session)
    insights = summary.get_key_insights(session)
    
    print("=== E-commerce Session Analysis ===")
    print(f"\nSession ID: {session_data['session_id']}")
    print(f"Duration: {session_data['duration_seconds']:.0f} seconds")
    print(f"Events: {session_data['event_count']}")
    print(f"\nCurrent Intent: {session_data['current_intent_state']}")
    print(f"Confidence: {session_data['current_confidence']:.2%}")
    
    print("\n=== Intent Trajectory ===")
    for i, state_info in enumerate(session_data['intent_trajectory'], 1):
        print(f"{i}. {state_info['state']} (confidence: {state_info['confidence']:.2%})")
    
    print("\n=== Key Insights ===")
    for insight in insights:
        print(f"- {insight}")
    
    print("\n=== Signals ===")
    signals = session_data['signals']
    print(f"Navigation: {signals['navigation']['unique_pages']} unique pages")
    print(f"Comparison: {signals['comparison']['is_comparing']}")
    print(f"Friction Score: {signals['friction']['friction_score']:.2f}")


if __name__ == "__main__":
    main()

