"""Wrapper around webhook helper functions."""

from oxeign.swagger.yard.yard_utils.yard_webhook import *  # noqa: F401,F403
# Import the helper from the top-level ``utils`` package, not from this
# package itself, to avoid a circular import when ``mybot.utils`` is
# initialised.
from utils.webhook import delete_webhook

__all__ = [*globals().get("__all__", []), "delete_webhook"]
