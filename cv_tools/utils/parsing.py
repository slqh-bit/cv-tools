"""
Parsing helpers for CLI arguments and preset values.
"""

from typing import Any, Dict, List, Sequence, Tuple


def parse_value(text: str) -> Any:
    """
    Convert a string token to the most specific Python type it represents.

    Order of attempts: bool -> None -> int -> float -> WxH tuple -> str.

    Example:
        >>> parse_value('2.0')
        2.0
        >>> parse_value('8x8')
        (8, 8)
    """
    lowered = text.strip().lower()

    if lowered in ('true', 'yes', 'on'):
        return True
    if lowered in ('false', 'no', 'off'):
        return False
    if lowered in ('none', 'null'):
        return None

    try:
        return int(text)
    except ValueError:
        pass

    try:
        return float(text)
    except ValueError:
        pass

    if 'x' in lowered:
        try:
            return parse_size(text)
        except ValueError:
            pass

    return text


def parse_kv(tokens: Sequence[str]) -> Dict[str, Any]:
    """
    Parse ``key=value`` tokens into a dictionary with typed values.

    Args:
        tokens: Tokens such as ``['clip=2.0', 'tile=8x8']``

    Returns:
        Dict of parsed parameters

    Raises:
        ValueError: If a token is not in ``key=value`` form
    """
    params: Dict[str, Any] = {}
    for token in tokens:
        if '=' not in token:
            raise ValueError(f"Expected key=value, got: {token!r}")
        key, _, value = token.partition('=')
        key = key.strip()
        if not key:
            raise ValueError(f"Empty parameter name in: {token!r}")
        params[key] = parse_value(value)
    return params


def parse_size(text: str) -> Tuple[int, int]:
    """
    Parse a ``WxH`` string into an (width, height) integer pair.

    Example:
        >>> parse_size('800x600')
        (800, 600)
    """
    parts = text.lower().split('x')
    if len(parts) != 2:
        raise ValueError(f"Expected WxH, got: {text!r}")
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        raise ValueError(f"Expected integer dimensions in: {text!r}") from None


def parse_int_list(text: str, count: int) -> List[int]:
    """
    Parse a comma-separated list of exactly ``count`` integers.

    Example:
        >>> parse_int_list('100,100,300,200', 4)
        [100, 100, 300, 200]
    """
    parts = [p.strip() for p in text.split(',')]
    if len(parts) != count:
        raise ValueError(f"Expected {count} comma-separated values, got {len(parts)}: {text!r}")
    try:
        return [int(p) for p in parts]
    except ValueError:
        raise ValueError(f"Expected integers in: {text!r}") from None


def parse_float_list(text: str, count: int) -> List[float]:
    """
    Parse a comma-separated list of exactly ``count`` floats.

    Example:
        >>> parse_float_list('20,1.0,220', 3)
        [20.0, 1.0, 220.0]
    """
    parts = [p.strip() for p in text.split(',')]
    if len(parts) != count:
        raise ValueError(f"Expected {count} comma-separated values, got {len(parts)}: {text!r}")
    try:
        return [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Expected numbers in: {text!r}") from None


def parse_resize_spec(text: str) -> Dict[str, Any]:
    """
    Parse a resize specification into keyword arguments for ``filters.crop_resize.resize``.

    Accepted forms:
        - ``800x600``  -> exact size
        - ``800x``     -> width only, height follows aspect ratio
        - ``x600``     -> height only, width follows aspect ratio
        - ``50%``      -> scale factor
        - ``0.5``      -> scale factor

    Example:
        >>> parse_resize_spec('50%')
        {'scale': 0.5}
    """
    text = text.strip().lower()

    if text.endswith('%'):
        try:
            return {'scale': float(text[:-1]) / 100.0}
        except ValueError:
            raise ValueError(f"Invalid percentage: {text!r}") from None

    if 'x' in text:
        width_part, _, height_part = text.partition('x')
        spec: Dict[str, Any] = {}
        if width_part:
            spec['width'] = int(width_part)
        if height_part:
            spec['height'] = int(height_part)
        if not spec:
            raise ValueError(f"Invalid resize spec: {text!r}")
        return spec

    try:
        return {'scale': float(text)}
    except ValueError:
        raise ValueError(f"Invalid resize spec: {text!r}") from None
