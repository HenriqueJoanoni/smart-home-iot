import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.alert import Alert


class AlertService: 
    """Service for managing alerts"""
    
    # Threshold values (from config)
    THRESHOLDS = {
        'temperature': {'high': 30.0, 'low': 15.0},
        'humidity':  {'high': 70.0, 'low': 30.0},
        'light': {'low': 50.0}
    }
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_alert(self, alert_data: Dict) -> Optional[Alert]: 
        """Save alert to database"""
        try: 
            if not alert_data.get('alert_type'):
                self.logger.error(f"Cannot save alert without alert_type: {alert_data}")
                return None
            
            alert = Alert.from_pubnub_message(alert_data)
            
            db.session.add(alert)
            db.session.commit()
            
            self.logger.warning(
                f"Alert created: [{alert.severity}] {alert.alert_type} - {alert.message}"
            )
            
            return alert
            
        except SQLAlchemyError as e: 
            self.logger.error(f"Database error saving alert: {e}")
            db.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Error saving alert: {e}")
            db.session.rollback()
            return None
    
    def check_thresholds(self, sensor_type: str, value: float, device_id: str = None) -> Optional[Alert]:
        """Check if sensor value violates thresholds and create alert"""
        if sensor_type not in self.THRESHOLDS:
            return None
        
        thresholds = self.THRESHOLDS[sensor_type]
        alert_data = None

        # Check high threshold
        if 'high' in thresholds and value > thresholds['high']: 
            alert_data = {
                'type': 'alert',
                # 'alert_type': f'HIGH_{sensor_type.upper()}',
                'alert_type': 'HIGH_TEMPERATURE',
                'severity': 'warning',
                'message': f'{sensor_type.capitalize()} {value} exceeds threshold of {thresholds["high"]}',
                'sensor_type': sensor_type,
                'value': value,
                'threshold_value': thresholds['high'],
                'device_id': device_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        elif 'low' in thresholds and value < thresholds['low']:
            alert_data = {
                'type': 'alert',
                # 'alert_type': f'LOW_{sensor_type.upper()}',
                'alert_type': 'LOW_TEMPERATURE',
                'severity': 'info',
                'message': f'{sensor_type.capitalize()} {value} below threshold of {thresholds["low"]}',
                'sensor_type': sensor_type,
                'value': value,
                'threshold_value': thresholds['low'],
                'device_id': device_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        if alert_data:
            return self.save_alert(alert_data)
        
        return None
    
    def get_unresolved_alerts(self, limit: int = 100) -> List[Alert]:
        """Get unresolved alerts"""
        try:
            return Alert.query.filter_by(resolved=False) \
                .order_by(desc(Alert.timestamp)) \
                .limit(limit) \
                .all()
        except Exception as e:
            self.logger.error(f"Error getting unresolved alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id: int, resolved_by: str = 'system') -> bool:
        """Mark alert as resolved"""
        try: 
            alert = Alert.query.get(alert_id)
            if alert:
                alert.resolved = True
                alert.resolved_at = datetime.now(timezone.utc)
                alert.resolved_by = resolved_by
                db.session.commit()
                self.logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            db.session.rollback()
            return False