"""Math utility functions."""

from typing import List, Optional


class MathUtils:
    """Utility functions for mathematical operations."""
    
    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a value to 0.0-1.0 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum possible value
            max_val: Maximum possible value
        
        Returns:
            Normalized value between 0.0 and 1.0
        """
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    @staticmethod
    def calculate_mean(values: List[float]) -> Optional[float]:
        """
        Calculate mean of a list of values.
        
        Args:
            values: List of numeric values
        
        Returns:
            Mean value or None if list is empty
        """
        if not values:
            return None
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_median(values: List[float]) -> Optional[float]:
        """
        Calculate median of a list of values.
        
        Args:
            values: List of numeric values
        
        Returns:
            Median value or None if list is empty
        """
        if not values:
            return None
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    @staticmethod
    def calculate_std_dev(values: List[float]) -> Optional[float]:
        """
        Calculate standard deviation of a list of values.
        
        Args:
            values: List of numeric values
        
        Returns:
            Standard deviation or None if list is empty
        """
        if not values:
            return None
        
        mean = MathUtils.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp a value between min and max.
        
        Args:
            value: Value to clamp
            min_val: Minimum value
            max_val: Maximum value
        
        Returns:
            Clamped value
        """
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def weighted_average(values: List[float], weights: List[float]) -> Optional[float]:
        """
        Calculate weighted average.
        
        Args:
            values: List of values
            weights: List of weights (must match length of values)
        
        Returns:
            Weighted average or None if lists are empty or mismatched
        """
        if not values or not weights or len(values) != len(weights):
            return None
        
        total_weight = sum(weights)
        if total_weight == 0:
            return None
        
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        return weighted_sum / total_weight

