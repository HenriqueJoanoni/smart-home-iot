from . sensor_routes import sensor_bp
from .control_routes import control_bp
from .alert_routes import alert_bp
from .stats_routes import stats_bp

__all__ = [
    'sensor_bp',
    'control_bp',
    'alert_bp',
    'stats_bp'
]