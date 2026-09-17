class MarketDataError(Exception):
    """Base exception for market-data errors."""


class NSEMarketDataError(MarketDataError):
    """Base exception for NSE market-data errors."""


class NSEAccessError(NSEMarketDataError):
    """Raised when NSE rejects access to the requested resource."""


class NSERateLimitError(NSEMarketDataError):
    """Raised when NSE rate-limits the client."""


class NSEServerError(NSEMarketDataError):
    """Raised when NSE returns a server-side error."""


class NSEConnectionError(NSEMarketDataError):
    """Raised when the NSE service cannot be reached."""