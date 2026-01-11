import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.sensor_data import SensorReading


class SensorService:
    """Service for managing sensor readings"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_reading(self, message: Dict) -> Optional[List[SensorReading]]: 
        """
        Save sensor reading(s) from PubNub message
 
        Message format:
        {
            'type': 'sensor_data',
            'device_id': 'rpi-001',
            'location': 'living_room',
            'temperature': 22.5,      # ← Sensor 1
            'humidity': 55.0,         # ← Sensor 2
            'light': 450.0,           # ← Sensor 3
            'motion': True,           # ← Sensor 4
            'timestamp': '2025-01-01T12:00:00Z'
        }
        
        Args:
            message: PubNub sensor data message
        
        Returns:
            List of saved SensorReading objects or None if error
        """
        try: 
            # Extract common fields
            device_id = message.get('device_id', 'unknown')
            location = message.get('location', 'living_room')
            timestamp_str = message.get('timestamp')
            
            # Parse timestamp
            if timestamp_str:
                try: 
                    from dateutil.parser import parse
                    timestamp = parse(timestamp_str)
                except:
                    timestamp = datetime.now(timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)
            
            readings = []
            
            # Sensor mappings:  field_name -> (unit, sensor_type)
            sensor_mappings = {
                'temperature':  ('°C', 'temperature'),
                'humidity': ('%', 'humidity'),
                'light': ('lux', 'light'),
                'motion':  ('boolean', 'motion')
            }
            
            for field, (unit, sensor_type) in sensor_mappings.items():
                if field in message and message[field] is not None:
                    # Convert boolean motion to numeric
                    value = message[field]
                    if field == 'motion': 
                        value = 1.0 if value else 0.0
                    
                    # Create individual reading
                    reading = SensorReading(
                        timestamp=timestamp,
                        sensor_type=sensor_type,
                        value=float(value),
                        unit=unit,
                        location=location,
                        device_id=device_id,
                        meta=message.get('metadata', {})
                    )
                    
                    readings.append(reading)
                    db.session.add(reading)
            
            if not readings:
                self.logger.warning(f"No sensor data found in message: {message}")
                return None
            
            # Commit all readings
            db.session.commit()
            
            # Log success
            sensor_summary = ", ".join([f"{r.sensor_type}={r.value}{r.unit}" for r in readings])
            self.logger.info(f"Saved {len(readings)} readings: {sensor_summary}")
            
            return readings
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error saving sensor reading: {e}")
            db.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Error saving sensor reading: {e}")
            db.session.rollback()
            return None
    
    def get_latest_reading(self, sensor_type: str, device_id: str = None) -> Optional[SensorReading]:
        """Get latest reading for a sensor type"""
        try:
            query = SensorReading.query.filter_by(sensor_type=sensor_type)
            
            if device_id:
                query = query.filter_by(device_id=device_id)
            
            return query.order_by(SensorReading.timestamp.desc()).first()
            
        except Exception as e:
            self.logger.error(f"Error getting latest reading: {e}")
            return None