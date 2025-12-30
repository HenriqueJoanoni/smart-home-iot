from abc import ABC, abstractmethod
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import setup_logger
except ImportError:
    # Fallback if logger not available
    import logging
    def setup_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


class BaseSensor(ABC):
    """
    Abstract base class for all sensors
    
    All sensor implementations should inherit from this class
    and implement the read() method.
    """
    
    def __init__(self, sensor_type: str, unit: str):
        """
        Initialise base sensor
        
        Args: 
            sensor_type: Type of sensor (e.g., 'temperature', 'light', 'motion')
            unit: Unit of measurement (e.g., '°C', 'lux', 'boolean')
        """
        self. sensor_type = sensor_type
        self.unit = unit
        self.logger = setup_logger(self.__class__.__name__)
        self.is_initialised = False
        
        # Statistics
        self._read_count = 0
        self._error_count = 0
    
    @abstractmethod
    def read(self):
        """
        Read sensor value
        
        Must be implemented by subclasses. 
        
        Returns:
            Sensor reading value(s) or None if error
        """
        pass
    
    def get_reading_with_unit(self) -> Optional[str]:
        """
        Get formatted reading with unit
        
        Returns:
            Formatted string like "22.5 °C" or None if error
        """
        value = self.read()
        if value is not None:
            if isinstance(value, tuple):
                # Multiple values (e.g., DHT22 returns temp + humidity)
                return str(value)
            else:
                return f"{value:. 1f} {self.unit}"
        return None
    
    def get_sensor_info(self) -> dict:
        """
        Get sensor information
        
        Returns:
            Dictionary with sensor metadata
        """
        return {
            'type': self.sensor_type,
            'unit': self.unit,
            'initialised': self.is_initialised,
            'read_count':  self._read_count,
            'error_count': self._error_count
        }
    
    def increment_read_count(self):
        """Increment successful read counter"""
        self._read_count += 1
    
    def increment_error_count(self):
        """Increment error counter"""
        self._error_count += 1
    
    def get_success_rate(self) -> float:
        """
        Calculate read success rate
        
        Returns: 
            Success rate as percentage (0-100)
        """
        total = self._read_count + self._error_count
        if total == 0:
            return 0.0
        return (self._read_count / total) * 100.0
    
    def cleanup(self):
        """
        Clean up sensor resources
        
        Override this method if sensor needs cleanup (e.g., GPIO)
        """
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup"""
        self.cleanup()
        return False
    
    def __repr__(self):
        """String representation"""
        return f"<{self.__class__.__name__} type={self.sensor_type} unit={self.unit} initialised={self.is_initialised}>"