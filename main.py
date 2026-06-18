from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from routes.agent_routes import agent_router
from routes.mission_routes import mission_router
from routes.report_routes import report_router
from database.db_connection import db
from logs.logger_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting...")
    db.create_db()
    db.connect()
    db.create_tables()
    logger.info("Database initialized")
    yield
    db.close_connection()
    logger.info("Server shutting down...")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception(request, exc):
    err = exc.errors()
    logger.error(f"Validation error: '{err[0]["loc"][-1]}' - {err[0]["msg"]}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=f"Error in filed: '{err[0]["loc"][-1]}' Invalid request format"
        )

@app.exception_handler(HTTPException)
async def http_exception(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
        )

@app.exception_handler(Exception)
async def general_exception(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"status": "error", "message":"Internal server error"}
    )


@app.middleware('http')
async def logger_middleware(req: Request, call_next):
    logger.info(f"{req.method} /{req.url}")
    return await call_next(req)


app.include_router(agent_router, tags=["agents"])
app.include_router(mission_router, tags=["missions"])
app.include_router(report_router, tags=["reports"])