# ====================================
# SENSORS
# ====================================
DHT22_PIN = 4        # GPIO 4  (Physical Pin 7)
LDR_PIN = 17         # GPIO 17 (Physical Pin 11)
PIR_PIN = 27         # GPIO 27 (Physical Pin 13)

# ====================================
# ACTUATORS - LEDS
# ====================================
LED_RED_PIN = 22     # GPIO 22 (Physical Pin 15)
LED_GREEN_PIN = 23   # GPIO 23 (Physical Pin 16)
LED_BLUE_PIN = 24    # GPIO 24 (Physical Pin 18)

# ====================================
# ACTUATORS - BUZZER
# ====================================
BUZZER_PIN = 25      # GPIO 25 (Physical Pin 22)

# ====================================
# MCP3008 ADC (if using for LDR)
# ====================================
SPI_PORT = 0
SPI_DEVICE = 0
MCP3008_LDR_CHANNEL = 0  # CH0 on MCP3008

# ====================================
# GPIO MODE
# ====================================
GPIO_MODE = 'BCM'  # Use BCM numbering (not BOARD)