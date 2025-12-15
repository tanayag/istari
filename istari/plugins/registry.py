"""Plugin registry for managing plugins."""

from typing import Dict, List, Optional
from istari.plugins.base import Plugin
from istari.exceptions import PluginError


class PluginRegistry:
    """Registry for managing and executing plugins."""
    
    def __init__(self):
        """Initialize plugin registry."""
        self._plugins: Dict[str, Plugin] = {}
    
    def register(self, plugin: Plugin):
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance to register
        
        Raises:
            PluginError: If plugin is invalid or already registered
        """
        if not isinstance(plugin, Plugin):
            raise PluginError(f"Plugin must be an instance of Plugin, got {type(plugin)}")
        
        if plugin.name in self._plugins:
            raise PluginError(f"Plugin '{plugin.name}' is already registered")
        
        self._plugins[plugin.name] = plugin
    
    def unregister(self, name: str):
        """
        Unregister a plugin.
        
        Args:
            name: Plugin name
        """
        if name in self._plugins:
            plugin = self._plugins.pop(name)
            plugin.cleanup()
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)
    
    def get_all_plugins(self) -> List[Plugin]:
        """
        Get all registered plugins.
        
        Returns:
            List of all plugins, sorted by priority (descending)
        """
        plugins = list(self._plugins.values())
        plugins.sort(key=lambda p: p.get_priority(), reverse=True)
        return plugins
    
    def get_plugins_for_state(self, state_type: str) -> List[Plugin]:
        """
        Get plugins that support a specific state type.
        
        Args:
            state_type: Intent state type
        
        Returns:
            List of plugins that support this state type
        """
        plugins = []
        for plugin in self._plugins.values():
            if state_type in plugin.get_supported_states():
                plugins.append(plugin)
        
        plugins.sort(key=lambda p: p.get_priority(), reverse=True)
        return plugins
    
    def clear(self):
        """Clear all registered plugins."""
        for plugin in self._plugins.values():
            plugin.cleanup()
        self._plugins.clear()

