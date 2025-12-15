"""Base classes for plugins."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from istari.core.session import Session
from istari.core.intent_state import IntentState


class PluginBase(ABC):
    """Base class for all Istari plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize plugin.
        
        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Optional configuration dictionary
        """
        pass
    
    def cleanup(self):
        """Cleanup plugin resources."""
        pass


class Plugin(PluginBase):
    """
    Base class for intent inference plugins.
    
    Plugins can extend Istari's inference capabilities without modifying core code.
    """
    
    @abstractmethod
    def infer(self, session: Session) -> Optional[IntentState]:
        """
        Infer intent state for a session.
        
        Args:
            session: Session to analyze
        
        Returns:
            Intent state or None if plugin cannot infer
        """
        pass
    
    @abstractmethod
    def get_supported_states(self) -> list:
        """
        Get list of intent state types this plugin supports.
        
        Returns:
            List of state type strings
        """
        pass
    
    def get_priority(self) -> int:
        """
        Get plugin priority (higher = more important).
        
        Returns:
            Priority integer (default: 0)
        """
        return 0

