from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class DeviceState(db.Model):
    """Current state of devices"""
    
    __tablename__ = 'device_states'
    
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(50), nullable=False, unique=True)
    device_type = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    value = db.Column(JSONB, default={})
    last_updated = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_by = db.Column(db.String(100), default='system')
    meta = db.Column('metadata', JSONB, default={})
    
    def __repr__(self):
        return f'<DeviceState {self.device_name}={self.state}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'state': self.state,
            'value': self.value or {},
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'updated_by': self.updated_by,
            'metadata': self.meta or {}
        }


class DeviceHistory(db.Model):
    """Device state change history"""
    
    __tablename__ = 'device_history'
    
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), primary_key=True, nullable=False, default=datetime.now(timezone.utc))
    device_name = db.Column(db.String(50), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    previous_state = db.Column(db.String(20))
    new_state = db.Column(db.String(20), nullable=False)
    value = db.Column(JSONB, default={})
    changed_by = db.Column(db.String(100), default='system')
    reason = db.Column(db.Text)
    
    def __repr__(self):
        return f'<DeviceHistory {self.device_name}:  {self.previous_state}→{self.new_state}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'previous_state': self.previous_state,
            'new_state': self.new_state,
            'value':  self.value or {},
            'changed_by': self.changed_by,
            'reason': self.reason
        }