from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.api.routes import health, payment, upload

setup_logging()

app = FastAPI(title="Image task FastAPI Application")
app.add_middleware(LoggingMiddleware)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(payment.router)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
