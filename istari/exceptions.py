"""Custom exceptions for Istari."""


class IstariError(Exception):
    """Base exception for all Istari errors."""
    pass


class EventValidationError(IstariError):
    """Raised when an event fails validation."""
    pass


class SessionError(IstariError):
    """Raised when session operations fail."""
    pass


class IntentStateError(IstariError):
    """Raised when intent state operations fail."""
    pass


class TransitionError(IstariError):
    """Raised when state transitions are invalid."""
    pass


class SchemaError(IstariError):
    """Raised when schema operations fail."""
    pass


class InferenceError(IstariError):
    """Raised when inference operations fail."""
    pass


class PluginError(IstariError):
    """Raised when plugin operations fail."""
    pass


class IntegrationError(IstariError):
    """Raised when integration operations fail."""
    pass

