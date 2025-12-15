"""Friction signal extraction."""

from typing import List, Dict, Any
from datetime import timedelta
from istari.core.session import Session
from istari.core.events import Event


class FrictionSignal:
    """Extracts friction and uncertainty signals from sessions."""
    
    def extract(self, session: Session) -> Dict[str, Any]:
        """
        Extract friction signals.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary with friction metrics
        """
        events = session.timeline.get_events()
        
        # Form abandonment
        form_starts = len([e for e in events if e.event_type == "form_start"])
        form_submits = len([e for e in events if e.event_type == "form_submit"])
        form_abandonment = form_starts > form_submits
        
        # Cart abandonment
        add_to_cart = len([e for e in events if e.event_type == "add_to_cart"])
        remove_from_cart = len([e for e in events if e.event_type == "remove_from_cart"])
        checkout_started = len([e for e in events if e.event_type == "checkout_started"])
        cart_abandonment = add_to_cart > 0 and checkout_started == 0
        
        # Long pauses (hesitation)
        long_pauses = self._detect_long_pauses(session)
        
        # Back navigation (uncertainty)
        back_nav = self._count_back_navigation(events)
        
        # Error events
        error_events = len([e for e in events if "error" in e.event_type.lower()])
        
        friction_score = self._calculate_friction_score(
            form_abandonment,
            cart_abandonment,
            long_pauses,
            back_nav,
            error_events
        )
        
        return {
            "form_abandonment": form_abandonment,
            "cart_abandonment": cart_abandonment,
            "long_pauses": long_pauses,
            "back_navigation": back_nav,
            "error_events": error_events,
            "friction_score": friction_score,
        }
    
    def _detect_long_pauses(self, session: Session, threshold_seconds: float = 60.0) -> int:
        """Detect long pauses in activity."""
        gaps = session.timeline.get_time_gaps()
        return len([g for g in gaps if g.total_seconds() > threshold_seconds])
    
    def _count_back_navigation(self, events: List[Event]) -> int:
        """Count back navigation events."""
        page_views = [e for e in events if e.event_type == "page_view"]
        if len(page_views) < 2:
            return 0
        
        back_nav = 0
        seen_pages = set()
        
        for event in page_views:
            page = event.properties.get("page", "unknown")
            if page in seen_pages:
                back_nav += 1
            seen_pages.add(page)
        
        return back_nav
    
    def _calculate_friction_score(
        self,
        form_abandonment: bool,
        cart_abandonment: bool,
        long_pauses: int,
        back_nav: int,
        error_events: int
    ) -> float:
        """Calculate overall friction score (0.0 to 1.0)."""
        score = 0.0
        
        if form_abandonment:
            score += 0.3
        if cart_abandonment:
            score += 0.3
        if long_pauses > 0:
            score += min(0.2, long_pauses * 0.05)
        if back_nav > 0:
            score += min(0.15, back_nav * 0.05)
        if error_events > 0:
            score += min(0.15, error_events * 0.1)
        
        return min(1.0, score)

