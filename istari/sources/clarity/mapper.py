"""Map Clarity signals to Istari signals."""

from typing import Dict, Any, List, Optional
from istari.core.events import Event


class ClarityMapper:
    """
    Maps Clarity-specific behavioral signals to Istari signal categories.
    
    Clarity provides rich frontend behavioral data that maps to Istari's
    intent inference signals.
    """
    
    # Mapping from Clarity signals to Istari signal categories
    SIGNAL_MAPPINGS = {
        "rage_click": "friction.high",
        "dead_click": "intent.confusion",
        "scroll": "content_engagement",
        "quick_back_nav": "dissatisfaction",
        "excessive_hover": "hesitation",
    }
    
    def map_event(self, clarity_event: Event) -> Dict[str, Any]:
        """
        Map a Clarity event to Istari signal categories.
        
        Args:
            clarity_event: Normalized Clarity event
        
        Returns:
            Dictionary mapping Istari signal categories to values
        """
        signals = {}
        properties = clarity_event.properties
        
        # Rage clicks -> friction.high
        if clarity_event.event_type == "rage_click" or properties.get("is_rage_click"):
            signals["friction.high"] = self._calculate_rage_click_intensity(properties)
        
        # Dead clicks -> intent.confusion
        if clarity_event.event_type == "dead_click" or properties.get("is_dead_click"):
            signals["intent.confusion"] = 1.0
        
        # Scroll depth -> content_engagement
        if clarity_event.event_type == "scroll" or "scroll_depth" in properties:
            scroll_depth = properties.get("scroll_depth", 0)
            signals["content_engagement"] = self._normalize_scroll_depth(scroll_depth)
        
        # Quick back navigation -> dissatisfaction
        if self._is_quick_back_nav(clarity_event, properties):
            signals["dissatisfaction"] = 1.0
        
        # Excessive hover -> hesitation
        if clarity_event.event_type == "hover" or "hover_duration" in properties:
            hover_duration = properties.get("hover_duration", 0)
            if hover_duration > 3.0:  # 3 seconds threshold
                signals["hesitation"] = self._normalize_hover_duration(hover_duration)
        
        return signals
    
    def map_batch(self, clarity_events: List[Event]) -> Dict[str, Any]:
        """
        Map multiple Clarity events and aggregate signals.
        
        Args:
            clarity_events: List of normalized Clarity events
        
        Returns:
            Aggregated signal dictionary
        """
        aggregated_signals = {}
        
        for event in clarity_events:
            signals = self.map_event(event)
            for signal_type, value in signals.items():
                if signal_type not in aggregated_signals:
                    aggregated_signals[signal_type] = []
                aggregated_signals[signal_type].append(value)
        
        # Aggregate by taking maximum (most significant signal)
        result = {}
        for signal_type, values in aggregated_signals.items():
            result[signal_type] = max(values) if values else 0.0
        
        return result
    
    def _calculate_rage_click_intensity(self, properties: Dict[str, Any]) -> float:
        """Calculate intensity of rage click signal (0.0 to 1.0)."""
        click_count = properties.get("click_count", 0)
        
        # More clicks = higher friction
        if click_count >= 5:
            return 1.0
        elif click_count >= 3:
            return 0.8
        elif click_count >= 2:
            return 0.6
        else:
            return 0.4
    
    def _normalize_scroll_depth(self, scroll_depth: float) -> float:
        """
        Normalize scroll depth to engagement score (0.0 to 1.0).
        
        Args:
            scroll_depth: Scroll depth percentage (0-100)
        
        Returns:
            Normalized engagement score
        """
        if scroll_depth >= 90:
            return 1.0
        elif scroll_depth >= 75:
            return 0.9
        elif scroll_depth >= 50:
            return 0.7
        elif scroll_depth >= 25:
            return 0.5
        else:
            return 0.3
    
    def _is_quick_back_nav(self, event: Event, properties: Dict[str, Any]) -> bool:
        """Detect quick back navigation (indicates dissatisfaction)."""
        if event.event_type != "navigation":
            return False
        
        # Check if navigation timing suggests quick back
        nav_timing = properties.get("navigation_timing", {})
        if isinstance(nav_timing, dict):
            duration = nav_timing.get("duration", 0)
            # If user navigated away quickly (< 5 seconds), likely dissatisfaction
            if duration > 0 and duration < 5.0:
                return True
        
        # Check referrer/back button usage
        if properties.get("is_back_navigation") or properties.get("referrer_type") == "back":
            return True
        
        return False
    
    def _normalize_hover_duration(self, hover_duration: float) -> float:
        """
        Normalize hover duration to hesitation score (0.0 to 1.0).
        
        Args:
            hover_duration: Hover duration in seconds
        
        Returns:
            Normalized hesitation score
        """
        # Excessive hover (> 3s) indicates hesitation
        if hover_duration >= 10:
            return 1.0
        elif hover_duration >= 7:
            return 0.9
        elif hover_duration >= 5:
            return 0.7
        elif hover_duration >= 3:
            return 0.5
        else:
            return 0.0
    
    def get_signal_explanation(self, signal_type: str) -> str:
        """
        Get human-readable explanation for a signal mapping.
        
        Args:
            signal_type: Istari signal type (e.g., "friction.high")
        
        Returns:
            Explanation string
        """
        explanations = {
            "friction.high": "Rage clicks detected - user experiencing high friction",
            "intent.confusion": "Dead clicks detected - user intent is unclear",
            "content_engagement": "Scroll depth indicates content engagement level",
            "dissatisfaction": "Quick back navigation suggests dissatisfaction",
            "hesitation": "Excessive hover time indicates hesitation",
        }
        
        return explanations.get(signal_type, f"Signal: {signal_type}")

