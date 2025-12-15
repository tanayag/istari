"""Navigation pattern signal extraction."""

from typing import List, Dict, Any, Set
from istari.core.session import Session
from istari.core.events import Event


class NavigationSignal:
    """Extracts navigation pattern signals from sessions."""
    
    def extract(self, session: Session) -> Dict[str, Any]:
        """
        Extract navigation signals.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary with navigation metrics
        """
        events = session.timeline.get_events()
        page_views = [e for e in events if e.event_type == "page_view"]
        
        # Unique pages visited
        unique_pages = set()
        page_sequence = []
        
        for event in page_views:
            page = event.properties.get("page", "unknown")
            unique_pages.add(page)
            page_sequence.append(page)
        
        # Detect loops (returning to same page)
        loops = self._detect_loops(page_sequence)
        
        # Calculate navigation depth
        depth = len(unique_pages)
        
        # Detect back navigation
        back_nav_count = self._count_back_navigation(page_sequence)
        
        return {
            "unique_pages": len(unique_pages),
            "total_page_views": len(page_views),
            "navigation_depth": depth,
            "loops_detected": loops,
            "back_navigation_count": back_nav_count,
            "page_sequence": page_sequence,
        }
    
    def _detect_loops(self, page_sequence: List[str]) -> int:
        """Detect navigation loops (returning to previously visited pages)."""
        visited = set()
        loops = 0
        
        for page in page_sequence:
            if page in visited:
                loops += 1
            visited.add(page)
        
        return loops
    
    def _count_back_navigation(self, page_sequence: List[str]) -> int:
        """Count back navigation events."""
        if len(page_sequence) < 2:
            return 0
        
        back_nav = 0
        for i in range(1, len(page_sequence)):
            # Simple heuristic: if we see a page we've seen before recently
            current_page = page_sequence[i]
            recent_pages = set(page_sequence[max(0, i-3):i])
            
            if current_page in recent_pages:
                back_nav += 1
        
        return back_nav
    
    def get_navigation_path(self, session: Session) -> List[str]:
        """
        Get the navigation path (sequence of pages).
        
        Args:
            session: Session to analyze
        
        Returns:
            List of page names in order
        """
        events = session.timeline.get_events()
        page_views = [e for e in events if e.event_type == "page_view"]
        
        return [e.properties.get("page", "unknown") for e in page_views]

