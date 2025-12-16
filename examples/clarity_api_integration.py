"""Microsoft Clarity API integration example."""

import os
from istari.sources.clarity import ClaritySource, ClarityAuthenticationError, ClarityAPIError


def main():
    # Get API key from environment variable or use placeholder
    api_key = os.getenv("CLARITY_API_KEY", "your-api-key-here")
    project_id = os.getenv("CLARITY_PROJECT_ID", "your-project-id")
    
    if api_key == "your-api-key-here":
        print("⚠️  Please set CLARITY_API_KEY environment variable")
        print("   Example: export CLARITY_API_KEY='your-actual-api-key'")
        print("\nTo get your API key:")
        print("1. Go to your Clarity project")
        print("2. Navigate to Settings > Data Export")
        print("3. Click 'Generate new API token'")
        print("4. Copy the token and set it as CLARITY_API_KEY")
        return
    
    # Initialize Clarity source
    clarity_source = ClaritySource()
    
    try:
        print("=== Fetching Data from Clarity API ===\n")
        
        # Option 1: Fetch and process in one call
        print("Fetching insights from Clarity API...")
        events, signals = clarity_source.import_from_api(
            api_key=api_key,
            project_id=project_id,
            start_date="2024-01-01",  # Optional: filter by date range
            end_date="2024-01-31",    # Optional: filter by date range
        )
        
        print(f"✓ Imported {len(events)} events")
        print(f"✓ Extracted {len(signals)} signal types\n")
        
        # Display events
        if events:
            print("=== Sample Events ===")
            for i, event in enumerate(events[:5], 1):  # Show first 5
                print(f"\n{i}. {event.event_type}")
                print(f"   User: {event.user_id}")
                print(f"   Session: {event.session_id}")
                print(f"   Timestamp: {event.timestamp}")
                if event.properties:
                    print(f"   Properties: {list(event.properties.keys())}")
        
        # Display signals
        if signals:
            print("\n=== Extracted Signals ===")
            for signal_type, value in signals.items():
                print(f"{signal_type}: {value:.2f}")
        
        # Option 2: Stream events directly from API
        print("\n=== Streaming Events from API ===")
        event_count = 0
        for raw_insight in clarity_source.fetch_from_api(
            api_key=api_key,
            project_id=project_id,
        ):
            event_count += 1
            if event_count <= 3:  # Show first 3
                print(f"Raw insight {event_count}: {type(raw_insight).__name__}")
                if isinstance(raw_insight, dict):
                    print(f"  Keys: {list(raw_insight.keys())[:5]}")
            if event_count >= 10:  # Limit for demo
                break
        
        print(f"\n✓ Streamed {event_count} insights from API")
        
    except ClarityAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPlease check:")
        print("1. Your API key is correct")
        print("2. The API key has proper permissions")
        print("3. The project ID matches your Clarity project")
    except ClarityAPIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()

