from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class SystemLog(db.Model):
    """Application logs and events"""
    
    __tablename__ = 'system_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(
        db.DateTime(timezone=True), 
        primary_key=True, 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    log_level = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column('metadata', JSONB, default={})
    
    def __repr__(self):
        return f'<SystemLog [{self.log_level}] {self.source}:  {self.message[:50]}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'log_level': self.log_level,
            'source': self.source,
            'message': self.message,
            'metadata': self.data or {}
        }