import logging
from pathlib import Path
from flask import Flask, jsonify, request

from app.config import get_config
from app.extensions import cors, db, migrate
from app.pubnub_handler import PubNubHandler

# Global PubNub handler
pubnub_handler = None


def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        raise
    
    # Initialize extensions
    cors.init_app(app, origins=config.CORS_ORIGINS)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize PubNub handler
    global pubnub_handler
    pubnub_handler = PubNubHandler(app)
    
    # Log startup info
    app.logger.info("=" * 70)
    app.logger.info("Smart Home IoT Backend Starting")
    app.logger.info("=" * 70)
    app.logger.info(f"Configuration: {config_name or 'default'}")
    
    summary = config.summary()
    for key, value in summary.items():
        app.logger.info(f"  {key}: {value}")
    
    app.logger.info("=" * 70)
    
    return app


def setup_logging(app):
    """Setup application logging"""
    from pathlib import Path
    from app.utils.database_log_handler import DatabaseLogHandler

    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    
    log_file = Path(app.config['LOG_FILE'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging. Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    db_handler = DatabaseLogHandler(app=app, level=logging.WARNING)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(db_handler)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(db_handler)
    app.logger.setLevel(log_level)


def register_blueprints(app):
    """Register Flask blueprints"""
    
    # Import blueprints
    from app.routes import sensor_bp, control_bp, alert_bp, stats_bp
    from app.routes.system_routes import system_bp
    
    # Register with /api prefix
    app.register_blueprint(sensor_bp, url_prefix='/api/sensors')
    app.register_blueprint(control_bp, url_prefix='/api/control')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    
    # Root routes
    @app.route('/')
    def index():
        return jsonify({
            'status': 'ok',
            'message': 'Smart Home IoT Backend API',
            'version': '1.0.0',
            'endpoints': {
                'sensors': '/api/sensors',
                'control': '/api/control',
                'alerts': '/api/alerts',
                'stats': '/api/stats',
                'health': '/health'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'pubnub': 'listening' if pubnub_handler and pubnub_handler.pubnub_service else 'not configured'
        })
    
    app.logger.info("✅ Blueprints registered")


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"400 Bad Request: {error}")
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 Not Found:  {request.path}")
        return jsonify({'error': 'Not found', 'message': str(error)}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        app.logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
        return jsonify({'error': 'Method not allowed', 'message': str(error)}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Internal Server Error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message':  str(error)}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Catch-all for unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500