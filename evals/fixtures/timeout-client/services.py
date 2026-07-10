from client import transport_timeout_seconds


def auth_timeout() -> float:
    return transport_timeout_seconds(250)


def profile_timeout() -> float:
    return transport_timeout_seconds(500)
