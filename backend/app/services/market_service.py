def get_current_price(asset_name: str) -> float:
    """
    Temporary mock prices.
    Later this will call a real market API.
    """

    prices = {
        "INFY": 1985,
        "TCS": 3520,
        "RELIANCE": 2950,
        "HDFCBANK": 1840,
        "SBIN": 925,
    }

    return prices.get(asset_name.upper(), 0)