from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class Alert(db.Model):
    """System alerts and warnings"""
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    sensor_type = db.Column(db.String(50))
    sensor_value = db.Column(db.Numeric(10, 2))
    threshold_value = db.Column(db.Numeric(10, 2))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime(timezone=True))
    resolved_by = db.Column(db.String(100))
    meta = db.Column('metadata', JSONB, default={})
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Alert {self.alert_type} [{self.severity}]>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'sensor_type': self.sensor_type,
            'sensor_value': float(self.sensor_value) if self.sensor_value else None,
            'threshold_value': float(self.threshold_value) if self.threshold_value else None,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'metadata': self.meta or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def from_pubnub_message(message):
        """
        Create Alert from PubNub message
        
        Expected message format:
        {
            'type': 'alert',
            'alert_type': 'HIGH_TEMPERATURE',
            'severity': 'warning',
            'message': 'Temperature 31.5°C exceeds threshold',
            'sensor_type': 'temperature',
            'value': 31.5,
            'threshold_value': 30.0,
            'device_id': 'rpi-001',
            'timestamp': '2025-01-01T12:00:00Z'
        }
        """
        timestamp_str = message.get('timestamp')
        if timestamp_str:
            try: 
                from dateutil.parser import parse
                timestamp = parse(timestamp_str)
            except:
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)
        
        alert_type = message.get('alert_type')

        if not alert_type:
            sensor_type = message.get('sensor_type', 'unknown')
            alert_type = f'ALERT_{sensor_type.upper()}'

        sensor_value = message.get('value') or message.get('sensor_value')
        title = message.get('title')

        if not title: 
            title = alert_type.replace('_', ' ').title()
        
        return Alert(
            timestamp=timestamp,
            alert_type=alert_type or 'UNKNOWN',
            severity=message.get('severity', 'info'),
            title=title or 'No Title',
            message=message.get('message'),
            sensor_type=message.get('sensor_type'),
            sensor_value=sensor_value,
            threshold_value=message.get('threshold_value'),
            meta=message.get('metadata', {})
        )