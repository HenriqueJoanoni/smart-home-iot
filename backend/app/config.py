import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent.parent
load_dotenv(basedir / '.env')


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # PubNub
    PUBNUB_PUBLISH_KEY = os.getenv('PUBNUB_PUBLISH_KEY', '')
    PUBNUB_SUBSCRIBE_KEY = os.getenv('PUBNUB_SUBSCRIBE_KEY', '')
    PUBNUB_SECRET_KEY = os.getenv('PUBNUB_SECRET_KEY', '')
    PUBNUB_UUID = os.getenv('PUBNUB_UUID', 'backend-server')
    
    # PubNub Channels
    PUBNUB_SENSOR_CHANNEL = os.getenv('PUBNUB_SENSOR_CHANNEL', 'smart-home-sensors')
    PUBNUB_CONTROL_CHANNEL = os.getenv('PUBNUB_CONTROL_CHANNEL', 'smart-home-control')
    PUBNUB_ALERT_CHANNEL = os.getenv('PUBNUB_ALERT_CHANNEL', 'smart-home-alerts')
    
    # PubNub Settings
    PUBNUB_ENABLE_SUBSCRIBE = os.getenv('PUBNUB_ENABLE_SUBSCRIBE', 'True').lower() == 'true'
    PUBNUB_ENABLE_PRESENCE = os.getenv('PUBNUB_ENABLE_PRESENCE', 'True').lower() == 'true'
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/backend.log')
    
    # Alert Thresholds
    ALERT_TEMP_HIGH = float(os.getenv('ALERT_TEMP_HIGH', 30.0))
    ALERT_TEMP_LOW = float(os.getenv('ALERT_TEMP_LOW', 15.0))
    ALERT_HUMIDITY_HIGH = float(os.getenv('ALERT_HUMIDITY_HIGH', 70.0))
    ALERT_HUMIDITY_LOW = float(os.getenv('ALERT_HUMIDITY_LOW', 30.0))
    ALERT_LIGHT_LOW = float(os.getenv('ALERT_LIGHT_LOW', 50.0))
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        errors = []
        
        if not Config.PUBNUB_PUBLISH_KEY or Config.PUBNUB_PUBLISH_KEY == 'your_publish_key_here':
            errors.append("PUBNUB_PUBLISH_KEY not configured")
        
        if not Config.PUBNUB_SUBSCRIBE_KEY or Config.PUBNUB_SUBSCRIBE_KEY == 'your_subscribe_key_here':
            errors.append("PUBNUB_SUBSCRIBE_KEY not configured")
        
        if not Config.SQLALCHEMY_DATABASE_URI:
            errors.append("DATABASE_URL not configured in .env")
        elif not Config.SQLALCHEMY_DATABASE_URI.startswith('postgresql'):
            errors.append("DATABASE_URL must be PostgreSQL (starts with postgresql://)")
        
        if errors:
            raise ValueError(
                "Configuration errors:\n  - " + "\n  - ".join(errors) +
                "\n\nPlease check your .env file"
            )
        
        return True
    
    @staticmethod
    def summary():
        """Get configuration summary (safe for logging)"""
        
        # Parse DATABASE_URL
        db_url = Config.SQLALCHEMY_DATABASE_URI
        
        if db_url and 'postgresql://' in db_url:
            try:
                parts = db_url.split('@')
                if len(parts) == 2:
                    host_part = parts[1]
                    if '/' in host_part:
                        host_db = host_part.split('/')
                        host_port = host_db[0]
                        dbname = host_db[1].split('?')[0]
                        db_info = f"postgresql://{host_port}/{dbname}"
                    else: 
                        db_info = "postgresql://configured"
                else:
                    db_info = "postgresql://configured"
            except:
                db_info = "postgresql://configured"
        else:
            db_info = "NOT CONFIGURED"
        
        return {
            'debug': Config.DEBUG,
            'host': Config.HOST,
            'port':  Config.PORT,
            'pubnub_uuid': Config.PUBNUB_UUID,
            'pubnub_configured': bool(Config.PUBNUB_PUBLISH_KEY and Config.PUBNUB_SUBSCRIBE_KEY),
            'pubnub_subscribe_enabled': Config.PUBNUB_ENABLE_SUBSCRIBE,
            'channels': {
                'sensor': Config.PUBNUB_SENSOR_CHANNEL,
                'control': Config.PUBNUB_CONTROL_CHANNEL,
                'alert':  Config.PUBNUB_ALERT_CHANNEL
            },
            'database': db_info
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration by name"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)