from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.hashids import HashIdJSONResponse
from app.modules.auth.router import router as auth_router
from app.modules.images.router import router as images_router
from app.modules.test.router import router as test_router
from app.modules.persons.router import router as persons_router
from app.modules.albums.router import router as albums_router
from app.modules.person_images.router import router as person_images_router

DOCS_URL = "/docs"

app = FastAPI(
    default_response_class=HashIdJSONResponse,
    docs_url=None,
    redoc_url=None,
)
app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get(DOCS_URL, include_in_schema=False)
def custom_swagger_ui_html() -> HTMLResponse:
    swagger_ui = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=settings.APP_ENV,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )
    html = swagger_ui.body.decode("utf-8")
    html = html.replace(
        "const ui = SwaggerUIBundle(",
        "const ui = window.ui = SwaggerUIBundle(",
    )
    html = html.replace(
        "</head>",
        '<style>.swagger-ui .topbar { display: none }</style></head>',
    )
    html = html.replace(
        "</body>",
        '<script src="/public/swagger-init.js"></script></body>',
    )
    return HTMLResponse(html)

app.include_router(auth_router)
app.include_router(images_router)
app.include_router(test_router)
app.include_router(persons_router)
app.include_router(albums_router)
app.include_router(person_images_router)
