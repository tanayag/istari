#!/usr/bin/env python3
"""Verify that Istari is properly installed and all modules are accessible."""

import sys

def verify_imports():
    """Verify all key modules can be imported."""
    errors = []
    
    # Core modules
    try:
        from istari.core import Event, Session, IntentState, Timeline
        print("✓ Core modules imported")
    except Exception as e:
        errors.append(f"Core modules: {e}")
    
    # Schemas
    try:
        from istari.schemas import BaseSchema, EcommerceSchema, WebSchema
        print("✓ Schema modules imported")
    except Exception as e:
        errors.append(f"Schema modules: {e}")
    
    # Inference
    try:
        from istari.inference import RuleBasedInference, IntentStateMachine
        print("✓ Inference modules imported")
    except Exception as e:
        errors.append(f"Inference modules: {e}")
    
    # Signals
    try:
        from istari.signals import DwellSignal, NavigationSignal, ComparisonSignal
        print("✓ Signal modules imported")
    except Exception as e:
        errors.append(f"Signal modules: {e}")
    
    # Explainability
    try:
        from istari.explainability import AttributionCalculator, NarrativeGenerator
        print("✓ Explainability modules imported")
    except Exception as e:
        errors.append(f"Explainability modules: {e}")
    
    # Sources (Clarity)
    try:
        from istari.sources import ClaritySource
        print("✓ Sources modules imported (Clarity)")
    except Exception as e:
        errors.append(f"Sources modules: {e}")
    
    # Integrations
    try:
        from istari.integrations import MixpanelIntegration, AmplitudeIntegration
        print("✓ Integration modules imported")
    except Exception as e:
        errors.append(f"Integration modules: {e}")
    
    # Plugins
    try:
        from istari.plugins import Plugin, PluginRegistry
        print("✓ Plugin modules imported")
    except Exception as e:
        errors.append(f"Plugin modules: {e}")
    
    # Utils
    try:
        from istari.utils import TimeUtils, MathUtils, ValidationUtils
        print("✓ Utility modules imported")
    except Exception as e:
        errors.append(f"Utility modules: {e}")
    
    # Main package
    try:
        import istari
        print(f"✓ Main package imported (version: {istari.__version__})")
    except Exception as e:
        errors.append(f"Main package: {e}")
    
    if errors:
        print("\n✗ Errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("\n✓ All modules imported successfully!")
    return True

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)

