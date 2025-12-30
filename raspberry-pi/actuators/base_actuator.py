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
    """Abstract base class for all actuators"""
    
    def __init__(self, actuator_type: str):
        """
        Initialise base actuator
        
        Args: 
            actuator_type: Type of actuator (e.g., 'led', 'buzzer')
        """
        self.actuator_type = actuator_type
        self.logger = setup_logger(self.__class__.__name__)
        self.is_initialised = False
        self._state = 'off'
    
    @abstractmethod
    def turn_on(self):
        """Turn actuator on"""
        pass
    
    @abstractmethod
    def turn_off(self):
        """Turn actuator off"""
        pass
    
    @property
    def state(self) -> str:
        """Get current state"""
        return self._state
    
    @property
    def is_on(self) -> bool:
        """Check if actuator is on"""
        return self._state == 'on'
    
    def cleanup(self):
        """Clean up actuator resources (override if needed)"""
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
        return f"<{self.__class__.__name__} type={self.actuator_type} state={self._state}>"