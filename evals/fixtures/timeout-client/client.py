def transport_timeout_seconds(timeout_ms: int) -> float:
    """Convert the public millisecond timeout for the seconds-based transport."""
    return float(timeout_ms)
