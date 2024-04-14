__all__ = "PrivatesError", "AccessError", "FrameError"


class PrivatesError(Exception):
    """Base exception for all privates.py errors."""


class AccessError(PrivatesError):
    """Caller does not have access to the target."""


class FrameError(PrivatesError):
    """Failed to get the frame."""
