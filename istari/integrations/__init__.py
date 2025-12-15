"""Integration modules for analytics platforms."""

from istari.integrations.generic import GenericIntegration
from istari.integrations.mixpanel import MixpanelIntegration
from istari.integrations.amplitude import AmplitudeIntegration
from istari.integrations.segment import SegmentIntegration

__all__ = [
    "GenericIntegration",
    "MixpanelIntegration",
    "AmplitudeIntegration",
    "SegmentIntegration",
]

