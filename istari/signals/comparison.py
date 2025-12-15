"""Comparison behavior signal extraction."""

from typing import List, Dict, Any, Set
from istari.core.session import Session
from istari.core.events import Event


class ComparisonSignal:
    """Extracts comparison behavior signals from sessions."""
    
    def extract(self, session: Session) -> Dict[str, Any]:
        """
        Extract comparison signals.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary with comparison metrics
        """
        events = session.timeline.get_events()
        
        # Product views
        product_views = [e for e in events if e.event_type == "product_view"]
        unique_products = set()
        product_categories = set()
        
        for event in product_views:
            product_id = event.properties.get("product_id") or event.properties.get("productId")
            if product_id:
                unique_products.add(str(product_id))
            
            category = event.properties.get("category")
            if category:
                product_categories.add(str(category))
        
        # Comparison indicators
        multiple_products = len(unique_products) > 1
        multiple_categories = len(product_categories) > 1
        rapid_product_switching = self._detect_rapid_switching(product_views)
        
        return {
            "unique_products_viewed": len(unique_products),
            "unique_categories_viewed": len(product_categories),
            "is_comparing": multiple_products or multiple_categories,
            "rapid_switching": rapid_product_switching,
            "comparison_score": self._calculate_comparison_score(
                len(unique_products),
                len(product_categories),
                rapid_product_switching
            ),
        }
    
    def _detect_rapid_switching(self, product_views: List[Event]) -> bool:
        """Detect rapid switching between products."""
        if len(product_views) < 2:
            return False
        
        # Check if multiple products viewed within short time window
        from datetime import timedelta
        
        recent_products = set()
        for event in product_views[-5:]:  # Last 5 product views
            product_id = event.properties.get("product_id") or event.properties.get("productId")
            if product_id:
                recent_products.add(str(product_id))
        
        return len(recent_products) >= 2
    
    def _calculate_comparison_score(
        self,
        unique_products: int,
        unique_categories: int,
        rapid_switching: bool
    ) -> float:
        """Calculate a comparison score (0.0 to 1.0)."""
        score = 0.0
        
        # More products = higher score
        if unique_products >= 3:
            score += 0.5
        elif unique_products >= 2:
            score += 0.3
        
        # Multiple categories = higher score
        if unique_categories >= 2:
            score += 0.3
        
        # Rapid switching = higher score
        if rapid_switching:
            score += 0.2
        
        return min(1.0, score)

