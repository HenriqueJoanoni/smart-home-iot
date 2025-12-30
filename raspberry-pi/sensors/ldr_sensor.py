import time
from typing import Optional, Dict, List, Tuple

try:
    import spidev
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

from base_sensor import BaseSensor


class LightSensor(BaseSensor):
    """
    Photo transistor light sensor via MCP3008 ADC
    
    Hardware Setup:
        - Photo transistor collector → 3.3V
        - Photo transistor emitter → 10kΩ resistor → GND
        - Junction (collector/emitter) → MCP3008 CH0
        - MCP3008 VDD/VREF → 3.3V
        - MCP3008 AGND/DGND → GND
        - MCP3008 CLK → GPIO 11 (Pin 23)
        - MCP3008 DOUT → GPIO 9 (Pin 21)
        - MCP3008 DIN → GPIO 10 (Pin 19)
        - MCP3008 CS → GPIO 8 (Pin 24)
    
    Features:
        - 10-bit ADC resolution (0-1023)
        - Configurable calibration
        - Moving average filter for stability
        - Detailed readings with voltage/ADC values
        - Simulation mode when hardware unavailable
    """
    
    # SPI Configuration
    SPI_BUS = 0
    SPI_DEVICE = 0
    SPI_MAX_SPEED = 1350000
    
    # ADC Configuration
    ADC_CHANNEL = 0
    ADC_MAX_VALUE = 1023
    VREF = 3.3
    
    # Calibration points (voltage, lux)
    CALIBRATION_POINTS = [
        (0.0, 0),
        (0.3, 5),
        (0.6, 20),
        (1.0, 80),
        (1.5, 200),
        (2.0, 450),
        (2.5, 700),
        (3.0, 900),
        (3.3, 1000)
    ]
    
    def __init__(
        self,
        spi_bus: int = SPI_BUS,
        spi_device: int = SPI_DEVICE,
        adc_channel: int = ADC_CHANNEL,
        smoothing_samples: int = 5,
        use_calibration: bool = True
    ):
        """
        Initialise light sensor
        
        Args: 
            spi_bus: SPI bus number (usually 0)
            spi_device: SPI device number (0 for CE0)
            adc_channel: MCP3008 channel (0-7)
            smoothing_samples: Number of samples for moving average
            use_calibration: Use calibration curve instead of linear mapping
        """
        super().__init__("light", "lux")
        
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.adc_channel = adc_channel
        self.smoothing_samples = max(1, smoothing_samples)
        self.use_calibration = use_calibration
        
        self.spi = None
        self._reading_buffer:  List[int] = []
        
        if not HARDWARE_AVAILABLE: 
            self.logger.warning("spidev library not available - running in SIMULATION mode")
            self.is_initialised = True
            return
        
        self._init_hardware()
    
    def _init_hardware(self):
        """Initialise SPI connection to MCP3008"""
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.spi_bus, self.spi_device)
            self.spi.max_speed_hz = self.SPI_MAX_SPEED
            self.spi.mode = 0
            
            self.is_initialised = True
            self.logger.info(
                f"Light sensor initialised:  SPI {self.spi_bus}. {self.spi_device}, "
                f"CH{self.adc_channel}, smoothing={self.smoothing_samples}"
            )
            
            # Test read
            test_value = self._read_adc_raw()
            if test_value is not None:
                test_lux = self._adc_to_lux(test_value)
                self.logger.info(f"Initial reading: ADC={test_value}, {test_lux:.1f} lux")
                
        except FileNotFoundError:
            self. logger.error("SPI device not found. Enable SPI:  sudo raspi-config → Interface → SPI")
            self.is_initialised = False
        except Exception as e:
            self.logger.error(f"Failed to initialise light sensor: {e}")
            self.is_initialised = False
    
    def _read_adc_raw(self) -> Optional[int]:
        """Read raw ADC value from MCP3008"""
        if not self.spi:
            return None
        
        try:
            command = [
                0x01,
                (0x08 + self.adc_channel) << 4,
                0x00
            ]
            
            response = self.spi.xfer2(command)
            adc_value = ((response[1] & 0x03) << 8) | response[2]
            
            return adc_value
            
        except Exception as e:
            self.logger.error(f"Error reading ADC: {e}")
            return None
    
    def _read_adc_smoothed(self) -> Optional[int]:
        """Read ADC with moving average smoothing"""
        raw_value = self._read_adc_raw()
        
        if raw_value is None: 
            return None
        
        self._reading_buffer.append(raw_value)
        
        if len(self._reading_buffer) > self.smoothing_samples:
            self._reading_buffer. pop(0)
        
        return sum(self._reading_buffer) // len(self._reading_buffer)
    
    def _adc_to_voltage(self, adc_value:  int) -> float:
        """Convert ADC value to voltage"""
        return (adc_value / self.ADC_MAX_VALUE) * self.VREF
    
    def _voltage_to_lux_calibrated(self, voltage: float) -> float:
        """Convert voltage to lux using calibration curve"""
        for i in range(len(self.CALIBRATION_POINTS) - 1):
            v1, lux1 = self.CALIBRATION_POINTS[i]
            v2, lux2 = self.CALIBRATION_POINTS[i + 1]
            
            if v1 <= voltage <= v2:
                ratio = (voltage - v1) / (v2 - v1)
                lux = lux1 + ratio * (lux2 - lux1)
                return lux
        
        if voltage < self.CALIBRATION_POINTS[0][0]:
            return 0.0
        else:
            return self.CALIBRATION_POINTS[-1][1]
    
    def _adc_to_lux(self, adc_value: int) -> float:
        """Convert ADC value to lux"""
        voltage = self._adc_to_voltage(adc_value)
        
        if self.use_calibration:
            return self._voltage_to_lux_calibrated(voltage)
        else:
            return (voltage / self.VREF) * 1000.0
    
    def read(self) -> Optional[float]:
        """
        Read light intensity
        
        Returns: 
            Light level in lux (0-1000 scale) or None if error
        """
        if not HARDWARE_AVAILABLE or not self.is_initialised:
            reading = self._simulate_light()
            self. increment_read_count()
            return reading
        
        try:
            adc_value = self._read_adc_smoothed()
            
            if adc_value is None:
                self.increment_error_count()
                return None
            
            lux = self._adc_to_lux(adc_value)
            self.increment_read_count()
            
            self.logger.debug(f"Light:  ADC={adc_value}, {lux:.1f} lux")
            
            return round(lux, 1)
            
        except Exception as e: 
            self.logger.error(f"Error reading light sensor: {e}")
            self.increment_error_count()
            return None
    
    def read_detailed(self) -> Optional[Dict[str, float]]:
        """
        Read sensor with detailed information
        
        Returns: 
            Dictionary with ADC value, voltage, lux, and metadata
        """
        if not HARDWARE_AVAILABLE or not self. is_initialised:
            lux = self._simulate_light()
            return {
                'lux': lux,
                'adc_value': None,
                'voltage': None,
                'simulated':  True
            }
        
        adc_value = self._read_adc_smoothed()
        if adc_value is None: 
            return None
        
        voltage = self._adc_to_voltage(adc_value)
        lux = self._adc_to_lux(adc_value)
        
        return {
            'lux': round(lux, 1),
            'adc_value': adc_value,
            'voltage': round(voltage, 3),
            'simulated': False
        }
    
    def get_light_level_category(self, lux: float = None) -> str:
        """Get human-readable light level category"""
        if lux is None:
            lux = self. read()
            if lux is None:
                return "Unknown"
        
        if lux < 10:
            return "Very Dark"
        elif lux < 50:
            return "Dark"
        elif lux < 150:
            return "Dim"
        elif lux < 400:
            return "Low Light"
        elif lux < 700:
            return "Normal"
        elif lux < 900:
            return "Bright"
        else:
            return "Very Bright"
    
    def _simulate_light(self) -> float:
        """Simulate light readings based on time of day"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        
        if 7 <= hour <= 19:
            peak_factor = 1.0 - abs(hour - 13) / 6.0
            base_lux = 300 + (400 * peak_factor)
            lux = base_lux + random.uniform(-50, 50)
        else:
            lux = random.uniform(10, 50)
        
        return round(lux, 1)
    
    def cleanup(self):
        """Clean up SPI resources"""
        if self.spi:
            try:
                self.spi.close()
                self.logger.info("Light sensor cleaned up")
            except: 
                pass


# ====================================
# STANDALONE TEST
# ====================================

if __name__ == "__main__": 
    """Standalone test mode"""
    import sys
    
    print("=" * 70)
    print("Light Sensor (Photo Transistor + MCP3008) - Standalone Test")
    print("=" * 70)
    
    sensor = LightSensor(smoothing_samples=5, use_calibration=True)
    
    if not sensor.is_initialised and HARDWARE_AVAILABLE:
        print("❌ Sensor failed to initialise")
        print("\nTroubleshooting:")
        print("1. Enable SPI: sudo raspi-config → Interface → SPI")
        print("2. Check MCP3008 power:  3.3V on pins 15 & 16")
        print("3. Verify SPI connections (GPIO 8,9,10,11)")
        sys.exit(1)
    
    print(f"✅ Sensor initialised")
    print(f"   Mode: {'HARDWARE' if HARDWARE_AVAILABLE and sensor.is_initialised else 'SIMULATION'}")
    print(f"   Smoothing: {sensor.smoothing_samples} samples")
    print()
    
    print("Reading light sensor...  (Press Ctrl+C to stop)")
    print("-" * 70)
    print(f"{'Time':<12} {'ADC':<8} {'Voltage':<12} {'Lux':<10} {'Category':<15}")
    print("-" * 70)
    
    try:
        while True:
            data = sensor.read_detailed()
            
            if data:
                lux = data['lux']
                category = sensor.get_light_level_category(lux)
                current_time = time.strftime("%H:%M:%S")
                
                if data['simulated']:
                    print(f"{current_time: <12} {'SIM':<8} {'SIM':<12} {lux:<10. 1f} {category:<15}", end='\r')
                else:
                    adc = data['adc_value']
                    voltage = data['voltage']
                    print(f"{current_time:<12} {adc:<8} {voltage: <12.3f} {lux:<10.1f} {category:<15}", end='\r')
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        
        info = sensor.get_sensor_info()
        print(f"\n📊 Statistics:")
        print(f"   Total reads:    {info['read_count']}")
        print(f"   Errors:         {info['error_count']}")
        print(f"   Success rate:   {sensor. get_success_rate():.1f}%")
        print("=" * 70)
        
    finally:
        sensor.cleanup()
        print("Sensor cleaned up. Goodbye! 👋")