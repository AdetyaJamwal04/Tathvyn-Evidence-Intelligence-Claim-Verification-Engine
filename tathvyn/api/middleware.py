"""RFC-7807 Problem Details Error Handling Middleware."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from tathvyn.api.schemas import RFC7807ProblemDetails
from tathvyn.common.exceptions import (
    VeriFactException,
)
from tathvyn.common.logging import get_logger

logger = get_logger("api_middleware")


def setup_error_handlers(app: FastAPI) -> None:
    """Register RFC-7807 exception handlers on FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        invalid_params = [
            {
                "name": " -> ".join(str(loc) for loc in err.get("loc", [])),
                "reason": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in errors
        ]
        problem = RFC7807ProblemDetails(
            type="https://Tathvyn.org/errors/validation-error",
            title="Request Validation Error",
            status=422,
            detail="One or more fields failed structural validation.",
            instance=str(request.url.path),
            error_code="VALIDATION_ERROR",
            invalid_params=invalid_params,
        )
        return JSONResponse(status_code=422, content=problem.model_dump(mode="json"))

    @app.exception_handler(VeriFactException)
    async def verifact_exception_handler(request: Request, exc: VeriFactException) -> JSONResponse:
        status_code = exc.status_code
        error_type = f"https://Tathvyn.org/errors/{exc.error_code.lower().replace('_', '-')}"

        logger.warning(
            "VeriFact domain exception caught",
            error_code=exc.error_code,
            status_code=status_code,
            message=exc.message,
            path=str(request.url.path),
        )

        problem = RFC7807ProblemDetails(
            type=error_type,
            title=exc.error_code.replace("_", " ").title(),
            status=status_code,
            detail=exc.message,
            instance=str(request.url.path),
            error_code=exc.error_code,
            invalid_params=[],
        )
        return JSONResponse(status_code=status_code, content=problem.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled server exception", error=str(exc), path=str(request.url.path))
        problem = RFC7807ProblemDetails(
            type="https://Tathvyn.org/errors/internal-error",
            title="Internal Server Error",
            status=500,
            detail="An unexpected internal error occurred during request processing.",
            instance=str(request.url.path),
            error_code="INTERNAL_SERVER_ERROR",
            invalid_params=[],
        )
        return JSONResponse(status_code=500, content=problem.model_dump(mode="json"))
