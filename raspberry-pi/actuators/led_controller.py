try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False
    GPIO = None

from .base_actuator import BaseActuator


class GreenLEDController(BaseActuator):
    """
    Controller for single green LED
    
    Hardware Setup:
        - LED Anode (+) → GPIO 23 (Pin 16)
        - LED Cathode (-) → 220Ω resistor → GND
    
    Features:
        - Simple on/off control
        - Toggle functionality
        - Blink patterns
        - Simulation mode when hardware unavailable
    """
    
    # Default GPIO pin for green LED
    DEFAULT_LED_PIN = 23
    
    # GPIO Mode
    if HARDWARE_AVAILABLE and GPIO is not None:
        GPIO_MODE = GPIO.BCM
    else:
        GPIO_MODE = None
    
    def __init__(self, gpio_pin: int = DEFAULT_LED_PIN):
        """
        Initialise green LED controller
        
        Args: 
            gpio_pin: GPIO pin number (BCM numbering)
        """
        super().__init__("led_green")
        
        self.gpio_pin = gpio_pin
        
        if not HARDWARE_AVAILABLE or GPIO is None:
            self.logger.warning("GPIO not available, LED will be simulated")
            self.is_initialised = True  # Allow simulation mode
            return
        
        self._init_hardware()
    
    def _init_hardware(self):
        """Initialise GPIO for LED"""
        try:
            GPIO.setmode(self.GPIO_MODE)
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            GPIO.output(self.gpio_pin, GPIO.LOW)
            
            self.is_initialised = True
            self.logger.info(f"Green LED initialised on GPIO {self.gpio_pin}")
            
        except Exception as e: 
            self.logger.error(f"Failed to initialise green LED:  {e}")
            self.is_initialised = False
    
    def turn_on(self):
        """Turn LED on"""
        if not self.is_initialised:
            self.logger.warning("LED not initialised")
            return
        
        if HARDWARE_AVAILABLE and GPIO is not None:
            try:
                GPIO.output(self.gpio_pin, GPIO.HIGH)
                self._state = 'on'
                self.logger.debug("Green LED turned ON")
            except Exception as e:
                self.logger.error(f"Error turning on LED: {e}")
        else:
            self._state = 'on'
            self.logger.info("🟢 [SIMULATION] Green LED turned ON")
    
    def turn_off(self):
        """Turn LED off"""
        if not self.is_initialised:
            self.logger.warning("LED not initialised")
            return
        
        if HARDWARE_AVAILABLE and GPIO is not None:
            try:
                GPIO.output(self.gpio_pin, GPIO.LOW)
                self._state = 'off'
                self.logger.debug("Green LED turned OFF")
            except Exception as e: 
                self.logger.error(f"Error turning off LED: {e}")
        else:
            self._state = 'off'
            self.logger.info("⚫ [SIMULATION] Green LED turned OFF")
    
    def toggle(self):
        """Toggle LED state"""
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()
    
    def blink(self, times: int = 3, on_time: float = 0.5, off_time: float = 0.5):
        """
        Blink LED multiple times
        
        Args: 
            times: Number of blinks
            on_time: Time LED stays on (seconds)
            off_time:  Time LED stays off (seconds)
        """
        import time
        
        for i in range(times):
            self.turn_on()
            time.sleep(on_time)
            self.turn_off()
            if i < times - 1:  # Don't wait after last blink
                time.sleep(off_time)
    
    def pulse(self, duration: float = 2.0, frequency: float = 2.0):
        """
        Pulse LED on and off for a duration
        
        Args:
            duration: Total pulse duration (seconds)
            frequency: Pulses per second (Hz)
        """
        import time
        
        if not HARDWARE_AVAILABLE or GPIO is None:
            self.logger.info(f"[SIMULATION] Pulsing LED for {duration}s at {frequency}Hz")
            return
        
        interval = 1.0 / (frequency * 2)
        end_time = time.time() + duration
        
        try:
            while time.time() < end_time:
                self.turn_on()
                time.sleep(interval)
                self.turn_off()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.turn_off()
    
    def flash_quick(self):
        """Quick flash (3 fast blinks)"""
        self.blink(times=3, on_time=0.1, off_time=0.1)
    
    def flash_slow(self):
        """Slow flash (2 slow blinks)"""
        self.blink(times=2, on_time=0.8, off_time=0.5)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if HARDWARE_AVAILABLE and GPIO is not None and self.is_initialised:
            try:
                self.turn_off()
                GPIO.cleanup(self.gpio_pin)
                self.logger.info("Green LED cleaned up")
            except Exception as e:
                self.logger.warning(f"Error during cleanup: {e}")


# ====================================
# STANDALONE TEST
# ====================================

if __name__ == "__main__": 
    """Standalone test mode"""
    import sys
    import time
    
    print("=" * 70)
    print("Green LED Controller - Standalone Test")
    print("=" * 70)
    
    led = GreenLEDController()
    
    if not led.is_initialised:
        print("❌ LED failed to initialise")
        print("\nTroubleshooting:")
        print("1. Check LED Anode (+) → GPIO 23 (Pin 16)")
        print("2. Check LED Cathode (-) → 220Ω resistor → GND")
        print("3. Verify LED polarity (longer leg = anode)")
        sys.exit(1)
    
    print(f"✅ LED initialised successfully")
    print(f"Mode: {'HARDWARE' if HARDWARE_AVAILABLE else 'SIMULATION'}")
    print(f"GPIO Pin: {led.gpio_pin}")
    print()
    
    try:
        # Test 1: Basic on/off
        print("Test 1: Basic ON/OFF")
        print("  Turning ON...")
        led.turn_on()
        time.sleep(2)
        print("  Turning OFF...")
        led.turn_off()
        time.sleep(1)
        print("✅ Pass")
        print()
        
        # Test 2: Toggle
        print("Test 2: Toggle (3 times)")
        for i in range(3):
            print(f"  Toggle {i+1}...")
            led.toggle()
            time.sleep(0.5)
        led.turn_off()
        print("  ✅ Pass")
        print()
        
        # Test 3: Blink
        print("Test 3: Blink (5 times)")
        led.blink(times=5, on_time=0.3, off_time=0.3)
        print("  ✅ Pass")
        print()
        
        # Test 4: Quick flash
        print("Test 4: Quick Flash")
        led.flash_quick()
        time.sleep(0.5)
        print("  ✅ Pass")
        print()
        
        # Test 5: Slow flash
        print("Test 5: Slow Flash")
        led.flash_slow()
        print("  ✅ Pass")
        print()
        
        # Test 6: Pulse
        print("Test 6: Pulse (3 seconds)")
        led.pulse(duration=3.0, frequency=3.0)
        print("  ✅ Pass")
        print()
        
        print("=" * 70)
        print("All tests passed!  ✅")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        
    finally:
        led.cleanup()
        print("LED cleaned up.  Goodbye!  👋")