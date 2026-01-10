import os
from dotenv import load_dotenv

load_dotenv()

# ====================================
# MODE
# ====================================
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'false').lower() == 'true'

# ====================================
# PUBNUB CONFIGURATION
# ====================================
PUBNUB_PUBLISH_KEY = os.getenv('PUBNUB_PUBLISH_KEY', '')
PUBNUB_SUBSCRIBE_KEY = os.getenv('PUBNUB_SUBSCRIBE_KEY', '')
PUBNUB_SENSOR_CHANNEL = os.getenv('PUBNUB_SENSOR_CHANNEL', 'smart-home-sensors')
PUBNUB_CONTROL_CHANNEL = os.getenv('PUBNUB_CONTROL_CHANNEL', 'smart-home-control')
PUBNUB_UUID = os.getenv('PUBNUB_UUID', 'raspberry-pi-main')

# ====================================
# SENSOR SETTINGS
# ====================================
SENSOR_READ_INTERVAL = int(os.getenv('SENSOR_READ_INTERVAL', '5'))  # seconds
USE_MCP3008_FOR_LDR = os.getenv('USE_MCP3008_FOR_LDR', 'true').lower() == 'true'

# ====================================
# LOCATION
# ====================================
DEVICE_LOCATION = os.getenv('DEVICE_LOCATION', 'living_room')
DEVICE_ID = os.getenv('DEVICE_ID', 'raspberry_pi_main')

# ====================================
# LOGGING
# ====================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/raspberry_pi.log')

# ====================================
# VALIDATION
# ====================================
def validate_config():
    """Validate required configuration"""
    errors = []
    
    if not PUBNUB_PUBLISH_KEY:
        errors.append("PUBNUB_PUBLISH_KEY not set")
    if not PUBNUB_SUBSCRIBE_KEY:
        errors.append("PUBNUB_SUBSCRIBE_KEY not set")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True