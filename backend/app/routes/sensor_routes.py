from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.sensor_data import SensorReading

sensor_bp = Blueprint('sensors', __name__)


@sensor_bp.route('/latest', methods=['GET'])
def get_latest_readings():
    """
    Get latest reading for each sensor type
    
    Returns:
        {
            "temperature": {... },
            "humidity": {...},
            "light": {...}
        }
    """
    try:
        # Get distinct sensor types
        sensor_types = db.session.query(
            SensorReading.sensor_type
        ).distinct().all()
        
        results = {}
        for (sensor_type,) in sensor_types:
            latest = SensorReading.query.filter_by(sensor_type=sensor_type) \
                .order_by(SensorReading.timestamp.desc()) \
                .first()
            
            if latest: 
                results[sensor_type] = latest.to_dict()
        
        return jsonify(results), 200
        
    except Exception as e: 
        return jsonify({'error': str(e)}), 500


@sensor_bp.route('/<sensor_type>/history', methods=['GET'])
def get_sensor_history(sensor_type):
    """
    Get sensor history for charts
    
    Query params:
        hours:  Number of hours (default: 24)
        limit: Max records (default: 100)
    
    Returns:
        {
            "sensor_type": "temperature",
            "count": 50,
            "readings": [...]
        }
    """
    try:
        # Get params
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 100))
        
        # Calculate time range
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Query
        readings = SensorReading.query.filter(
            SensorReading.sensor_type == sensor_type,
            SensorReading.timestamp >= start_time
        ).order_by(SensorReading.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'sensor_type': sensor_type,
            'count': len(readings),
            'readings': [r.to_dict() for r in readings]
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500