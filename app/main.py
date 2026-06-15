from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import (
    TrafficPredictionRequest, TrafficPredictionResponse, TrainResponse,
    BestHoursRequest, BestHoursResponse, BestHourResponse,
    RouteInsightsResponse, HealthResponse
)
from app.model import predict, models_exist, get_route_insights, predict_best_hours_range, get_metadata
from app.train import train_model
from datetime import datetime

# ---------------------------
# Lifespan (startup / shutdown)
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Estado inicial
    app.state.models_ready = False
    print("\n" + "="*60)
    print("STARTING TRAFFIC AI SERVICE")
    print("="*60)

    try:
        if models_exist():
            print("Models found. Loading metadata...")
            app.state.models_ready = True
            metadata = get_metadata()
            print(f"  last_trained: {metadata.get('trained_at', 'N/A')}")
            acc = metadata.get("classifier_accuracy")
            if acc is not None:
                print(f"  classifier_accuracy: {acc:.2%}")
        else:
            print("No models found. Running initial training...")
            accuracy, samples = train_model()
            app.state.models_ready = True
            print(f"Initial training finished: accuracy={accuracy:.2%}, samples={samples}")
    except Exception as e:
        app.state.models_ready = False
        print("Error during startup:", e)

    yield

    # Shutdown
    print("\n" + "="*60)
    print("SHUTTING DOWN TRAFFIC AI SERVICE")
    print("="*60 + "\n")


# ---------------------------
# App config
# ---------------------------
app = FastAPI(
    title="Traffic AI Service",
    description="Microserviço de ML para previsão inteligente de tráfego em Aracaju",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS: evitar allow_origins=['*'] quando allow_credentials=True
# Defina explicitamente as origens confiáveis (ajuste conforme seu ambiente)
TRUSTED_ORIGINS = [
    "http://localhost:3000",   # frontend dev
    "http://localhost:8080",   # seu Spring Boot se servir frontend
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=TRUSTED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"]
)


# ---------------------------
# Helpers
# ---------------------------
def models_ready() -> bool:
    return bool(getattr(app.state, "models_ready", False))


# ---------------------------
# Endpoints
# ---------------------------
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    metadata = get_metadata()
    return HealthResponse(
        status="online" if models_ready() else "offline",
        models_ready=models_ready(),
        last_trained=metadata.get("trained_at"),
        total_samples=metadata.get("total_samples"),
        classifier_accuracy=metadata.get("classifier_accuracy")
    )


@app.post("/predict", response_model=TrafficPredictionResponse, tags=["Predictions"])
def predict_traffic(request: TrafficPredictionRequest):
    if not models_ready():
        raise HTTPException(status_code=503, detail="models_not_ready")

    try:
        result = predict(
            request.route_id,
            request.day_of_week,
            request.hour,
            request.average_speed
        )
        # result must be a dict matching TrafficPredictionResponse fields
        return TrafficPredictionResponse(
            route_id=request.route_id,
            day_of_week=request.day_of_week,
            hour=request.hour,
            **result
        )
    except ValueError as e:
        # known validation error from model layer
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"prediction_error: {str(e)}")


@app.post("/train", response_model=TrainResponse, tags=["Training"])
def retrain():
    try:
        accuracy, samples = train_model()
        app.state.models_ready = True
        metadata = get_metadata()
        return TrainResponse(
            message="model_retrained",
            accuracy=round(accuracy, 4),
            samples_used=samples,
            regressor_mae=metadata.get("regressor_mae"),
            regressor_r2=metadata.get("regressor_r2")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"validation_error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"training_error: {str(e)}")


@app.get("/best-hours/{route_id}", response_model=BestHoursResponse, tags=["Analytics"])
def get_best_hours(
    route_id: int,
    day_of_week: int = Query(2, ge=0, le=6),
    start_hour: int = Query(6, ge=0, le=23),
    end_hour: int = Query(23, ge=0, le=23)
):
    if start_hour > end_hour:
        raise HTTPException(status_code=400, detail="start_hour_must_be_le_end_hour")
    if not models_ready():
        raise HTTPException(status_code=503, detail="models_not_ready")

    try:
        results = predict_best_hours_range(route_id, day_of_week, start_hour, end_hour)
        if not results:
            raise HTTPException(status_code=404, detail="no_predictions")
        return BestHoursResponse(
            route_id=route_id,
            day_of_week=day_of_week,
            results=[BestHourResponse(**r) for r in results],
            best_hour=results[0]["hour"],
            worst_hour=results[-1]["hour"],
            best_level=results[0]["level"],
            worst_level=results[-1]["level"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"best_hours_error: {str(e)}")


@app.get("/insights/{route_id}", response_model=RouteInsightsResponse, tags=["Analytics"])
def get_route_analysis(route_id: int):
    if not models_ready():
        raise HTTPException(status_code=503, detail="models_not_ready")
    try:
        insights = get_route_insights(route_id)
        return RouteInsightsResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"insights_error: {str(e)}")


@app.get("/status", tags=["System"])
def status():
    metadata = get_metadata()
    return {
        "timestamp": datetime.now().isoformat(),
        "service_status": "online" if models_ready() else "offline",
        "models_loaded": models_ready(),
        "training_info": {
            "last_trained": metadata.get("trained_at"),
            "total_samples_used": metadata.get("total_samples"),
            "test_samples": metadata.get("test_samples"),
            "classifier_accuracy": metadata.get("classifier_accuracy"),
            "regressor_mae_seconds": metadata.get("regressor_mae"),
            "regressor_r2_score": metadata.get("regressor_r2")
        },
        "available_features": metadata.get("feature_columns"),
        "traffic_levels": metadata.get("traffic_levels")
    }


@app.get("/", tags=["Documentation"])
def root():
    return {
        "title": "Traffic AI Service v2.0",
        "description": "Microserviço de ML para previsão de tráfego em Aracaju",
        "docs": {
            "swagger": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc",
            "openapi": "http://localhost:8000/openapi.json"
        },
        "main_endpoints": {
            "predict": {"method": "POST", "url": "/predict", "description": "Prediz nível e duração de tráfego"},
            "best_hours": {"method": "GET", "url": "/best-hours/{route_id}?day_of_week=2", "description": "Retorna ranking de melhores horários"},
            "insights": {"method": "GET", "url": "/insights/{route_id}", "description": "Análise completa de padrões de tráfego"},
            "train": {"method": "POST", "url": "/train", "description": "Re-treina modelo com dados novos"},
            "health": {"method": "GET", "url": "/health", "description": "Verifica saúde do serviço"}
        }
    }


# Local execution helper
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)