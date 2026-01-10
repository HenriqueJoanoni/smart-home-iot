import time
from typing import Optional

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False

from .base_actuator import BaseActuator
from config.gpio_pins import BUZZER_PIN, GPIO_MODE


class BuzzerController(BaseActuator):
    """
    Controller for standalone buzzer
    
    Note: PIR sensor has integrated buzzer control. 
    This is for manual buzzer control independent of PIR.
    """
    
    # PWM Configuration
    DEFAULT_FREQUENCY = 2000# Hz
    
    def __init__(self, gpio_pin: int = BUZZER_PIN, frequency: int = DEFAULT_FREQUENCY):
        """
        Initialize buzzer controller
        
        Args:
            gpio_pin: GPIO pin number for buzzer
            frequency: PWM frequency in Hz
        """
        super().__init__("buzzer")
        self.gpio_pin = gpio_pin
        self.frequency = frequency
        self.pwm = None
        
        if not HARDWARE_AVAILABLE:
            self.logger.warning("GPIO not available, buzzer will be simulated")
            self.is_initialised = True
            return
        
        try:
            GPIO.setmode(getattr(GPIO, GPIO_MODE))
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            
            # Initialize PWM
            self.pwm = GPIO.PWM(self.gpio_pin, self.frequency)
            self.pwm.start(0)  # Start with 0% duty cycle (OFF)
            
            self.is_initialised = True
            self.logger.info(f"Buzzer initialized on GPIO {self.gpio_pin} (PWM @ {self.frequency}Hz)")
            
        except Exception as e: 
            self.logger.error(f"Failed to initialize buzzer: {e}")
            self.is_initialised = False
    
    def turn_on(self, frequency: Optional[int] = None):
        """
        Turn buzzer on
        
        Args: 
            frequency: Optional frequency override (Hz)
        """
        if not self.is_initialised:
            return
        
        if HARDWARE_AVAILABLE and self.pwm:
            try:
                if frequency:
                    self.pwm.ChangeFrequency(frequency)
                self.pwm.ChangeDutyCycle(50)  # 50% duty cycle
                self._state = 'on'
                self.increment_on_count()
                self.logger.debug("Buzzer turned ON")
            except Exception as e: 
                self.logger.error(f"Error turning on buzzer: {e}")
        else:
            self._state = 'on'
            self.increment_on_count()
            self.logger.info("[SIMULATION] Buzzer turned ON")
    
    def turn_off(self):
        """Turn buzzer off"""
        if not self.is_initialised:
            return
        
        if HARDWARE_AVAILABLE and self.pwm:
            try:
                self.pwm.ChangeDutyCycle(0)
                self._state = 'off'
                self.increment_off_count()
                self.logger.debug("Buzzer turned OFF")
            except Exception as e: 
                self.logger.error(f"Error turning off buzzer:  {e}")
        else:
            self._state = 'off'
            self.increment_off_count()
            self.logger.info("[SIMULATION] Buzzer turned OFF")
    
    def beep(self, duration: float = 0.2, frequency: Optional[int] = None):
        """
        Make a single beep
        
        Args: 
            duration:  Beep duration in seconds
            frequency: Optional frequency override
        """
        self.turn_on(frequency)
        time.sleep(duration)
        self.turn_off()
    
    def beep_pattern(self, count: int = 3, duration: float = 0.2, interval: float = 0.1):
        """
        Play a beep pattern
        
        Args:
            count: Number of beeps
            duration: Duration of each beep
            interval:  Interval between beeps
        """
        for i in range(count):
            self.beep(duration)
            if i < count - 1:
                time.sleep(interval)
    
    def alarm(self, duration: float = 2.0):
        """
        Play alarm sound (alternating tones)
        
        Args: 
            duration: Total alarm duration in seconds
        """
        if not self.is_initialised:
            return
        
        end_time = time.time() + duration
        
        while time.time() < end_time:
            self.turn_on(2000)
            time.sleep(0.2)
            self.turn_on(2500)
            time.sleep(0.2)
        
        self.turn_off()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if HARDWARE_AVAILABLE and self.is_initialised:
            try: 
                self.turn_off()
                if self.pwm:
                    self.pwm.stop()
                GPIO.cleanup(self.gpio_pin)
                self.logger.info("Buzzer cleaned up")
            except: 
                pass


# ====================================
# STANDALONE TEST
# ====================================

if __name__ == "__main__": 
    """Standalone test mode"""
    import sys
    
    print("=" * 70)
    print("Buzzer Controller - Standalone Test")
    print("=" * 70)
    
    buzzer = BuzzerController()
    
    if not buzzer.is_initialised:
        print("❌ Buzzer failed to initialize")
        sys.exit(1)
    
    print(f"✅ Buzzer initialized")
    print(f"   Mode: {'HARDWARE' if HARDWARE_AVAILABLE else 'SIMULATION'}")
    print(f"   GPIO: {buzzer.gpio_pin}")
    print()
    
    try:
        print("Testing buzzer patterns...")
        
        print("1. Single beep")
        buzzer.beep()
        time.sleep(1)
        
        print("2. Triple beep")
        buzzer.beep_pattern(count=3)
        time.sleep(1)
        
        print("3. Alarm (2 seconds)")
        buzzer.alarm(duration=2.0)
        time.sleep(1)
        
        print("\n✅ Test complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    finally:
        buzzer.cleanup()
        print("Buzzer cleaned up.  Goodbye!  👋")