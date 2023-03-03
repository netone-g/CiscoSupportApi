def split_list(target: list, n: int):
    """Split a list into evenly sized chunks

    Args:
        target (list): list
        n (int): size

    Yields:
        Generator[list]: split list generator
    """
    for idx in range(0, len(target), n):
        yield target[idx : idx + n]


def filter_none_value_keys(d: dict) -> dict:
    """Filter keys with None from a dict

    Args:
        d (dict): dict

    Returns:
        dict: filtered dict
    """
    return dict(filter(lambda x: x[1] is not None, d.items()))
