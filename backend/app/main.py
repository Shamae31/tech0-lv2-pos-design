import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, members, products, purchases, transactions
from app.core.config import DEMO_MODE
from app.core.security import _secret

_secret()
if DEMO_MODE and os.getenv("POS_ENV") != "development":
    raise RuntimeError("デモモードはPOS_ENV=developmentの場合だけ使用できます")

production = os.getenv("POS_ENV", "production") == "production"
app = FastAPI(title="簡易POS API", version="0.2.0", docs_url=None if production else "/docs", redoc_url=None if production else "/redoc", openapi_url=None if production else "/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, members.router, products.router, purchases.router, transactions.router):
    app.include_router(router)


@app.exception_handler(RequestValidationError)
async def safe_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": [{"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]} for error in exc.errors()]})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
