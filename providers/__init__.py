"""
providers/ - Ad Network Providers

Modular ad provider system for easy addition of new networks.
Each provider should inherit from BaseProvider and implement required methods.
"""

from .base_provider import BaseProvider
from .adsterra_provider import AdsterraProvider
from .demo_provider import DemoProvider
from .provider_manager import ProviderManager

__all__ = [
    'BaseProvider',
    'AdsterraProvider',
    'DemoProvider',
    'ProviderManager'
]
