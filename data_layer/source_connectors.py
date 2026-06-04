"""Future deterministic source connectors.

Connectors must return raw tabular data and never make betting decisions.
"""


class ConnectorNotImplementedError(NotImplementedError):
    pass


def fetch_football_data() -> None:
    raise ConnectorNotImplementedError("Football-Data connector is reserved for a future release.")

