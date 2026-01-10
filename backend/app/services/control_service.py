import logging
from app.config import Config
from app.extensions import db
from app.models.device_state import DeviceState


class ControlService:
    """Service for controlling devices"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def control_led(self, action, brightness=100):
        """
        Control LED
        
        Args:
            action: 'on', 'off', 'toggle'
            brightness: 0-100
        
        Returns:
            bool: Success
        """
        try:
            # Import here to avoid circular import
            from app.pubnub_handler import pubnub_handler
            
            if not pubnub_handler or not pubnub_handler.pubnub_service:
                self.logger.error("PubNub handler not initialized")
                return False
            
            # Create command message
            command = {
                'type': 'control_command',
                'device': 'led',
                'action':  action,
                'brightness': brightness if action == 'on' else None
            }
            
            # Publish to control channel
            success = pubnub_handler.pubnub_service.publish(
                Config.PUBNUB_CONTROL_CHANNEL,
                command
            )
            
            if success:
                self.logger.info(f"LED command sent: {action}")
                # Update device state in DB
                self._update_device_state('led', action, {'brightness': brightness})
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error controlling LED: {e}")
            return False
    
    def control_buzzer(self, action):
        """
        Control Buzzer
        
        Args:
            action: 'on', 'off', 'beep', 'alarm'
        
        Returns:
            bool: Success
        """
        try:
            from app.pubnub_handler import pubnub_handler
            
            if not pubnub_handler or not pubnub_handler.pubnub_service:
                self.logger.error("PubNub handler not initialized")
                return False
            
            command = {
                'type': 'control_command',
                'device': 'buzzer',
                'action': action
            }
            
            success = pubnub_handler.pubnub_service.publish(
                Config.PUBNUB_CONTROL_CHANNEL,
                command
            )
            
            if success: 
                self.logger.info(f"Buzzer command sent:  {action}")
                self._update_device_state('buzzer', action, {})
            
            return success
            
        except Exception as e: 
            self.logger.error(f"Error controlling buzzer: {e}")
            return False
    
    def get_device_status(self):
        """Get current device states"""
        try: 
            devices = DeviceState.query.all()
            
            status = {}
            for device in devices: 
                status[device.device_name] = device.to_dict()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting device status: {e}")
            return {}
    
    def _update_device_state(self, device_name, state, value):
        """Update device state in database"""
        try:
            device = DeviceState.query.filter_by(device_name=device_name).first()
            
            if device:
                device.state = state
                device.value = value
            else:
                device = DeviceState(
                    device_name=device_name,
                    device_type='actuator',
                    state=state,
                    value=value
                )
                db.session.add(device)
            
            db.session.commit()
            
        except Exception as e: 
            self.logger.error(f"Error updating device state: {e}")
            db.session.rollback()