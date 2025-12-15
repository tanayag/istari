"""Price sensitivity signal extraction."""

from typing import List, Dict, Any, Optional
from istari.core.session import Session
from istari.core.events import Event


class PriceSignal:
    """Extracts price sensitivity signals from sessions."""
    
    def extract(self, session: Session) -> Dict[str, Any]:
        """
        Extract price sensitivity signals.
        
        Args:
            session: Session to analyze
        
        Returns:
            Dictionary with price sensitivity metrics
        """
        events = session.timeline.get_events()
        
        # Extract price-related events
        product_views = [e for e in events if e.event_type == "product_view"]
        add_to_cart_events = [e for e in events if e.event_type == "add_to_cart"]
        remove_from_cart_events = [e for e in events if e.event_type == "remove_from_cart"]
        
        # Price ranges viewed
        prices_viewed = []
        for event in product_views:
            price = self._extract_price(event)
            if price is not None:
                prices_viewed.append(price)
        
        # Price range of items added to cart
        cart_prices = []
        for event in add_to_cart_events:
            price = self._extract_price(event)
            if price is not None:
                cart_prices.append(price)
        
        # Price range of items removed from cart
        removed_prices = []
        for event in remove_from_cart_events:
            price = self._extract_price(event)
            if price is not None:
                removed_prices.append(price)
        
        # Calculate price sensitivity indicators
        price_range_viewed = self._calculate_range(prices_viewed)
        price_comparison = len(prices_viewed) > 1
        lower_price_preference = self._detect_lower_price_preference(
            prices_viewed, cart_prices, removed_prices
        )
        
        price_sensitivity_score = self._calculate_price_sensitivity_score(
            price_range_viewed,
            price_comparison,
            lower_price_preference,
            removed_prices
        )
        
        return {
            "prices_viewed": prices_viewed,
            "price_range": price_range_viewed,
            "price_comparison": price_comparison,
            "lower_price_preference": lower_price_preference,
            "price_sensitivity_score": price_sensitivity_score,
        }
    
    def _extract_price(self, event: Event) -> Optional[float]:
        """Extract price from event properties."""
        for key in ["price", "amount", "value", "cost"]:
            if key in event.properties:
                try:
                    return float(event.properties[key])
                except (ValueError, TypeError):
                    pass
        return None
    
    def _calculate_range(self, prices: List[float]) -> Optional[float]:
        """Calculate price range."""
        if not prices:
            return None
        return max(prices) - min(prices)
    
    def _detect_lower_price_preference(
        self,
        prices_viewed: List[float],
        cart_prices: List[float],
        removed_prices: List[float]
    ) -> bool:
        """Detect if user prefers lower-priced items."""
        if not prices_viewed or not cart_prices:
            return False
        
        avg_viewed = sum(prices_viewed) / len(prices_viewed)
        avg_cart = sum(cart_prices) / len(cart_prices)
        
        # If cart average is lower than viewed average, prefer lower prices
        return avg_cart < avg_viewed
    
    def _calculate_price_sensitivity_score(
        self,
        price_range: Optional[float],
        price_comparison: bool,
        lower_price_preference: bool,
        removed_prices: List[float]
    ) -> float:
        """Calculate price sensitivity score (0.0 to 1.0)."""
        score = 0.0
        
        if price_comparison:
            score += 0.3
        
        if lower_price_preference:
            score += 0.3
        
        if removed_prices:
            # Removing items might indicate price sensitivity
            score += 0.2
        
        if price_range and price_range > 0:
            # Large price range indicates price shopping
            if price_range > 100:  # Assuming currency units
                score += 0.2
        
        return min(1.0, score)

