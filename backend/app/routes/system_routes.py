from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.system_log import SystemLog
import logging

system_bp = Blueprint('system', __name__)

@system_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """
    Get system logs
    
    Query params:
        level:  Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        source: Filter by source (e.g., 'PubNubHandler')
        hours: Time range in hours (default: 24)
        limit: Max records (default: 100)
    """
    try:
        # Get params
        level = request.args.get('level')
        source = request.args.get('source')
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 100))
        
        # Build query
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = SystemLog.query.filter(SystemLog.timestamp >= start_time)
        
        if level:
            query = query.filter_by(log_level=level.upper())
        
        if source:
            query = query.filter_by(source=source)
        
        # Execute
        logs = query.order_by(SystemLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'count': len(logs),
            'logs': [log.to_dict() for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@system_bp.route('/logs/summary', methods=['GET'])
def get_logs_summary():
    """
    Get log summary statistics
    
    Query params:
        hours: Time range (default: 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Count by level
        level_counts = db.session.query(
            SystemLog.log_level,
            db.func.count(SystemLog.id)
        ).filter(
            SystemLog.timestamp >= start_time
        ).group_by(SystemLog.log_level).all()
        
        # Count by source
        source_counts = db.session.query(
            SystemLog.source,
            db.func.count(SystemLog.id)
        ).filter(
            SystemLog.timestamp >= start_time
        ).group_by(SystemLog.source).order_by(
            db.func.count(SystemLog.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'period_hours': hours,
            'by_level': {level: count for level, count in level_counts},
            'top_sources': {source: count for source, count in source_counts}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500