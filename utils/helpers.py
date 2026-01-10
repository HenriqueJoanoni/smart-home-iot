import time
from datetime import datetime
from typing import Dict, Any

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def safe_read(func, max_retries: int = 3, delay: float = 0.5):
    """
    Safely read from sensor with retries
    
    Args: 
        func: Function to call for reading
        max_retries:  Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns: 
        Reading value or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RuntimeError as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                return None
        except Exception: 
            return None
    return None

def create_sensor_message(
    sensor_type: str,
    value: float,
    unit: str,
    location: str,
    device_id: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create standardised sensor message for PubNub
    
    Args:
        sensor_type: Type of sensor (e.g., 'temperature')
        value:  Sensor reading value
        unit: Unit of measurement
        location: Device location
        device_id:  Unique device identifier
        metadata: Additional metadata
    
    Returns:
        Formatted message dictionary
    """
    message = {
        'timestamp': get_timestamp(),
        'sensor_type': sensor_type,
        'value': value,
        'unit': unit,
        'location': location,
        'device_id': device_id,
        'source': 'hardware' if not metadata or not metadata.get('simulated') else 'simulation'
    }
    
    if metadata:
        message['metadata'] = metadata
    
    return message