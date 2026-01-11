import logging
from datetime import datetime, timezone
from app.extensions import db
from app.models.system_log import SystemLog


class DatabaseLogHandler(logging.Handler):
    """
    Custom logging handler that saves logs to database
    
    Only logs WARNING and above to avoid too many records
    """
    
    def __init__(self, app=None, level=logging.WARNING):
        """
        Initialize handler
        
        Args:
            app: Flask app instance (for app context)
            level: Minimum log level (default: WARNING)
        """
        super().__init__(level=level)
        self.app = app
        
        # Formatter
        self.setFormatter(logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        ))
    
    def emit(self, record):
        """
        Emit a log record to database
        
        Args:
            record: LogRecord instance
        """
        # Skip if no app context
        if not self.app:
            return
        
        try:
            with self.app.app_context():
                metadata = {
                    'pathname': record.pathname,
                    'lineno': record.lineno,
                    'funcName': record.funcName,
                    'process': record.process,
                    'thread': record.thread
                }
                
                if record.exc_info:
                    import traceback
                    metadata['exception'] = ''.join(
                        traceback.format_exception(*record.exc_info)
                    )
                
                log_entry = SystemLog(
                    timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc),
                    log_level=record.levelname,
                    source=record.name,
                    message=self.format(record),
                    data=metadata
                )
                
                db.session.add(log_entry)
                db.session.commit()

        except Exception as e:
            print(f"Failed to save log to database: {e}")