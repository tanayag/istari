"""Time utility functions."""

from datetime import datetime, timedelta
from typing import List, Optional


class TimeUtils:
    """Utility functions for time operations."""
    
    @staticmethod
    def parse_timestamp(value: any) -> datetime:
        """
        Parse various timestamp formats into datetime.
        
        Args:
            value: Timestamp value (int, float, str, or datetime)
        
        Returns:
            Datetime object
        """
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(value)
        
        if isinstance(value, str):
            # ISO format
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
            
            # Try common formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    pass
        
        raise ValueError(f"Could not parse timestamp: {value}")
    
    @staticmethod
    def calculate_duration(start: datetime, end: datetime) -> timedelta:
        """
        Calculate duration between two timestamps.
        
        Args:
            start: Start timestamp
            end: End timestamp
        
        Returns:
            Timedelta object
        """
        return end - start
    
    @staticmethod
    def get_time_gaps(timestamps: List[datetime]) -> List[timedelta]:
        """
        Get time gaps between consecutive timestamps.
        
        Args:
            timestamps: List of timestamps in chronological order
        
        Returns:
            List of timedelta objects
        """
        if len(timestamps) < 2:
            return []
        
        gaps = []
        for i in range(1, len(timestamps)):
            gap = timestamps[i] - timestamps[i-1]
            gaps.append(gap)
        
        return gaps
    
    @staticmethod
    def detect_long_pauses(
        timestamps: List[datetime],
        threshold_seconds: float = 60.0
    ) -> List[timedelta]:
        """
        Detect long pauses in a sequence of timestamps.
        
        Args:
            timestamps: List of timestamps
            threshold_seconds: Threshold for considering a pause "long"
        
        Returns:
            List of timedelta objects representing long pauses
        """
        gaps = TimeUtils.get_time_gaps(timestamps)
        return [g for g in gaps if g.total_seconds() > threshold_seconds]
    
    @staticmethod
    def format_duration(duration: timedelta) -> str:
        """
        Format a duration as a human-readable string.
        
        Args:
            duration: Timedelta object
        
        Returns:
            Formatted string (e.g., "5m 30s")
        """
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)

