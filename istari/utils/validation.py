"""Validation utility functions."""

from typing import Any, Dict, List, Optional
from istari.exceptions import EventValidationError


class ValidationUtils:
    """Utility functions for validation."""
    
    @staticmethod
    def validate_event_data(data: Dict[str, Any]) -> bool:
        """
        Validate event data structure.
        
        Args:
            data: Event data dictionary
        
        Returns:
            True if valid
        
        Raises:
            EventValidationError: If validation fails
        """
        required_fields = ["event_type", "timestamp", "user_id", "session_id"]
        
        for field in required_fields:
            if field not in data:
                raise EventValidationError(f"Missing required field: {field}")
            
            if not data[field]:
                raise EventValidationError(f"Field '{field}' cannot be empty")
        
        return True
    
    @staticmethod
    def validate_confidence(confidence: float) -> bool:
        """
        Validate confidence score.
        
        Args:
            confidence: Confidence value
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If confidence is out of range
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
        return True
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format.
        
        Args:
            session_id: Session ID string
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If session ID is invalid
        """
        if not session_id or not isinstance(session_id, str):
            raise ValueError("Session ID must be a non-empty string")
        
        if len(session_id) > 255:
            raise ValueError("Session ID must be 255 characters or less")
        
        return True
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """
        Validate user ID format.
        
        Args:
            user_id: User ID string
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If user ID is invalid
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")
        
        if len(user_id) > 255:
            raise ValueError("User ID must be 255 characters or less")
        
        return True
    
    @staticmethod
    def sanitize_string(value: Any, max_length: int = 1000) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: Value to sanitize
            max_length: Maximum length
        
        Returns:
            Sanitized string
        """
        if value is None:
            return ""
        
        str_value = str(value)
        if len(str_value) > max_length:
            return str_value[:max_length]
        
        return str_value

