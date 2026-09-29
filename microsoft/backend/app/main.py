from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analysis, markets, ventures, competitors, simulation, trajectory, maps, customers, hindsight_routes, context_routes
from app.config import settings

app = FastAPI(
    title="VentureScope API",
    description="Venture Intelligence Platform - Evidence-grounded market analysis and venture simulation",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(context_routes.router, prefix="/api/context", tags=["Context"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(markets.router, prefix="/api/markets", tags=["Markets"])
app.include_router(ventures.router, prefix="/api/ventures", tags=["Ventures"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(trajectory.router, prefix="/api/trajectory", tags=["Trajectory"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(hindsight_routes.router, prefix="/api/hindsight", tags=["Hindsight"])

@app.get("/")
async def root():
    return {
        "name": "VentureScope API",
        "version": "0.1.0",
        "status": "operational",
        "description": "Evidence-grounded venture intelligence platform"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}
