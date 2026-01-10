from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.alert import Alert

alert_bp = Blueprint('alerts', __name__)


@alert_bp.route('/', methods=['GET'])
def get_alerts():
    """
    Get alerts
    
    Query params:
        resolved: true | false (optional, filter by resolved status)
        limit: Max records (default: 50)
    """
    try:
        # Get params
        resolved_param = request.args.get('resolved')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = Alert.query
        
        if resolved_param is not None:
            resolved = resolved_param.lower() == 'true'
            query = query.filter_by(resolved=resolved)
        
        # Execute
        alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'count': len(alerts),
            'alerts': [a.to_dict() for a in alerts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """
    Mark alert as resolved
    
    Body (optional):
        {
            "resolved_by": "user_name"
        }
    """
    try:
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Get resolver name
        data = request.get_json() or {}
        resolved_by = data.get('resolved_by', 'user')
        
        # Resolve
        from datetime import datetime, timezone
        alert.resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = resolved_by
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500