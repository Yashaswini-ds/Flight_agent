from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, flights, bookings, payments, refunds, support, feedback, assistant, admin

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Grade Flight Booking Platform with Dual-Agent Architecture & AP2 Payment Protocol Simulation",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(refunds.router)
app.include_router(support.router)
app.include_router(feedback.router)
app.include_router(assistant.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "message": "Flight Booking Platform API",
        "health": "/api/health",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "demo_tax_rate": f"{settings.DEMO_TAX_PERCENTAGE}%"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
