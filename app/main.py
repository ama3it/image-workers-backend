from fastapi import FastAPI
from app.api.routes import health
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import http_exception_handler, validation_exception_handler

setup_logging()

app = FastAPI(title="Professional FastAPI Application")
app.add_middleware(LoggingMiddleware)

app.include_router(health.router)


app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
