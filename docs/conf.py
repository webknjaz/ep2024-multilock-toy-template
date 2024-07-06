"""Sphinx docs generation project configuration."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from sphinx.application import Sphinx


copyright = '@webknjaz (Sviatoslav Sydorenko)'
html_theme = 'furo'
project = 'Lokiverse'


def _identify_py38_eol_date() -> str:
    py38_lifecycle_details = requests.get(
        'https://endoflife.date/api/python/3.8.json',
        headers={'Accept': 'application/json'},
        timeout=5,
    )
    return py38_lifecycle_details.json()['eol']


def setup(app: Sphinx) -> dict[str, Any]:
    """Compute the ``|py38_eol_date|`` substitution dynamically."""
    app.config.rst_epilog = f"""
    .. |py38_eol_date| replace:: {_identify_py38_eol_date()}
    """

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
