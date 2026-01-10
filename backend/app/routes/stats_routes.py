from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.extensions import db
from app.models.sensor_data import SensorReading
from app.models.alert import Alert

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """
    Get dashboard statistics
    
    Query params:
        hours: Time range in hours (default: 24)
    
    Returns:
        {
            "sensors": {
                "temperature": {"avg": 22.5, "min": 20, "max": 25, "count": 100},
                ... 
            },
            "alerts":  {
                "total": 5,
                "unresolved": 2,
                "by_severity": {... }
            }
        }
    """
    try:
        hours = int(request.args.get('hours', 24))
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Sensor stats
        sensor_stats = db.session.query(
            SensorReading.sensor_type,
            func.count(SensorReading.id).label('count'),
            func.avg(SensorReading.value).label('avg'),
            func.min(SensorReading.value).label('min'),
            func.max(SensorReading.value).label('max')
        ).filter(
            SensorReading.timestamp >= start_time
        ).group_by(SensorReading.sensor_type).all()
        
        sensors = {}
        for stat in sensor_stats:
            sensors[stat.sensor_type] = {
                'count': stat.count,
                'avg': round(float(stat.avg), 2) if stat.avg else None,
                'min': round(float(stat.min), 2) if stat.min else None,
                'max': round(float(stat.max), 2) if stat.max else None
            }
        
        # Alert stats
        total_alerts = Alert.query.filter(Alert.timestamp >= start_time).count()
        unresolved_alerts = Alert.query.filter(
            Alert.timestamp >= start_time,
            Alert.resolved == False
        ).count()
        
        alert_by_severity = db.session.query(
            Alert.severity,
            func.count(Alert.id)
        ).filter(
            Alert.timestamp >= start_time
        ).group_by(Alert.severity).all()
        
        return jsonify({
            'period_hours': hours,
            'sensors': sensors,
            'alerts':  {
                'total': total_alerts,
                'unresolved': unresolved_alerts,
                'by_severity': {severity: count for severity, count in alert_by_severity}
            }
        }), 200
        
    except Exception as e: 
        return jsonify({'error': str(e)}), 500