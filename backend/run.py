from app import create_app
from app.config import get_config

# Create Flask app
app = create_app()

if __name__ == '__main__': 
    config = get_config()
    
    print("\n" + "=" * 70)
    print("🚀 Starting Smart Home IoT Backend")
    print("=" * 70)
    print(f"Environment: {config.__name__}")
    print(f"Debug: {config.DEBUG}")
    print(f"URL: http://{config.HOST}:{config. PORT}")
    print("=" * 70 + "\n")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )