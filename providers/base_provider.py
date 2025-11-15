"""
base_provider.py - Base class for all ad providers

All providers should inherit from this class and implement the required methods.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for ad providers"""
    
    def __init__(self, name, enabled=True):
        self.name = name
        self.enabled = enabled
        self.priority = 0  # Higher = more important
    
    @abstractmethod
    def fetch_ad(self, ad_format='native', user_country='ZA', view_count=0):
        """
        Fetch an ad from this provider
        
        Args:
            ad_format: Preferred ad format
            user_country: ISO country code
            view_count: Number of ads user has viewed
        
        Returns:
            Dict with ad data or None
        """
        pass
    
    @abstractmethod
    def track_impression(self, ad_id, user_id, impression_url=None):
        """Track when an ad is shown"""
        pass
    
    @abstractmethod
    def track_completion(self, ad_id, user_id, watch_time):
        """Track when an ad is completed"""
        pass
    
    def get_status(self):
        """Get provider status for startup logging"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'type': self.__class__.__name__
        }
