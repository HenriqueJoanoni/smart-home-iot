from abc import ABC, abstractmethod
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import setup_logger
except ImportError:
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


class BaseActuator(ABC):
    """
    Abstract base class for all actuators
    
    All actuator implementations should inherit from this class
    and implement turn_on() and turn_off() methods. 
    """
    
    def __init__(self, actuator_name: str):
        """
        Initialize base actuator
        
        Args: 
            actuator_name: Name/identifier of actuator (e.g., 'led_red', 'buzzer')
        """
        self.actuator_name = actuator_name
        self.logger = setup_logger(self.__class__.__name__)
        self.is_initialised = False
        self._state = 'off'  # 'on', 'off', or custom state
        
        # Statistics
        self._on_count = 0
        self._off_count = 0
    
    @abstractmethod
    def turn_on(self):
        """
        Turn actuator on
        
        Must be implemented by subclasses. 
        """
        pass
    
    @abstractmethod
    def turn_off(self):
        """
        Turn actuator off
        
        Must be implemented by subclasses.
        """
        pass
    
    def get_state(self) -> str:
        """
        Get current state
        
        Returns:
            Current state string ('on', 'off', or custom)
        """
        return self._state
    
    def is_on(self) -> bool:
        """Check if actuator is on"""
        return self._state == 'on'
    
    def is_off(self) -> bool:
        """Check if actuator is off"""
        return self._state == 'off'
    
    def get_actuator_info(self) -> dict:
        """
        Get actuator information
        
        Returns: 
            Dictionary with actuator metadata
        """
        return {
            'name': self.actuator_name,
            'initialised': self.is_initialised,
            'state': self._state,
            'on_count':  self._on_count,
            'off_count': self._off_count
        }
    
    def increment_on_count(self):
        """Increment 'turn on' counter"""
        self._on_count += 1
    
    def increment_off_count(self):
        """Increment 'turn off' counter"""
        self._off_count += 1
    
    def cleanup(self):
        """
        Clean up actuator resources
        
        Override this method if actuator needs cleanup (e.g., GPIO)
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
        return f"<{self.__class__.__name__} name={self.actuator_name} state={self._state} initialised={self.is_initialised}>"