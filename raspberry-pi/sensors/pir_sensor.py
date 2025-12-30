import time
from typing import Optional, Dict, Callable
from datetime import datetime, timedelta

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False
    GPIO = None
    print("Warning: RPi.GPIO not available. Install with: pip3 install RPi.GPIO")

from base_sensor import BaseSensor


class PIRSensor(BaseSensor):
    """
    PIR motion sensor implementation with integrated alerts
    
    Hardware Setup:
        - PIR VCC → Raspberry Pi 5V (Pin 2 or 4)
        - PIR OUT → GPIO 27 (Pin 13)
        - PIR GND → GND
        - Buzzer (+) → GPIO 25 (Pin 22) [Passive buzzer with PWM]
        - Buzzer (-) → GND
        - LED Green (+) → GPIO 23 (Pin 16) → 220Ω → GND
    
    Features:
        - Motion detection with debouncing
        - PWM buzzer support for passive buzzers
        - Visual LED indicator
        - Motion event callbacks
        - Motion history tracking
        - Configurable alerts
        - Statistics and analytics
        - Simulation mode for testing
    """
    
    # GPIO Configuration
    DEFAULT_PIR_PIN = 27
    DEFAULT_BUZZER_PIN = 25
    DEFAULT_LED_PIN = 23
    if HARDWARE_AVAILABLE and GPIO is not None:
        GPIO_MODE = GPIO.BCM
    else:
        GPIO_MODE = None
    
    # Timing Configuration
    DEFAULT_CALIBRATION_TIME = 2.0      # Seconds for PIR to stabilise
    DEFAULT_DEBOUNCE_TIME = 0.1         # Seconds to ignore rapid changes
    DEFAULT_MOTION_TIMEOUT = 5.0        # Seconds to consider motion "ended"
    
    # Buzzer PWM Configuration
    DEFAULT_BUZZER_FREQUENCY = 2000     # Hz (adjust for different pitch)
    DEFAULT_BEEP_DURATION = 0.2         # Seconds per beep
    DEFAULT_BEEP_COUNT = 3              # Number of beeps on motion
    
    def __init__(
        self,
        pir_pin: int = DEFAULT_PIR_PIN,
        buzzer_pin: int = DEFAULT_BUZZER_PIN,
        led_pin: int = DEFAULT_LED_PIN,
        calibration_time: float = DEFAULT_CALIBRATION_TIME,
        debounce_time: float = DEFAULT_DEBOUNCE_TIME,
        motion_timeout: float = DEFAULT_MOTION_TIMEOUT,
        buzzer_frequency: int = DEFAULT_BUZZER_FREQUENCY,
        beep_duration: float = DEFAULT_BEEP_DURATION,
        beep_count:  int = DEFAULT_BEEP_COUNT,
        enable_buzzer: bool = True,
        enable_led: bool = True,
        on_motion_detected: Optional[Callable] = None,
        on_motion_ended: Optional[Callable] = None
    ):
        """
        Initialise PIR motion sensor with alerts
        
        Args:
            pir_pin: GPIO pin for PIR sensor (BCM numbering)
            buzzer_pin: GPIO pin for buzzer (BCM numbering)
            led_pin: GPIO pin for LED indicator (BCM numbering)
            calibration_time: Time in seconds for sensor calibration
            debounce_time:  Minimum time between state changes
            motion_timeout: Time after last motion to consider motion "ended"
            buzzer_frequency: PWM frequency for buzzer (Hz)
            beep_duration:  Duration of each beep (seconds)
            beep_count: Number of beeps on motion detection
            enable_buzzer: Enable buzzer alerts
            enable_led: Enable LED alerts
            on_motion_detected: Callback function when motion starts
            on_motion_ended:  Callback function when motion ends
        """
        super().__init__("motion", "boolean")
        
        # GPIO Pins
        self.pir_pin = pir_pin
        self.buzzer_pin = buzzer_pin
        self.led_pin = led_pin
        
        # Timing
        self.calibration_time = calibration_time
        self.debounce_time = debounce_time
        self. motion_timeout = motion_timeout
        
        # Buzzer settings
        self.buzzer_frequency = buzzer_frequency
        self.beep_duration = beep_duration
        self.beep_count = beep_count
        self.enable_buzzer = enable_buzzer
        self.enable_led = enable_led
        
        # PWM object
        self.buzzer_pwm = None
        
        # Callbacks
        self.on_motion_detected = on_motion_detected
        self.on_motion_ended = on_motion_ended
        
        # State tracking
        self._last_motion_time = None
        self._last_read_time = 0
        self._last_state = False
        self._motion_active = False
        self._calibration_complete = False
        
        # Statistics
        self._total_motion_events = 0
        self._total_readings = 0
        self._motion_durations = []
        
        # History (last 100 events)
        self._motion_history = []
        self._max_history = 100
        
        if not HARDWARE_AVAILABLE:
            self.logger.warning("RPi.GPIO not available - running in SIMULATION mode")
            self.is_initialised = True
            self._calibration_complete = True
            return
        
        # Initialise hardware
        self._init_hardware()
    
    def _init_hardware(self):
        """Initialise GPIO for PIR sensor, buzzer, and LED"""
        try:
            # Set up GPIO mode
            GPIO.setmode(self.GPIO_MODE)
            GPIO.setwarnings(False)
            
            # Set up PIR pin as input
            GPIO.setup(self.pir_pin, GPIO. IN)
            
            # Set up Buzzer with PWM
            if self.enable_buzzer:
                GPIO.setup(self.buzzer_pin, GPIO.OUT)
                self.buzzer_pwm = GPIO.PWM(self.buzzer_pin, self.buzzer_frequency)
                self.buzzer_pwm.start(0)  # Start with 0% duty cycle (OFF)
                self.logger.info(f"Buzzer initialised on GPIO {self.buzzer_pin} (PWM @ {self.buzzer_frequency} Hz)")
            
            # Set up LED
            if self.enable_led:
                GPIO.setup(self. led_pin, GPIO.OUT)
                GPIO.output(self.led_pin, GPIO.LOW)
                self.logger.info(f"LED initialised on GPIO {self.led_pin}")
            
            self.logger.info(f"PIR sensor initialising on GPIO {self.pir_pin}...")
            self.logger.info(f"Calibration time: {self.calibration_time}s")
            
            # Wait for PIR to calibrate
            if self.calibration_time > 0:
                self.logger. info("⏳ PIR calibrating - please wait and avoid movement...")
                time.sleep(self.calibration_time)
            
            self._calibration_complete = True
            self.is_initialised = True
            
            # Read initial state
            initial_state = GPIO.input(self.pir_pin)
            self. logger.info(f"✅ PIR sensor ready!  Initial state: {'HIGH' if initial_state else 'LOW'}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialise PIR sensor: {e}")
            self.is_initialised = False
            self._calibration_complete = False
    
    def _read_gpio(self) -> bool:
        """Read current GPIO state"""
        if not GPIO: 
            return False
        
        try:
            return bool(GPIO.input(self.pir_pin))
        except Exception as e:
            self.logger.error(f"Error reading GPIO: {e}")
            return False
    
    def _led_on(self):
        """Turn LED on"""
        if self.enable_led and HARDWARE_AVAILABLE:
            try:
                GPIO.output(self.led_pin, GPIO.HIGH)
            except: 
                pass
    
    def _led_off(self):
        """Turn LED off"""
        if self.enable_led and HARDWARE_AVAILABLE: 
            try:
                GPIO. output(self.led_pin, GPIO.LOW)
            except:
                pass
    
    def _buzzer_on(self, frequency: Optional[int] = None):
        """Turn buzzer on with PWM"""
        if not self.enable_buzzer or not self. buzzer_pwm:
            return
        
        try:
            if frequency:
                self.buzzer_pwm. ChangeFrequency(frequency)
            self.buzzer_pwm.ChangeDutyCycle(50)  # 50% duty cycle
        except: 
            pass
    
    def _buzzer_off(self):
        """Turn buzzer off"""
        if not self.enable_buzzer or not self.buzzer_pwm:
            return
        
        try:
            self.buzzer_pwm.ChangeDutyCycle(0)
        except:
            pass
    
    def _beep(self, duration: float = None, frequency: int = None):
        """Make a single beep with LED"""
        duration = duration or self.beep_duration
        
        self._led_on()
        self._buzzer_on(frequency)
        time.sleep(duration)
        self._buzzer_off()
        self._led_off()
    
    def _beep_pattern(self):
        """Play beep pattern on motion detection"""
        for i in range(self.beep_count):
            self._beep(self.beep_duration, self. buzzer_frequency)
            if i < self.beep_count - 1:
                time.sleep(0.1)
    
    def read(self) -> Optional[float]:
        """
        Read motion detection status
        
        Returns:
            1.0 if motion detected, 0.0 if no motion, None if error
        """
        self._total_readings += 1
        
        if not self. is_initialised or not self._calibration_complete:
            self.logger.warning("Sensor not calibrated yet")
            return None
        
        # Debouncing:  Don't read too frequently
        current_time = time.time()
        if current_time - self._last_read_time < self.debounce_time:
            return 1.0 if self._motion_active else 0.0
        
        self._last_read_time = current_time
        
        if not HARDWARE_AVAILABLE:
            motion = self._simulate_motion()
        else:
            motion = self._read_gpio()
        
        # Handle state change
        if motion and not self._last_state:
            # Motion started
            self._on_motion_start()
        elif not motion and self._last_state:
            # Motion might have ended (check timeout)
            if self._last_motion_time: 
                time_since_motion = current_time - self._last_motion_time
                if time_since_motion > self.motion_timeout:
                    self._on_motion_end()
        
        # Update motion timestamp if currently detecting
        if motion: 
            self._last_motion_time = current_time
            self._motion_active = True
        
        self._last_state = motion
        
        return 1.0 if motion else 0.0
    
    def _on_motion_start(self):
        """Handle motion start event"""
        self._total_motion_events += 1
        self._motion_active = True
        
        event = {
            'timestamp': datetime.now(),
            'type': 'start',
            'event_number': self._total_motion_events
        }
        self._add_to_history(event)
        
        self.logger.info(f"🚶 Motion detected! (Event #{self._total_motion_events})")
        
        # Play alert
        self._beep_pattern()
        
        # Trigger callback
        if self.on_motion_detected:
            try:
                self.on_motion_detected()
            except Exception as e: 
                self.logger.error(f"Error in motion_detected callback: {e}")
    
    def _on_motion_end(self):
        """Handle motion end event"""
        self._motion_active = False
        
        # Calculate duration
        if self._motion_history and self._motion_history[-1]['type'] == 'start':
            start_time = self._motion_history[-1]['timestamp']
            duration = (datetime.now() - start_time).total_seconds()
            self._motion_durations.append(duration)
        else:
            duration = None
        
        event = {
            'timestamp': datetime.now(),
            'type': 'end',
            'duration': duration
        }
        self._add_to_history(event)
        
        if duration:
            self.logger.info(f"🛑 Motion ended (Duration: {duration:.1f}s)")
        else:
            self.logger.info("🛑 Motion ended")
        
        # Trigger callback
        if self.on_motion_ended:
            try: 
                self.on_motion_ended()
            except Exception as e: 
                self.logger.error(f"Error in motion_ended callback: {e}")
    
    def _add_to_history(self, event: Dict):
        """Add event to history (FIFO queue)"""
        self._motion_history.append(event)
        
        if len(self._motion_history) > self._max_history:
            self._motion_history.pop(0)
    
    def is_motion_detected(self) -> bool:
        """Check if motion is currently detected"""
        reading = self.read()
        return reading is not None and reading > 0.5
    
    def is_motion_active(self) -> bool:
        """Check if motion is considered active (within timeout period)"""
        if not self._last_motion_time:
            return False
        
        time_since_motion = time.time() - self._last_motion_time
        return time_since_motion <= self.motion_timeout
    
    def time_since_last_motion(self) -> Optional[float]:
        """Get time in seconds since last motion detection"""
        if self._last_motion_time is None:
            return None
        return time.time() - self._last_motion_time
    
    def get_motion_count(self, time_window: Optional[float] = None) -> int:
        """Get number of motion events in time window"""
        if time_window is None:
            return self._total_motion_events
        
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        count = sum(
            1 for event in self._motion_history
            if event['type'] == 'start' and event['timestamp'] >= cutoff_time
        )
        return count
    
    def get_average_motion_duration(self) -> Optional[float]:
        """Get average duration of motion events"""
        if not self._motion_durations:
            return None
        return sum(self._motion_durations) / len(self._motion_durations)
    
    def get_motion_history(self, limit: Optional[int] = None) -> list:
        """Get motion event history (most recent first)"""
        history = self._motion_history[: :-1]
        
        if limit: 
            history = history[: limit]
        
        return history
    
    def get_statistics(self) -> Dict:
        """Get comprehensive sensor statistics"""
        avg_duration = self.get_average_motion_duration()
        time_since = self.time_since_last_motion()
        
        last_minute = self. get_motion_count(60)
        last_hour = self.get_motion_count(3600)
        
        return {
            'total_readings': self._total_readings,
            'total_motion_events':  self._total_motion_events,
            'motion_active': self._motion_active,
            'last_motion_time': self._last_motion_time,
            'time_since_last_motion': time_since,
            'average_motion_duration': avg_duration,
            'motion_events_last_minute': last_minute,
            'motion_events_last_hour': last_hour,
            'history_size': len(self._motion_history),
            'calibration_complete': self._calibration_complete,
            'hardware_mode':  HARDWARE_AVAILABLE and self.is_initialised,
            'buzzer_enabled': self.enable_buzzer,
            'led_enabled': self.enable_led
        }
    
    def reset_statistics(self):
        """Reset all statistics and history"""
        self._total_motion_events = 0
        self._total_readings = 0
        self._motion_durations. clear()
        self._motion_history.clear()
        self.logger.info("Statistics reset")
    
    def test_alerts(self):
        """Test buzzer and LED"""
        self. logger.info("Testing alerts...")
        
        # Test melody
        notes = [
            (2000, 0.15),
            (2500, 0.15),
            (3000, 0.15),
        ]
        
        for freq, duration in notes:
            self._beep(duration, freq)
            time.sleep(0.05)
        
        self.logger.info("Alert test complete")
    
    def _simulate_motion(self) -> bool:
        """Simulate motion detection for testing"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        
        if 7 <= hour <= 23:
            probability = 0.12
        else:
            probability = 0.02
        
        if self._last_motion_time: 
            time_since = time.time() - self._last_motion_time
            if time_since > 60: 
                probability *= 1.5
        
        return random.random() < probability
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if HARDWARE_AVAILABLE and self.is_initialised:
            try:
                # Turn off buzzer and LED
                self._buzzer_off()
                self._led_off()
                time.sleep(0.1)
                
                # Stop PWM
                if self.buzzer_pwm:
                    self.buzzer_pwm. stop()
                
                # Cleanup GPIO
                GPIO.cleanup([self.pir_pin, self.buzzer_pin, self. led_pin])
                self.logger.info("PIR sensor cleaned up")
            except Exception as e:
                self.logger.warning(f"Error during cleanup: {e}")


# ====================================
# STANDALONE TEST
# ====================================

if __name__ == "__main__":
    """Standalone test mode"""
    import sys
    
    print("=" * 70)
    print("PIR Motion Sensor - Standalone Test")
    print("With Passive Buzzer (PWM) and Green LED")
    print("=" * 70)
    
    # Callback functions
    def on_motion():
        print("\n🚨 [CALLBACK] MOTION DETECTED!")
    
    def on_motion_end():
        print("\n✅ [CALLBACK] Motion ended")
    
    # Create sensor with all features enabled
    sensor = PIRSensor(
        calibration_time=2.0,
        debounce_time=0.1,
        motion_timeout=3.0,
        buzzer_frequency=2000,
        beep_duration=0.2,
        beep_count=3,
        enable_buzzer=True,
        enable_led=True,
        on_motion_detected=on_motion,
        on_motion_ended=on_motion_end
    )
    
    if not sensor.is_initialised:
        print("❌ Sensor failed to initialise")
        print("\nTroubleshooting:")
        print("1. Check PIR:  VCC→5V, OUT→GPIO27, GND→GND")
        print("2. Check Buzzer: +→GPIO25, -→GND")
        print("3. Check LED:  Anode→GPIO23, Cathode→220Ω→GND")
        sys.exit(1)
    
    print(f"✅ Sensor initialised successfully")
    print(f"Mode: {'HARDWARE' if HARDWARE_AVAILABLE and sensor.is_initialised else 'SIMULATION'}")
    print(f"PIR GPIO: {sensor.pir_pin}")
    print(f"Buzzer GPIO: {sensor. buzzer_pin} (PWM @ {sensor.buzzer_frequency} Hz)")
    print(f"LED GPIO:  {sensor.led_pin}")
    print()
    
    # Test alerts
    print("🔊 Testing buzzer and LED...")
    sensor.test_alerts()
    print()
    
    print("Monitoring for motion...  (Press Ctrl+C to stop)")
    print("-" * 70)
    print(f"{'Time':<12} {'Status':<15} {'Events':<10} {'Last Motion':<20}")
    print("-" * 70)
    
    try:
        while True:
            motion = sensor.read()
            
            if motion is not None:
                current_time = time.strftime("%H:%M:%S")
                status = "🔴 MOTION" if motion > 0.5 else "🟢 Clear"
                events = sensor._total_motion_events
                
                time_since = sensor.time_since_last_motion()
                if time_since is None:
                    last_motion_str = "Never"
                elif time_since < 60:
                    last_motion_str = f"{time_since:.1f}s ago"
                else:
                    last_motion_str = f"{time_since/60:.1f}m ago"
                
                print(f"{current_time:<12} {status:<15} {events: <10} {last_motion_str:<20}", end='\r')
            
            time.sleep(0.2)
            
    except KeyboardInterrupt: 
        print("\n" + "-" * 70)
        
        stats = sensor.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"Total readings:         {stats['total_readings']}")
        print(f"Motion events:        {stats['total_motion_events']}")
        print(f"Events (last minute): {stats['motion_events_last_minute']}")
        print(f"Events (last hour):   {stats['motion_events_last_hour']}")
        
        if stats['average_motion_duration']:
            print(f"   Avg motion duration:  {stats['average_motion_duration']:.1f}s")
        
        print("\n📜 Recent Motion Events:")
        history = sensor.get_motion_history(limit=5)
        if history:
            for event in history:
                time_str = event['timestamp'].strftime("%H:%M:%S")
                if event['type'] == 'start':
                    print(f"{time_str} - Motion started (Event #{event['event_number']})")
                else:
                    duration_str = f" ({event['duration']:.1f}s)" if event['duration'] else ""
                    print(f"{time_str} - Motion ended{duration_str}")
        else:
            print("No events recorded")
        
        print("=" * 70)
        
    finally:
        sensor.cleanup()
        print("Sensor cleaned up. Goodbye!  👋")