from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en el arranque (para SQLite / dev)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Sistema de Control de Inventario",
    description="API REST y herramientas MCP para gestión de inventario multi-usuario con control estricto de umbrales mínimos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers.auth import router as auth_router
from app.routers.productos import router as productos_router


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(productos_router)
