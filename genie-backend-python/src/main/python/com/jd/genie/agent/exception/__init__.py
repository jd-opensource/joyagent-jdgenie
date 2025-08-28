"""
Genie Agent Exception Module

This module contains custom exception classes for the Genie Agent system.
"""

from .token_limit_exceeded import TokenLimitExceeded

__all__ = [
    "TokenLimitExceeded",
]