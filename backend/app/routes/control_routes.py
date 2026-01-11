from flask import Blueprint, jsonify, request
from app.services.control_service import ControlService

control_bp = Blueprint('control', __name__)
control_service = ControlService()


@control_bp.route('/led', methods=['POST'])
def control_led_endpoint():
    """
    Control LED
    
    Body: 
        {
            "action":  "on" | "off" | "toggle",
            "brightness": 100  (optional, 0-100)
        }
    """
    try:
        data = request.get_json() or {}
        action = data. get('action')
        brightness = data.get('brightness', 100)
        
        if not action:
            return jsonify({'error': 'Missing action parameter'}), 400
        
        result = control_service.control_led(action, brightness)
        
        if result. get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@control_bp.route('/buzzer', methods=['POST'])
def control_buzzer_endpoint():
    """
    Control Buzzer
    
    Body: 
        {
            "action": "beep" | "alarm" | "on" | "off"
        }
    """
    try:
        data = request.get_json() or {}
        action = data.get('action')
        
        if not action: 
            return jsonify({'error': 'Missing action parameter'}), 400
        
        result = control_service.control_buzzer(action)
        
        if result. get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@control_bp.route('/status', methods=['GET'])
def get_status_endpoint():
    """
    Get device status
    
    Returns current state of all devices
    """
    try:
        status = control_service.get_device_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500