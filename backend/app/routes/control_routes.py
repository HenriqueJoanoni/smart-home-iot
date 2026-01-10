from flask import Blueprint, jsonify, request
from app.services.control_service import ControlService

control_bp = Blueprint('control', __name__)
control_service = ControlService()


@control_bp.route('/led', methods=['POST'])
def control_led():
    """
    Control LED
    
    Body:
        {
            "action": "on" | "off" | "toggle",
            "brightness": 0-100 (optional, for "on")
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'action' not in data:
            return jsonify({'error': 'Missing action'}), 400
        
        action = data['action']
        brightness = data.get('brightness', 100)
        
        # Send control command via PubNub
        success = control_service.control_led(action, brightness)
        
        if success:
            return jsonify({
                'success': True,
                'action': action,
                'brightness':  brightness if action == 'on' else None
            }), 200
        else:
            return jsonify({'error': 'Failed to send command'}), 500
            
    except Exception as e: 
        return jsonify({'error': str(e)}), 500


@control_bp.route('/buzzer', methods=['POST'])
def control_buzzer():
    """
    Control Buzzer
    
    Body:
        {
            "action": "on" | "off" | "beep" | "alarm"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'action' not in data:
            return jsonify({'error': 'Missing action'}), 400
        
        action = data['action']
        
        # Send control command via PubNub
        success = control_service.control_buzzer(action)
        
        if success:
            return jsonify({
                'success': True,
                'action': action
            }), 200
        else:
            return jsonify({'error': 'Failed to send command'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@control_bp.route('/status', methods=['GET'])
def get_device_status():
    """
    Get current device states
    
    Returns:
        {
            "led": {"state": "on", "brightness": 100},
            "buzzer": {"state": "off"}
        }
    """
    try:
        status = control_service.get_device_status()
        return jsonify(status), 200
        
    except Exception as e: 
        return jsonify({'error':  str(e)}), 500