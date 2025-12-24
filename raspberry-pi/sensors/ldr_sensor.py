import spidev
import time
from typing import Optional
from base_sensor import BaseSensor


class LDRSensor(BaseSensor):
    """LDR sensor using MCP3008 via spidev"""
    
    def __init__(self, channel: int = 0):
        super().__init__("light", "lux")
        self.channel = channel
        self.spi = None
        
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 1350000
            self.is_initialised = True
            self.logger.info("LDR sensor initialised (spidev)")
        except Exception as e:
            self.logger.error(f"Failed to initialise LDR:  {e}")
            self.is_initialised = False
    
    def read(self) -> Optional[float]:
        """Read light level from MCP3008"""
        if not self.is_initialised:
            return self._simulate_light()
        
        try:
            # Read MCP3008 (10-bit ADC, 0-1023)
            adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
            data = ((adc[1] & 3) << 8) + adc[2]
            
            # Convert to lux (0-1000 scale)
            lux = (data / 1023.0) * 1000.0
            
            return round(lux, 2)
        except Exception as e: 
            self.logger.error(f"Error reading LDR: {e}")
            return None
    
    def _simulate_light(self) -> float:
        """Simulate light for testing"""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        if 7 <= hour <= 19:
            return round(300 + random.uniform(0, 400), 2)
        else:
            return round(random.uniform(5, 30), 2)
    
    def cleanup(self):
        """Clean up SPI connection"""
        if self.spi:
            self.spi. close()