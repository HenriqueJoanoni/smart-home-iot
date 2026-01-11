import logging
from app.config import Config
from app.services.pubnub_service import PubNubService
from app.services.sensor_service import SensorService
from app.services.alert_service import AlertService


class PubNubHandler: 
    """Handles PubNub messages and saves to database"""
    
    def __init__(self, app=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pubnub_service = None
        self.sensor_service = SensorService()
        self.alert_service = AlertService()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app context"""
        self.app = app
        
        if Config.PUBNUB_SENSOR_CHANNEL == Config.PUBNUB_ALERT_CHANNEL: 
            self.logger.error(
                "❌ CONFIGURATION ERROR:  PUBNUB_SENSOR_CHANNEL and PUBNUB_ALERT_CHANNEL "
                "have the same value! This will cause message routing conflicts!"
            )
            self.logger.error(f"   Both set to: {Config.PUBNUB_SENSOR_CHANNEL}")
            self.logger.error("   Please set different channel names in .env")
            raise ValueError("PubNub channels must be different")
        
        # Log channel configuration
        self.logger.info(f"PubNub Channels:")
        self.logger.info(f"  Sensor:  {Config.PUBNUB_SENSOR_CHANNEL}")
        self.logger.info(f"  Control: {Config.PUBNUB_CONTROL_CHANNEL}")
        self.logger.info(f"  Alert:   {Config.PUBNUB_ALERT_CHANNEL}")
        
        # Create PubNub service
        self.pubnub_service = PubNubService(
            publish_key=Config.PUBNUB_PUBLISH_KEY,
            subscribe_key=Config.PUBNUB_SUBSCRIBE_KEY,
            uuid=Config.PUBNUB_UUID,
            secret_key=getattr(Config, 'PUBNUB_SECRET_KEY', None)
        )
        
        # Register message handlers
        self.pubnub_service.add_message_handler(
            Config.PUBNUB_SENSOR_CHANNEL,
            self.handle_sensor_message
        )
        
        self.pubnub_service.add_message_handler(
            Config.PUBNUB_ALERT_CHANNEL,
            self.handle_alert_message
        )
        
        # Subscribe to channels
        self.pubnub_service.subscribe([
            Config.PUBNUB_SENSOR_CHANNEL,
            Config.PUBNUB_ALERT_CHANNEL
        ])
        
        self.logger.info("✅ PubNub handler initialized and listening")
    
    def handle_sensor_message(self, message):
        try:
            with self.app.app_context():
                self.logger.info(f"📨 [SENSOR HANDLER] Received message on sensor channel")
                self.logger.debug(f"   Message: {message}")

                msg_type = message.get('type')
                if msg_type != 'sensor_data':  
                    self.logger.warning(
                        f"[SENSOR HANDLER] Expected sensor_data, got {msg_type}. Ignoring."
                    )
                    return
                
                readings = self.sensor_service.save_reading(message)
                
                if readings: 
                    # Log summary
                    sensor_summary = ", ".join([
                        f"{r.sensor_type}={r.value}{r.unit}" 
                        for r in readings
                    ])
                    self.logger.info(
                        f"✅ Saved {len(readings)} sensor readings: {sensor_summary}"
                    )
                    
                    for reading in readings:
                        alert = self.alert_service.check_thresholds(
                            sensor_type=reading.sensor_type,
                            value=float(reading.value),
                            device_id=reading.device_id
                        )
                        
                        if alert:
                            self.logger.warning(
                                f"⚠️ Alert triggered: {alert.alert_type} - {alert.message}"
                            )
                    
        except Exception as e:
            self.logger.error(f"❌ Error handling sensor message:  {e}")
            import traceback
            traceback.print_exc()
    
    def handle_alert_message(self, message):
        """Handle incoming alert from PubNub"""
        try:  
            with self.app.app_context():
                # ✅ Log recebimento
                self.logger.info(f"📨 [ALERT HANDLER] Received message on alert channel")
                self.logger.debug(f"   Message: {message}")
                
                msg_type = message.get('type')
                if msg_type != 'alert': 
                    self.logger.warning(
                        f"[ALERT HANDLER] Expected alert, got {msg_type}. Ignoring."
                    )
                    return

                alert = self.alert_service.save_alert(message)
                
                if alert: 
                    self.logger.warning(
                        f"✅ Alert saved from PubNub: [{alert.severity}] {alert.alert_type}"
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Error handling alert message: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Stop PubNub service"""
        if self.pubnub_service:
            self.pubnub_service.stop()