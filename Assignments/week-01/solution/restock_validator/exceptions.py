"""Custom exception hierarchy for the restock manifest loader.

Two levels, same shape as this week's support_api.store exceptions: a
base class every caller can catch generically, plus a specific subclass
for the one failure mode that needs its own handling.
"""


class ManifestError(Exception):
    """Base class for every error this module raises — callers can catch just this one type."""


class ManifestNotFoundError(ManifestError):
    """Raised when the manifest file does not exist on disk."""
