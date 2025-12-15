# Istari

Istari is a Python library that infers user intent states from raw behavioral event streams and exposes them as a structured, machine-readable layer for CRO systems, personalization engines, and agentic AI workflows.

Instead of treating user behavior as isolated events or funnels, Istari models sessions as continuous intent trajectories over time.

## What Problem Istari Solves

Modern products collect events like:
- page views
- scroll depth
- clicks
- add to cart
- remove from cart
- time gaps
- navigation loops
- rage clicks (Clarity)
- dead clicks (Clarity)

But downstream systems still reason in crude terms like funnels and conversion rates.

Istari sits between raw analytics and decision-making systems and answers:
- What is the user trying to do right now?
- Are they exploring, comparing, hesitating, or ready to act?
- What friction or uncertainty is blocking progress?
- How intent is evolving over the session?

## Core Abstraction

Istari introduces a first-class abstraction called an **Intent State**.

An intent state is:
- **time-aware**: associated with timestamps
- **probabilistic**: has confidence scores
- **explainable**: includes attribution data
- **composable**: can be combined across domains

Example intent states:
- `browsing`
- `evaluating_options`
- `price_sensitive`
- `trust_seeking`
- `purchase_ready`
- `abandonment_risk`

## High-Level Flow

1. Raw events are normalized into a canonical schema
2. Temporal patterns and transitions are extracted
3. Intent hypotheses are scored
4. A state machine produces the most likely intent trajectory
5. Outputs are exposed to CRO rules or agentic systems

## Design Goals

- **Python-first, backend friendly**
- **Deterministic core** with optional ML layers
- **Explainability by default**
- **Domain-adaptable** without retraining
- **Open-core friendly architecture**

## Installation

```bash
pip install istari-core
```

For development:

```bash
git clone https://github.com/istari/istari.git
cd istari
pip install -e .
```

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from istari.core.events import Event
from istari.core.session import Session
from istari.inference.rules import RuleBasedInference
from istari.inference.heuristics import BrowsingRule, PurchaseReadyRule

# Create a session
session = Session(
    session_id="session_123",
    user_id="user_456",
    started_at=datetime.now(timezone.utc),
)

# Add events
session.add_event(Event(
    event_type="page_view",
    timestamp=datetime.now(timezone.utc),
    user_id="user_456",
    session_id="session_123",
    properties={"page": "/products"},
))

# Infer intent state
inference = RuleBasedInference()
inference.add_rule(BrowsingRule())
inference.add_rule(PurchaseReadyRule())

intent_state = inference.infer(session)
print(f"Intent: {intent_state.state_type}")
print(f"Confidence: {intent_state.confidence:.2%}")
```

## Microsoft Clarity Integration

Istari includes first-class support for Microsoft Clarity behavioral signals. Clarity events are converted into Istari's canonical format and mapped to intent signals:

```python
from istari.sources.clarity import ClaritySource

# Initialize Clarity source
clarity_source = ClaritySource()

# Parse Clarity events/exports
clarity_events = [
    {
        "event": "rage_click",
        "timestamp": 1234567890000,
        "userId": "user_123",
        "sessionId": "session_456",
        "clickCount": 5,
    },
    # ... more events
]

# Parse and extract signals
events, signals = clarity_source.process(clarity_events)

# Signals are automatically mapped:
# - rage_click → friction.high
# - dead_click → intent.confusion
# - scroll → content_engagement
# - excessive_hover → hesitation
```

### Clarity Signal Mappings

| Clarity Signal | Istari Signal | Intent Impact |
|----------------|---------------|---------------|
| Rage clicks | `friction.high` | Contributes to `abandonment_risk` |
| Dead clicks | `intent.confusion` | Contributes to `hesitating` |
| Scroll depth | `content_engagement` | Contributes to `browsing` |
| Quick back nav | `dissatisfaction` | Contributes to `abandonment_risk` |
| Excessive hover | `hesitation` | Contributes to `hesitating` |

## Architecture

### Core Modules

- **`core/`**: Event normalization, session modeling, intent states, transitions, scoring
- **`schemas/`**: Event schema normalization (base, ecommerce, web)
- **`inference/`**: Rule-based inference, heuristics, state machine, confidence calculation
- **`signals/`**: Signal extraction (dwell, navigation, comparison, friction, price)
- **`explainability/`**: Attribution calculation, narrative generation, summaries
- **`plugins/`**: Plugin system for extending inference capabilities
- **`sources/`**: Event source integrations (Clarity, etc.)
- **`integrations/`**: Analytics platform integrations (Mixpanel, Amplitude, Segment)

### Event Sources vs Integrations

- **`sources/`**: Behavioral signal sources (like Clarity) that provide frontend behavioral data
- **`integrations/`**: Analytics platform integrations for event ingestion

### Open-Source vs Proprietary

**Open-source core:**
- Event normalization
- Session modeling
- Intent state definitions
- Rule-based inference
- Explainability primitives
- Plugin interfaces
- Clarity integration

**Proprietary extensions (planned):**
- Learned intent models
- Vertical-specific heuristics
- Advanced uncertainty modeling
- Real-time streaming inference
- Deep analytics integrations

## Examples

See the `examples/` directory for:
- `basic_inference.py`: Basic intent inference
- `ecommerce_session.py`: Full e-commerce session analysis
- `explain_intent.py`: Intent explanation and narratives
- `clarity_integration.py`: Microsoft Clarity integration example

## Documentation

- [Concepts](docs/concepts.md)
- [Intent States](docs/intent_states.md)
- [Schemas](docs/schemas.md)
- [Explainability](docs/explainability.md)
- [Plugins](docs/plugins.md)

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see our contributing guidelines (coming soon).
