import time
from typing import Optional, Tuple

try:
    import board
    import adafruit_dht
    HARDWARE_AVAILABLE = True
except (ImportError, NotImplementedError):
    HARDWARE_AVAILABLE = False

from base_sensor import BaseSensor


class DHT22Sensor(BaseSensor):
    """
    DHT22 temperature and humidity sensor implementation
    
    Hardware Setup:
        - DHT22 VCC → Raspberry Pi 3.3V (Pin 1 or 17)
        - DHT22 DOUT → GPIO 4 (Pin 7)
        - DHT22 GND → GND
    
    Features:
        - Reads temperature and humidity simultaneously
        - Automatic retry on read failures
        - Simulation mode when hardware unavailable
        - Individual temperature/humidity getters
    """
    
    # Default GPIO pin
    DEFAULT_GPIO_PIN = 4
    
    # DHT22 specifications
    MIN_READ_INTERVAL = 2.0  # Minimum 2 seconds between reads
    
    def __init__(self, gpio_pin: int = DEFAULT_GPIO_PIN):
        """
        Initialise DHT22 sensor
        
        Args:
            gpio_pin: GPIO pin number (BCM mode)
        """
        super().__init__("dht22", "multi")
        
        self.gpio_pin = gpio_pin
        self.dht_device = None
        self._last_temperature = None
        self._last_humidity = None
        self._last_read_time = 0
        
        if not HARDWARE_AVAILABLE:
            self.logger.warning("DHT libraries not available, will simulate readings")
            self.is_initialised = True  # Allow simulation
            return
        
        self._init_hardware()
    
    def _init_hardware(self):
        """Initialise DHT22 hardware"""
        try:
            # Initialise DHT22 on specified GPIO
            pin = getattr(board, f'D{self.gpio_pin}')
            self.dht_device = adafruit_dht.DHT22(pin, use_pulseio=False)
            
            self.is_initialised = True
            self.logger.info(f"DHT22 sensor initialised on GPIO {self.gpio_pin}")
            
            # Test read
            test_reading = self.read()
            if test_reading: 
                self.logger.info(f"Initial reading: {test_reading[0]:.1f}°C, {test_reading[1]:.1f}%")
            
        except Exception as e: 
            self.logger.error(f"Failed to initialise DHT22 sensor: {e}")
            self.is_initialised = False
    
    def read(self) -> Optional[Tuple[float, float]]:
        """
        Read temperature and humidity
        
        Returns:
            Tuple of (temperature_celsius, humidity_percent) or None if error
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self._last_read_time < self.MIN_READ_INTERVAL: 
            # Return last known values if reading too frequently
            if self._last_temperature is not None and self._last_humidity is not None:
                return (self._last_temperature, self._last_humidity)
        
        self._last_read_time = current_time
        
        if not HARDWARE_AVAILABLE or not self.is_initialised:
            return self._simulate_readings()
        
        try: 
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            
            if temperature is not None and humidity is not None: 
                self._last_temperature = round(temperature, 1)
                self._last_humidity = round(humidity, 1)
                self.increment_read_count()
                
                self.logger.debug(f"DHT22: {self._last_temperature}°C, {self._last_humidity}%")
                
                return (self._last_temperature, self._last_humidity)
            else:
                self.increment_error_count()
                return None
                
        except RuntimeError as e:
            # DHT sensors can occasionally fail to read
            self.logger.debug(f"DHT22 read error (will retry): {e}")
            self.increment_error_count()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error reading DHT22: {e}")
            self.increment_error_count()
            return None
    
    def read_with_retry(self, max_attempts: int = 3, delay: float = 2.0) -> Optional[Tuple[float, float]]:
        """
        Read sensor with automatic retries
        
        Args: 
            max_attempts: Maximum number of read attempts
            delay: Delay between attempts in seconds
        
        Returns:
            Tuple of (temperature, humidity) or None if all attempts failed
        """
        for attempt in range(max_attempts):
            reading = self.read()
            if reading is not None:
                return reading
            
            if attempt < max_attempts - 1:
                self.logger.debug(f"Retry {attempt + 1}/{max_attempts} in {delay}s...")
                time.sleep(delay)
        
        self.logger.warning("All DHT22 read attempts failed")
        return None
    
    def get_temperature(self) -> Optional[float]: 
        """
        Get only temperature reading
        
        Returns:
            Temperature in Celsius or None if error
        """
        reading = self.read()
        return reading[0] if reading else None
    
    def get_humidity(self) -> Optional[float]: 
        """
        Get only humidity reading
        
        Returns: 
            Relative humidity percentage or None if error
        """
        reading = self.read()
        return reading[1] if reading else None
    
    def get_heat_index(self) -> Optional[float]:
        """
        Calculate heat index (feels-like temperature)
        Uses simplified formula for Celsius
        
        Returns:
            Heat index in Celsius or None if error
        """
        reading = self.read()
        if not reading:
            return None
        
        temp_c, humidity = reading
        
        # Convert to Fahrenheit for calculation
        temp_f = temp_c * 9/5 + 32
        
        # Simplified heat index formula (valid for temp > 27°C and humidity > 40%)
        if temp_c < 27 or humidity < 40:
            return temp_c  # Heat index not applicable
        
        hi_f = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi_f -= 0.22475541 * temp_f * humidity
        hi_f -= 0.00683783 * temp_f * temp_f
        hi_f -= 0.05481717 * humidity * humidity
        hi_f += 0.00122874 * temp_f * temp_f * humidity
        hi_f += 0.00085282 * temp_f * humidity * humidity
        hi_f -= 0.00000199 * temp_f * temp_f * humidity * humidity
        
        # Convert back to Celsius
        hi_c = (hi_f - 32) * 5/9
        
        return round(hi_c, 1)
    
    def get_dew_point(self) -> Optional[float]:
        """
        Calculate dew point temperature
        Uses Magnus formula approximation
        
        Returns: 
            Dew point in Celsius or None if error
        """
        reading = self.read()
        if not reading:
            return None
        
        temp_c, humidity = reading
        
        # Magnus formula constants
        a = 17.27
        b = 237.7
        
        alpha = ((a * temp_c) / (b + temp_c)) + (humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return round(dew_point, 1)
    
    def _simulate_readings(self) -> Tuple[float, float]:
        """
        Simulate temperature and humidity readings
        
        Returns:
            Tuple of simulated (temperature, humidity)
        """
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        
        # Temperature simulation (18-28°C with daily pattern)
        if 6 <= hour <= 18:
            base_temp = 22.0 + (hour - 12) * 0.5
        else:
            base_temp = 19.0
        temperature = round(base_temp + random.uniform(-1.0, 1.0), 1)
        
        # Humidity simulation (40-70% inverse to temperature)
        base_humidity = 70.0 - (temperature - 18.0) * 2
        humidity = round(base_humidity + random.uniform(-5.0, 5.0), 1)
        humidity = max(30.0, min(80.0, humidity))
        
        return (temperature, humidity)
    
    def cleanup(self):
        """Clean up DHT sensor resources"""
        if self.dht_device: 
            try:
                self.dht_device.exit()
                self.logger.info("DHT22 sensor cleaned up")
            except:
                pass


# ====================================
# STANDALONE TEST
# ====================================

if __name__ == "__main__":
    """Standalone test mode"""
    import sys
    
    print("=" * 70)
    print("DHT22 Temperature & Humidity Sensor - Standalone Test")
    print("=" * 70)
    
    sensor = DHT22Sensor()
    
    if not sensor.is_initialised:
        print("❌ Sensor failed to initialise")
        print("\nTroubleshooting:")
        print("1. Check VCC → 3.3V (Pin 1 or 17)")
        print("2. Check DOUT → GPIO 4 (Pin 7)")
        print("3. Check GND → GND")
        print("4. Install library: pip3 install adafruit-circuitpython-dht")
        sys.exit(1)
    
    print(f"✅ Sensor initialised successfully")
    print(f"   Mode: {'HARDWARE' if HARDWARE_AVAILABLE else 'SIMULATION'}")
    print(f"   GPIO Pin: {sensor.gpio_pin}")
    print()
    
    print("Reading sensor every 2 seconds...  (Press Ctrl+C to stop)")
    print("-" * 70)
    print(f"{'Time':<12} {'Temperature':<15} {'Humidity':<15} {'Heat Index':<15}")
    print("-" * 70)
    
    try:
        while True:
            reading = sensor.read_with_retry()
            
            if reading: 
                temp, humidity = reading
                heat_index = sensor.get_heat_index()
                dew_point = sensor.get_dew_point()
                
                current_time = time.strftime("%H:%M:%S")
                print(f"{current_time:<12} {temp: >6.1f} °C      {humidity:>6.1f} %      {heat_index:>6.1f} °C", end='\r')
            else:
                print("⚠️  Read error", end='\r')
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        
        info = sensor.get_sensor_info()
        print(f"\n📊 Statistics:")
        print(f"   Total reads:     {info['read_count']}")
        print(f"   Errors:         {info['error_count']}")
        print(f"   Success rate:   {sensor.get_success_rate():.1f}%")
        
        if reading:
            print(f"\n📈 Last Reading:")
            print(f"   Temperature:     {temp:.1f} °C")
            print(f"   Humidity:       {humidity:.1f} %")
            print(f"   Heat Index:     {heat_index:.1f} °C")
            print(f"   Dew Point:      {dew_point:.1f} °C")
        
        print("=" * 70)
        
    finally:
        sensor.cleanup()
        print("Sensor cleaned up.  Goodbye!  👋")