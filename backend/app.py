from web import create_app
from web.config import get_settings
import uvicorn

app = create_app()
settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        'app:app',
        host=settings.host,
        port=settings.port,
        reload = True
    )
