#!/usr/bin/env python3
import sys
import time
import signal
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict

# PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory

# Configuration
from config import settings, gpio_pins

# Sensors
from sensors.dht22_sensor import DHT22Sensor
from sensors.ldr_sensor import LightSensor
from sensors.pir_sensor import PIRSensor

# Actuators
from actuators.led_controller import LEDController
from actuators.buzzer_controller import BuzzerController

# Utilities
from utils.logger import setup_logger


class SmartHomeController:
    """Main controller for Raspberry Pi smart home system"""
    
    def __init__(self):
        """Initialize controller"""
        self.logger = setup_logger("SmartHomeController")
        self.running = False
        
        # Components
        self.pubnub = None
        self.dht22 = None
        self.ldr = None
        self.pir = None
        self.led_green = None
        self.buzzer = None
        
        # Statistics
        self.publish_count = 0
        self.error_count = 0
        
        self.logger.info("=" * 70)
        self.logger.info("🏠 SMART HOME IoT - RASPBERRY PI")
        self.logger.info("=" * 70)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize components
        self._init_pubnub()
        self._init_sensors()
        self._init_actuators()
        
        self.logger.info("=" * 70)
        self.logger.info("✅ Initialization complete!  ")
        self.logger.info("=" * 70)
    
    def _validate_config(self):
        """Validate configuration"""
        self.logger.info("Validating configuration...")
        
        try:
            settings.validate_config()
            self.logger.info("✅ Configuration valid")
        except ValueError as e:
            self.logger.error(f"❌ Configuration error: {e}")
            sys.exit(1)
        
        # Log configuration
        self.logger.info(f"   Device ID: {settings.DEVICE_ID}")
        self.logger.info(f"   Location: {settings.DEVICE_LOCATION}")
        self.logger.info(f"   Read interval: {settings.SENSOR_READ_INTERVAL}s")
        self.logger.info(f"   Simulation mode: {settings.SIMULATION_MODE}")
    
    def _init_pubnub(self):
        """Initialize PubNub connection"""
        self.logger.info("Initializing PubNub...")
        
        try:
            pnconfig = PNConfiguration()
            pnconfig.publish_key = settings.PUBNUB_PUBLISH_KEY
            pnconfig.subscribe_key = settings.PUBNUB_SUBSCRIBE_KEY
            pnconfig.uuid = settings.PUBNUB_UUID
            pnconfig.ssl = True
            
            self.pubnub = PubNub(pnconfig)
            
            # Create and add listener
            listener = PubNubListener(self)
            self.pubnub.add_listener(listener)
            
            # Subscribe to control channel
            self.pubnub.subscribe().channels(settings.PUBNUB_CONTROL_CHANNEL).execute()
            
            self.logger.info(f"✅ PubNub initialized")
            self.logger.info(f"   UUID: {settings.PUBNUB_UUID}")
            self.logger.info(f"   Sensor channel: {settings.PUBNUB_SENSOR_CHANNEL}")
            self.logger.info(f"   Control channel: {settings.PUBNUB_CONTROL_CHANNEL}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize PubNub: {e}")
            sys.exit(1)
    
    def _init_sensors(self):
        """Initialize all sensors"""
        self.logger.info("Initializing sensors...")
        
        # DHT22 (Temperature + Humidity)
        try:
            self.dht22 = DHT22Sensor(gpio_pin=gpio_pins.DHT22_PIN)
            if self.dht22.is_initialised:
                self.logger.info(f"✅ DHT22 sensor ready (GPIO {gpio_pins.DHT22_PIN})")
            else:
                self.logger.warning("⚠️  DHT22 not initialized")
        except Exception as e: 
            self.logger.error(f"❌ DHT22 initialization failed: {e}")
        
        # LDR (Light)
        try:
            self.ldr = LightSensor(
                adc_channel=gpio_pins.MCP3008_LDR_CHANNEL,
                smoothing_samples=5
            )
            if self.ldr.is_initialised:
                self.logger.info(f"✅ Light sensor ready (MCP3008 CH{gpio_pins.MCP3008_LDR_CHANNEL})")
            else:
                self.logger.warning("⚠️  Light sensor not initialized")
        except Exception as e: 
            self.logger.error(f"❌ Light sensor initialization failed: {e}")
        
        # PIR (Motion) - with integrated buzzer and LED
        try:
            self.pir = PIRSensor(
                pir_pin=gpio_pins.PIR_PIN,
                buzzer_pin=gpio_pins.BUZZER_PIN,
                led_pin=gpio_pins.LED_GREEN_PIN,
                calibration_time=2.0,
                enable_buzzer=True,
                enable_led=True,
                on_motion_detected=self._on_motion_detected
            )
            if self.pir.is_initialised:
                self.logger.info(f"✅ PIR sensor ready (GPIO {gpio_pins.PIR_PIN})")
                self.logger.info(f"   Integrated buzzer: GPIO {gpio_pins.BUZZER_PIN}")
                self.logger.info(f"   Integrated LED: GPIO {gpio_pins.LED_GREEN_PIN}")
            else:
                self.logger.warning("⚠️  PIR sensor not initialized")
        except Exception as e:
            self.logger.error(f"❌ PIR sensor initialization failed:  {e}")
    
    def _init_actuators(self):
        """Initialize actuators"""
        self.logger.info("Initializing actuators...")
        
        # Note: LED and Buzzer are already integrated with PIR sensor
        # This section is for standalone control if needed
        
        # Standalone LED (if you want separate control)
        # Uncomment if you want to control LED independently: 
        # try:
        #     self.led_green = LEDController('green')
        #     self.logger.info(f"✅ LED controller ready")
        # except Exception as e: 
        #     self.logger. error(f"��� LED initialization failed: {e}")
        
        # Standalone Buzzer (if you want separate control)
        # Uncomment if you want to control buzzer independently:
        # try:
        #     self. buzzer = BuzzerController(gpio_pin=25)  # Different pin from PIR's buzzer
        #     self. logger.info(f"✅ Buzzer controller ready")
        # except Exception as e: 
        #     self.logger.error(f"❌ Buzzer initialization failed: {e}")
        
        self.logger.info("ℹ️  Actuators managed by PIR sensor")
    
    def _on_motion_detected(self):
        """Callback when PIR detects motion"""
        self.logger.info("🚶 Motion detected - publishing alert...")
        
        # Publish motion alert to PubNub
        try:
            message = {
                'type': 'alert',
                'alert_type': 'MOTION_DETECTED',
                'severity': 'info',
                'message': 'Motion detected in living room',
                'device_id': settings.DEVICE_ID,
                'location': settings.DEVICE_LOCATION,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Publish to sensor channel (alerts are monitored there)
            self.pubnub.publish().channel(settings.PUBNUB_SENSOR_CHANNEL).message(message).pn_async(
                lambda result, status:  self.logger.debug("Motion alert published")
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish motion alert: {e}")
    
    def read_all_sensors(self) -> Dict:
        """
        Read all sensors and return data
        
        Returns:
            Dictionary with all sensor readings
        """
        data = {
            'device_id': settings.DEVICE_ID,
            'location': settings.DEVICE_LOCATION,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # DHT22 - Temperature & Humidity
        if self.dht22:
            reading = self.dht22.read_with_retry(max_attempts=2)
            if reading:
                temp, humidity = reading
                data['temperature'] = temp
                data['humidity'] = humidity
                self.logger.debug(f"DHT22: {temp}°C, {humidity}%")
        
        # LDR - Light
        if self.ldr:
            light = self.ldr.read()
            if light is not None: 
                data['light'] = light
                self.logger.debug(f"Light: {light} lux")
        
        # PIR - Motion (read but don't publish state constantly)
        # Motion events are published via callback
        if self.pir:
            motion = self.pir.read()
            # Only include if motion is active
            if motion == 1.0:
                data['motion'] = True
        
        return data
    
    def publish_sensor_data(self, data: Dict) -> bool:
        """
        Publish sensor data to PubNub
        
        Args:
            data: Sensor data dictionary
        
        Returns:
            True if published successfully
        """
        try:
            # Format as sensor_data message
            message = {
                'type': 'sensor_data',
                **data
            }
            
            # Publish
            envelope = self.pubnub.publish() \
                .channel(settings.PUBNUB_SENSOR_CHANNEL) \
                .message(message) \
                .sync()
            
            if not envelope.status.is_error():
                self.publish_count += 1
                self.logger.debug(f"Published sensor data (#{self.publish_count})")
                return True
            else: 
                self.error_count += 1
                self.logger.error(f"Publish failed: {envelope.status.error_data}")
                return False
                
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error publishing:  {e}")
            return False
    
    def handle_control_command(self, message: Dict):
        """
        Handle incoming control commands from PubNub
        
        Args:
            message: Control command message
        """
        try:
            command_type = message.get('type')
            device = message.get('device')
            action = message.get('action')
            
            self.logger.info(f"📥 Control command:  {device} → {action}")
            
            if command_type != 'control_command':
                self.logger.warning(f"Unknown command type: {command_type}")
                return
            
            # Handle buzzer commands
            if device == 'buzzer' and self.pir:
                if action == 'beep':
                    self.pir._beep_pattern()
                    self.logger.info("✅ Buzzer beep executed")
                elif action == 'on':
                    self.pir._buzzer_on()
                    self.logger.info("✅ Buzzer turned on")
                elif action == 'off':
                    self.pir._buzzer_off()
                    self.logger.info("✅ Buzzer turned off")
                elif action == 'alarm':
                    # Play alarm pattern
                    for _ in range(5):
                        self.pir._beep(0.2, 2000)
                        time.sleep(0.1)
                    self.logger.info("✅ Alarm executed")
                else:
                    self.logger.warning(f"Unknown buzzer action: {action}")
            
            # Handle LED commands
            elif device == 'led' and self.pir:
                if action == 'on': 
                    self.pir._led_on()
                    self.logger.info("✅ LED turned on")
                elif action == 'off':
                    self.pir._led_off()
                    self.logger.info("✅ LED turned off")
                elif action == 'toggle':
                    # Toggle LED state
                    if self.pir.enable_led:
                        # Simple toggle by turning on then scheduling off
                        self.pir._led_on()
                        time.sleep(0.5)
                        self.pir._led_off()
                    self.logger.info("✅ LED toggled")
                else:
                    self.logger.warning(f"Unknown LED action: {action}")
            
            else:
                self.logger.warning(f"Unknown device: {device}")
                
        except Exception as e:
            self.logger.error(f"Error handling control command: {e}")
            traceback.print_exc()
    
    def run(self):
        """Main loop"""
        self.running = True
        self.logger.info("🚀 Starting main loop...")
        self.logger.info(f"   Reading sensors every {settings.SENSOR_READ_INTERVAL} seconds")
        self.logger.info("   Press Ctrl+C to stop")
        self.logger.info("-" * 70)
        
        try:
            while self.running:
                # Read all sensors
                sensor_data = self.read_all_sensors()
                
                # Log summary
                summary_parts = []
                if 'temperature' in sensor_data:
                    summary_parts.append(f"🌡️  {sensor_data['temperature']}°C")
                if 'humidity' in sensor_data:
                    summary_parts.append(f"💧 {sensor_data['humidity']}%")
                if 'light' in sensor_data:
                    summary_parts.append(f"💡 {sensor_data['light']} lux")
                if 'motion' in sensor_data:
                    summary_parts.append(f"🚶 Motion!")
                
                if summary_parts:
                    self.logger.info(" | ".join(summary_parts))
                
                # Publish to PubNub
                if sensor_data: 
                    self.publish_sensor_data(sensor_data)
                
                # Wait for next reading
                time.sleep(settings.SENSOR_READ_INTERVAL)
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Received stop signal")
        except Exception as e:
            self.logger.error(f"❌ Error in main loop: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources"""
        self.logger.info("-" * 70)
        self.logger.info("🧹 Cleaning up...")
        
        self.running = False
        
        # Cleanup sensors
        if self.dht22:
            self.dht22.cleanup()
        if self.ldr:
            self.ldr.cleanup()
        if self.pir:
            self.pir.cleanup()
        
        # Cleanup actuators
        if self.led_green:
            self.led_green.cleanup()
        if self.buzzer:
            self.buzzer.cleanup()
        
        # Stop PubNub
        if self.pubnub:
            self.pubnub.unsubscribe_all()
            self.pubnub.stop()
        
        # Print statistics
        self.logger.info("-" * 70)
        self.logger.info("📊 Session Statistics:")
        self.logger.info(f"   Published:  {self.publish_count} messages")
        self.logger.info(f"   Errors: {self.error_count}")
        
        if self.dht22:
            dht_info = self.dht22.get_sensor_info()
            self.logger.info(f"   DHT22 reads: {dht_info['read_count']} (errors: {dht_info['error_count']})")
        
        if self.ldr:
            ldr_info = self.ldr.get_sensor_info()
            self.logger.info(f"   Light reads: {ldr_info['read_count']} (errors: {ldr_info['error_count']})")
        
        if self.pir:
            pir_stats = self.pir.get_statistics()
            self.logger.info(f"   Motion events: {pir_stats['total_motion_events']}")
        
        self.logger.info("=" * 70)
        self.logger.info("✅ Cleanup complete. Goodbye!  👋")
        self.logger.info("=" * 70)


class PubNubListener(SubscribeCallback):
    """PubNub message listener"""
    
    def __init__(self, controller):
        self.controller = controller
        self.logger = setup_logger("PubNubListener")
    
    def status(self, pubnub, status):
        """Handle connection status"""
        if status.category == PNStatusCategory.PNConnectedCategory:
            self.logger.info("✅ Connected to PubNub")
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            self.logger.info("🔄 Reconnected to PubNub")
        elif status.category == PNStatusCategory.PNDisconnectedCategory:
            self.logger.warning("⚠️  Disconnected from PubNub")
        elif status.is_error():
            self.logger.error(f"❌ PubNub error: {status.error_data}")
    
    def message(self, pubnub, message):
        """Handle incoming messages"""
        try:
            payload = message.message
            channel = message.channel
            
            self.logger.debug(f"📨 Message on {channel}: {payload}")
            
            # Handle control commands
            if channel == settings.PUBNUB_CONTROL_CHANNEL: 
                self.controller.handle_control_command(payload)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")


def main():
    """Entry point"""
    # Create controller
    controller = SmartHomeController()
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print()  # New line after ^C
        controller.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run main loop
    controller.run()


if __name__ == "__main__":
    main()