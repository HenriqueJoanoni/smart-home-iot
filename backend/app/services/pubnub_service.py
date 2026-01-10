import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Callable, Any
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory


class PubNubService:  
    """
    PubNub service for real-time IoT communication
    """
    
    def __init__(
        self,
        publish_key: str,
        subscribe_key: str,
        uuid: str,
        secret_key: Optional[str] = None,
        enable_logging: bool = True
    ):
        """
        Initialize PubNub service
        
        Args:
            publish_key: PubNub publish key
            subscribe_key: PubNub subscribe key
            uuid:   Unique identifier for this client
            enable_logging: Enable PubNub logging
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configure PubNub
        pnconfig = PNConfiguration()
        pnconfig.publish_key = publish_key
        pnconfig.subscribe_key = subscribe_key
        pnconfig.uuid = uuid
        pnconfig.ssl = True
        
        if secret_key:
            pnconfig.secret_key = secret_key
            self.logger.info("Using Secret Key for Authentication")
        
        self.pubnub = PubNub(pnconfig)
        self.is_subscribed = False
        
        # Message handlers
        self._message_handlers: Dict[str, Callable] = {}
        self._presence_handlers: Dict[str, Callable] = {}
        
        self.logger.info(f"PubNub service initialized with UUID: {uuid}")
    
    def publish(
        self,
        channel: str,
        message: Dict[str, Any],
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Publish message to channel
        
        Args:
            channel: Channel name
            message:   Message payload (will be JSON serialized)
            metadata: Optional metadata
        
        Returns:
            True if published successfully
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Publish
            envelope = self.pubnub.publish() \
                .channel(channel) \
                .message(message) \
                .meta(metadata) \
                .sync()
            
            if envelope.status.is_error():
                self.logger.error(f"Failed to publish to {channel}: {envelope.status.error_data}")
                return False
            
            self.logger.debug(f"Published to {channel}: {message}")
            return True
            
        except Exception as e:  
            self.logger.error(f"Error publishing to {channel}: {e}")
            return False
    
    def subscribe(
        self,
        channels: list[str],
        callback: Optional[SubscribeCallback] = None,
        with_presence: bool = True
    ):
        """
        Subscribe to channels
        
        Args:
            channels: List of channel names
            callback:  Callback handler (if None, uses default)
            with_presence:  Enable presence tracking
        """
        try: 
            # Use provided callback or default
            if callback is None:
                callback = self._create_default_callback()
            
            self.pubnub.add_listener(callback)
            
            # Subscribe
            subscribe_call = self.pubnub.subscribe()
            for channel in channels:
                subscribe_call.channels(channel)
            
            if with_presence:
                subscribe_call.with_presence()
            
            subscribe_call.execute()
            
            self.is_subscribed = True
            self.logger.info(f"Subscribed to channels: {channels}")
            
        except Exception as e:
            self.logger.error(f"Error subscribing to channels: {e}")
    
    def unsubscribe(self, channels:   list[str]):
        """Unsubscribe from channels"""
        try:
            self.pubnub.unsubscribe() \
                .channels(channels) \
                .execute()
            
            self.logger.info(f"Unsubscribed from channels: {channels}")
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing:   {e}")
    
    def unsubscribe_all(self):
        """Unsubscribe from all channels"""
        try:  
            self.pubnub.unsubscribe_all()
            self.is_subscribed = False
            self.logger.info("Unsubscribed from all channels")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from all:   {e}")
    
    def add_message_handler(self, channel: str, handler:  Callable):
        """
        Add message handler for specific channel
        
        Args:  
            channel: Channel name
            handler: Function to call when message received
        """
        self._message_handlers[channel] = handler
        self.logger.debug(f"Added message handler for channel: {channel}")
    
    def add_presence_handler(self, channel: str, handler: Callable):
        """Add presence handler for specific channel"""
        self._presence_handlers[channel] = handler
        self.logger.debug(f"Added presence handler for channel: {channel}")
    
    def _create_default_callback(self):
        """Create default subscribe callback"""
        service = self
        
        class DefaultCallback(SubscribeCallback):
            def status(self, pubnub, status):
                if status.category == PNStatusCategory.PNConnectedCategory:
                    service.logger.info("✅ Connected to PubNub")
                elif status.category == PNStatusCategory.PNReconnectedCategory:
                    service.logger.info("🔄 Reconnected to PubNub")
                elif status.category == PNStatusCategory.PNDisconnectedCategory: 
                    service.logger.warning("⚠️ Disconnected from PubNub")
                elif status.is_error():
                    service.logger.error(f"❌ PubNub error: {status.error_data}")
            
            def message(self, pubnub, message):
                channel = message.channel
                payload = message.message
                
                service.logger.debug(f"📨 Message on {channel}: {payload}")
                
                # Call specific handler if registered
                if channel in service._message_handlers:
                    try:
                        service._message_handlers[channel](payload)
                    except Exception as e:
                        service.logger.error(f"Error in message handler for {channel}: {e}")
            
            def presence(self, pubnub, presence):
                channel = presence.channel
                event = presence.event
                uuid = presence.uuid
                
                service.logger.info(f"👤 Presence on {channel}:   {uuid} {event}")
                
                # Call specific handler if registered
                if channel in service._presence_handlers:
                    try:
                        service._presence_handlers[channel](presence)
                    except Exception as e:
                        service.logger.error(f"Error in presence handler:   {e}")
        
        return DefaultCallback()
    
    def get_channel_members(self, channel: str) -> list: 
        """
        Get list of members currently on channel
        
        Args:
            channel: Channel name
        
        Returns:
            List of UUIDs currently present
        """
        try:
            envelope = self.pubnub.here_now() \
                .channels(channel) \
                .include_uuids(True) \
                .sync()
            
            if channel in envelope.result.channels:
                occupants = envelope.result.channels[channel].occupants
                return [occ.uuid for occ in occupants]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting channel members:   {e}")
            return []
    
    def stop(self):
        """Stop PubNub service"""
        try:
            self.unsubscribe_all()
            self.pubnub.stop()
            self.logger.info("PubNub service stopped")
        except Exception as e:  
            self.logger.error(f"Error stopping PubNub:  {e}")


# ====================================
# HELPER FUNCTIONS
# ====================================

def create_sensor_message(
    device_id: str,
    sensor_type: str,
    value: float,
    unit: str,
    location: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """Create standardized sensor data message"""
    return {
        'type': 'sensor_data',
        'device_id': device_id,
        'sensor_type': sensor_type,
        'value': value,
        'unit': unit,
        'location': location,
        'metadata': metadata or {},
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def create_control_message(
    device_id: str,
    command: str,
    parameters: Optional[Dict] = None
) -> Dict:
    """Create standardized control command message"""
    return {
        'type': 'control_command',
        'device_id': device_id,
        'command': command,
        'parameters': parameters or {},
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def create_alert_message(
    alert_type: str,
    severity: str,
    message: str,
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    value: Optional[float] = None
) -> Dict:
    """Create standardized alert message"""
    return {
        'type': 'alert',
        'alert_type': alert_type,
        'severity': severity,
        'message': message,
        'device_id': device_id,
        'sensor_type': sensor_type,
        'value': value,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }