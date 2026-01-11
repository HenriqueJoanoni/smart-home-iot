import logging
from datetime import datetime, timezone
from typing import Optional, Dict
from app.extensions import db
from app.models.device_state import DeviceState


class ControlService:
    """Service for controlling IoT devices"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _save_device_state(self, device_name: str, state: str, parameters: Dict = None):
        """
        Save device state to database
        
        Args: 
            device_name: Name of device (led, buzzer)
            state: Current state (on, off, etc)
            parameters: Additional parameters (brightness, etc)
        """
        try:
            # Find existing state or create new
            device_state = DeviceState.query.filter_by(device_name=device_name).first()
            
            if not device_state:
                device_state = DeviceState(device_name=device_name)
                db.session.add(device_state)
            
            # Update state
            device_state.state = state
            device_state.parameters = parameters or {}
            device_state.last_updated = datetime.now(timezone.utc)
            
            db.session.commit()
            
            self.logger.info(f"✅ Device state saved: {device_name} = {state}")
            return device_state
            
        except Exception as e:
            self.logger.error(f"Error saving device state: {e}")
            db.session.rollback()
            return None
    
    def _publish_state_change(self, device_name: str, state: str, parameters: Dict = None):
        """
        Publish state change via PubNub
        
        Args:
            device_name: Name of device
            state:  New state
            parameters: Additional parameters
        """
        try: 
            from app import pubnub_handler
            from app.config import Config
            
            if pubnub_handler and pubnub_handler.pubnub_service:
                message = {
                    'type':  'state_update',
                    'device': device_name,
                    'state': state,
                    'parameters': parameters or {},
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Publish to CONTROL channel so frontend can listen
                pubnub_handler.pubnub_service.publish(
                    channel=Config.PUBNUB_CONTROL_CHANNEL,
                    message=message
                )
                
                self.logger.info(f"✅ State change published: {device_name} = {state}")
        except Exception as e:
            self.logger.error(f"Error publishing state change: {e}")
    
    def control_buzzer(self, action: str, metadata: Dict = None) -> Dict:
        """Control buzzer device"""
        try: 
            # Validate action
            valid_actions = ['beep', 'alarm', 'on', 'off']
            if action not in valid_actions:
                return {
                    'success':  False,
                    'error':  f'Invalid action.Must be one of: {", ".join(valid_actions)}'
                }
            
            self.logger.info(f"Controlling buzzer: {action}")
            
            if action in ['on', 'off']:
                self._save_device_state('buzzer', action)
            
            # Send command via PubNub
            from app import pubnub_handler
            
            if pubnub_handler and pubnub_handler.pubnub_service:
                from app.config import Config
                
                message = {
                    'type': 'control_command',
                    'device': 'buzzer',
                    'action': action,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    **(metadata or {})
                }
                
                pubnub_handler.pubnub_service.publish(
                    channel=Config.PUBNUB_CONTROL_CHANNEL,
                    message=message
                )
                
                self.logger.info(f"✅ Buzzer command sent via PubNub: {action}")

            if action in ['on', 'off']: 
                self._publish_state_change('buzzer', action)
            
            return {
                'success': True,
                'action':  action,
                'device': 'buzzer',
                'state': action if action in ['on', 'off'] else None,
                'message': f'Buzzer {action} command sent'
            }
            
        except Exception as e: 
            self.logger.error(f"Error controlling buzzer: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def control_led(self, action: str, brightness: int = 100, metadata: Dict = None) -> Dict:
        """Control LED device"""
        try:
            # Validate action
            valid_actions = ['on', 'off', 'toggle']
            if action not in valid_actions:
                return {
                    'success': False,
                    'error': f'Invalid action.Must be one of: {", ".join(valid_actions)}'
                }
            
            # Validate brightness
            brightness = max(0, min(100, brightness))
            
            self.logger.info(f"Controlling LED: {action} (brightness: {brightness}%)")

            final_state = action
            if action == 'toggle': 
                # Get current state
                current = DeviceState.query.filter_by(device_name='led').first()
                if current and current.state == 'on': 
                    final_state = 'off'
                else: 
                    final_state = 'on'

            self._save_device_state('led', final_state, {'brightness':  brightness})
            
            # Send command via PubNub
            from app import pubnub_handler
            
            if pubnub_handler and pubnub_handler.pubnub_service:
                from app.config import Config
                
                message = {
                    'type': 'control_command',
                    'device':  'led',
                    'action': action,
                    'brightness': brightness,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    **(metadata or {})
                }
                
                pubnub_handler.pubnub_service.publish(
                    channel=Config.PUBNUB_CONTROL_CHANNEL,
                    message=message
                )
                
                self.logger.info(f"✅ LED command sent via PubNub:  {action}")

            self._publish_state_change('led', final_state, {'brightness':  brightness})
            
            return {
                'success': True,
                'action': action,
                'device': 'led',
                'state': final_state,
                'brightness': brightness,
                'message': f'LED {action} command sent'
            }
            
        except Exception as e:
            self.logger.error(f"Error controlling LED: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error':  str(e)
            }
    
    def get_device_status(self) -> Dict:
        """
        Get current device status from database
        
        Returns: 
            Dictionary with device states
        """
        try: 
            # Get LED state
            led_state = DeviceState.query.filter_by(device_name='led').first()
            led_data = {
                'state': led_state.state if led_state else 'off',
                'brightness':  led_state.parameters.get('brightness', 100) if led_state else 100,
                'last_updated': led_state.last_updated.isoformat() if led_state and led_state.last_updated else None
            }
            
            # Get Buzzer state
            buzzer_state = DeviceState.query.filter_by(device_name='buzzer').first()
            buzzer_data = {
                'state': buzzer_state.state if buzzer_state else 'off',
                'last_updated': buzzer_state.last_updated.isoformat() if buzzer_state and buzzer_state.last_updated else None
            }
            
            return {
                'led': led_data,
                'buzzer':  buzzer_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting device status: {e}")
            return {
                'led': {'state': 'unknown', 'brightness': 100},
                'buzzer': {'state': 'unknown'}
            }