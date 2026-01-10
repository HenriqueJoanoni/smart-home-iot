import logging
from datetime import datetime,timezone,timedelta
from typing import List, Optional, Dict
from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.sensor_data import SensorReading


class SensorService:
    """Service for managing sensor data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_reading(self, sensor_data: Dict) -> Optional[SensorReading]:
        """
        Save sensor reading to database
        
        Args:
            sensor_data: Dictionary with sensor data from PubNub
        
        Returns:
            Created SensorReading or None if error
        """
        try: 
            # Create model from PubNub message
            reading = SensorReading.from_pubnub_message(sensor_data)
            
            # Save to database
            db.session.add(reading)
            db.session.commit()
            
            self.logger.info(
                f"Saved sensor reading: {reading.sensor_type}="
                f"{reading.value}{reading.unit} from {reading.device_id}"
            )
            
            return reading
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error saving sensor reading: {e}")
            db.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Error saving sensor reading: {e}")
            db.session.rollback()
            return None
    
    def get_latest_reading(
        self,
        sensor_type: str,
        location: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> Optional[SensorReading]:
        """Get latest reading for sensor type"""
        try:
            query = SensorReading.query.filter_by(sensor_type=sensor_type)
            
            if location:
                query = query.filter_by(location=location)
            
            if device_id:
                query = query.filter_by(device_id=device_id)
            
            return query.order_by(desc(SensorReading.timestamp)).first()
            
        except Exception as e:
            self.logger.error(f"Error getting latest reading: {e}")
            return None
    
    def get_readings_in_range(
        self,
        sensor_type: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        limit: int = 1000
    ) -> List[SensorReading]:
        """Get sensor readings within time range"""
        try:
            if end_time is None:
                end_time = datetime.now(timezone.utc)
            
            query = SensorReading.query.filter(
                SensorReading.sensor_type == sensor_type,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time
            )
            
            if location:
                query = query.filter_by(location=location)
            
            return query.order_by(desc(SensorReading.timestamp)).limit(limit).all()
            
        except Exception as e:
            self.logger.error(f"Error getting readings in range: {e}")
            return []
    
    def get_statistics(
        self,
        sensor_type: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """Get statistics for sensor type in time range"""
        try: 
            if end_time is None: 
                end_time = datetime.now(timezone.utc)
            
            query = db.session.query(
                func.avg(SensorReading.value).label('avg'),
                func.min(SensorReading.value).label('min'),
                func.max(SensorReading.value).label('max'),
                func.stddev(SensorReading.value).label('stddev'),
                func.count(SensorReading.id).label('count')
            ).filter(
                SensorReading.sensor_type == sensor_type,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time
            )
            
            if location:
                query = query.filter(SensorReading.location == location)
            
            result = query.first()
            
            if result:
                return {
                    'sensor_type': sensor_type,
                    'avg':  float(result.avg) if result.avg else None,
                    'min': float(result.min) if result.min else None,
                    'max':  float(result.max) if result.max else None,
                    'stddev': float(result.stddev) if result.stddev else None,
                    'count': result.count,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return None
    
    def get_all_latest_readings(self) -> Dict[str, SensorReading]:
        """Get latest reading for each sensor type"""
        try: 
            # Get distinct sensor types
            sensor_types = db.session.query(
                SensorReading.sensor_type
            ).distinct().all()
            
            results = {}
            for (sensor_type,) in sensor_types:
                latest = self.get_latest_reading(sensor_type)
                if latest:
                    results[sensor_type] = latest
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting all latest readings: {e}")
            return {}