"""Microsoft Clarity integration example."""

from datetime import datetime, timezone
from istari.sources.clarity import ClaritySource
from istari.core.session import Session


def main():
    # Example Clarity raw events (as they might come from Clarity export)
    clarity_raw_events = [
        {
            "event": "rage_click",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "userId": "user_123",
            "sessionId": "session_456",
            "clickCount": 5,
            "url": "/checkout",
            "path": "/checkout",
        },
        {
            "event": "dead_click",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000) + 1000,
            "userId": "user_123",
            "sessionId": "session_456",
            "url": "/checkout",
            "path": "/checkout",
        },
        {
            "event": "scroll",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000) + 2000,
            "userId": "user_123",
            "sessionId": "session_456",
            "scrollDepth": 85,
            "url": "/product",
            "path": "/product",
        },
        {
            "event": "hover",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000) + 3000,
            "userId": "user_123",
            "sessionId": "session_456",
            "hoverDuration": 4.5,
            "url": "/product",
            "path": "/product",
        },
    ]
    
    # Initialize Clarity source
    clarity_source = ClaritySource()
    
    # Parse Clarity events into Istari canonical format
    istari_events, signals = clarity_source.process(clarity_raw_events)
    
    print("=== Clarity Events Parsed ===")
    print(f"Parsed {len(istari_events)} events\n")
    
    for event in istari_events:
        print(f"Event: {event.event_type}")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  User: {event.user_id}")
        print(f"  Session: {event.session_id}")
        print(f"  Properties: {event.properties}")
        print()
    
    print("=== Mapped Signals ===")
    print("Clarity signals mapped to Istari signal categories:\n")
    
    signal_explanations = {
        "friction.high": "Rage clicks detected - user experiencing high friction",
        "intent.confusion": "Dead clicks detected - user intent is unclear",
        "content_engagement": "Scroll depth indicates content engagement level",
        "dissatisfaction": "Quick back navigation suggests dissatisfaction",
        "hesitation": "Excessive hover time indicates hesitation",
    }
    
    for signal_type, value in signals.items():
        explanation = signal_explanations.get(signal_type, "")
        print(f"{signal_type}: {value:.2f}")
        if explanation:
            print(f"  → {explanation}")
        print()
    
    # Create a session and add Clarity events
    session = Session(
        session_id="session_456",
        user_id="user_123",
        started_at=istari_events[0].timestamp if istari_events else datetime.now(timezone.utc),
    )
    
    session.add_events(istari_events)
    
    print("=== Session Created ===")
    print(f"Session ID: {session.session_id}")
    print(f"User ID: {session.user_id}")
    print(f"Event Count: {session.get_event_count()}")
    print(f"Duration: {session.get_duration().total_seconds():.0f} seconds")
    
    print("\n=== Signal Mapping Summary ===")
    print("These Clarity signals can now be used by Istari's inference engine:")
    print("  - friction.high → contributes to 'abandonment_risk' intent state")
    print("  - intent.confusion → contributes to 'hesitating' intent state")
    print("  - content_engagement → contributes to 'browsing' intent state")
    print("  - hesitation → contributes to 'hesitating' intent state")


if __name__ == "__main__":
    main()

