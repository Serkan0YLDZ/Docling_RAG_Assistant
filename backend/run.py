import os

from app import create_app
from app.env_loader import load_repo_env

load_repo_env()
app = create_app()

if __name__ == "__main__":
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")
    print(f"API http://127.0.0.1:{port}/api/health")
    app.run(host=host, port=port, debug=debug)
