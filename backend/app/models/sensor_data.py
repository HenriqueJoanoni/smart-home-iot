from datetime import datetime,timezone
from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class SensorReading(db.Model):
    """Sensor readings time-series data"""
    
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), primary_key=True, nullable=False, default=datetime.now(timezone.utc))
    sensor_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), default='living_room')
    device_id = db.Column(db.String(100), default='raspberry_pi_main')
    meta = db.Column('metadata', JSONB, default={})
    
    def __repr__(self):
        return f'<SensorReading {self.sensor_type}={self.value}{self.unit} @ {self.timestamp}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sensor_type': self.sensor_type,
            'value':  float(self.value) if self.value else None,
            'unit': self.unit,
            'location': self.location,
            'device_id': self.device_id,
            'metadata': self.meta or {}
        }
    
    @staticmethod
    def from_pubnub_message(message):
        """
        Create SensorReading from PubNub message
        
        Expected message format:
        {
            'type': 'sensor_data',
            'device_id': 'rpi-001',
            'sensor_type':  'temperature',
            'value': 22.5,
            'unit':  '°C',
            'location': 'living_room',
            'timestamp': '2025-01-01T12:00:00Z',
            'metadata': {}
        }
        """
        # Parse timestamp
        timestamp_str = message.get('timestamp')
        if timestamp_str: 
            try:
                from dateutil.parser import parse
                timestamp = parse(timestamp_str)
            except:
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)
        
        return SensorReading(
            timestamp=timestamp,
            sensor_type=message.get('sensor_type'),
            value=message.get('value'),
            unit=message.get('unit'),
            location=message.get('location', 'living_room'),
            device_id=message.get('device_id', 'raspberry_pi_main'),
            meta=message.get('metadata', {})
        )