"""Errors raised by provider adapters."""


class ProviderError(RuntimeError):
    """Base class for errors from an external provider."""


class ProviderUnavailable(ProviderError):
    """The provider could not be reached or returned a server error."""


class ProviderAuthenticationError(ProviderError):
    """The provider rejected the configured credentials."""


class ProviderRateLimited(ProviderError):
    """The provider throttled the request."""


class ProviderNotFound(ProviderError):
    """The requested provider resource does not exist."""
