"""E-commerce specific event schemas."""

from typing import Dict, Any
from istari.schemas.base import BaseSchema
from istari.core.events import Event


class EcommerceSchema(BaseSchema):
    """Schema for e-commerce events."""
    
    # Common e-commerce event types
    EVENT_TYPES = {
        "page_view": "page_view",
        "product_view": "product_view",
        "add_to_cart": "add_to_cart",
        "remove_from_cart": "remove_from_cart",
        "checkout_started": "checkout_started",
        "checkout_completed": "checkout_completed",
        "purchase": "purchase",
        "cart_abandoned": "cart_abandoned",
    }
    
    def normalize(self, raw_event: Dict[str, Any]) -> Event:
        """Normalize e-commerce event."""
        timestamp = self.extract_timestamp(raw_event)
        user_id = self.extract_user_id(raw_event)
        session_id = self.extract_session_id(raw_event)
        event_type = self.extract_event_type(raw_event)
        properties = self.extract_properties(raw_event)
        
        # Normalize event type if needed
        event_type = self.EVENT_TYPES.get(event_type, event_type)
        
        return Event(
            event_type=event_type,
            timestamp=timestamp,
            user_id=user_id,
            session_id=session_id,
            properties=properties,
            source="ecommerce",
            raw_data=raw_event,
        )
    
    def extract_product_info(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information from event."""
        properties = self.extract_properties(raw_event)
        
        product_info = {}
        for key in ["product_id", "productId", "product", "item_id", "itemId"]:
            if key in properties:
                product_info["product_id"] = properties[key]
                break
        
        for key in ["product_name", "productName", "name"]:
            if key in properties:
                product_info["product_name"] = properties[key]
                break
        
        for key in ["price", "amount", "value"]:
            if key in properties:
                product_info["price"] = float(properties[key])
                break
        
        for key in ["category", "category_id"]:
            if key in properties:
                product_info["category"] = properties[key]
                break
        
        return product_info

