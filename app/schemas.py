from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TrafficPredictionRequest(BaseModel):
    """Request para fazer uma predição de tráfego."""
    route_id: int = Field(..., gt=0, description="ID da rota")
    day_of_week: int = Field(..., ge=0, le=6, description="0=segunda ... 6=domingo")
    hour: int = Field(..., ge=0, le=23, description="Hora do dia")
    average_speed: float = Field(40.0, ge=0, description="Velocidade média estimada em km/h")


class TrafficPredictionResponse(BaseModel):
    """Response com predição completa."""
    route_id: int
    day_of_week: int
    day_of_week_name: str
    hour: int
    predicted_level: str
    predicted_duration: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_peak_hour: bool
    recommendation: str
    alternative_hours: Optional[List[int]] = None
    probability_distribution: Dict[str, float]
    model_version: Optional[str] = None


class BestHoursRequest(BaseModel):
    """Request para buscar melhores horários."""
    route_id: int = Field(..., gt=0)
    day_of_week: int = Field(..., ge=0, le=6)
    start_hour: int = Field(6, ge=0, le=23)
    end_hour: int = Field(23, ge=0, le=23)


class BestHourResponse(BaseModel):
    """Resposta de uma hora prevista no ranking."""
    hour: int = Field(..., ge=0, le=23)
    level: str
    duration: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_peak: bool


class BestHoursResponse(BaseModel):
    """Resposta listando melhores e piores horas."""
    route_id: int
    day_of_week: int
    results: List[BestHourResponse]
    best_hour: int
    worst_hour: int
    best_level: str
    worst_level: str


class RouteInsightsResponse(BaseModel):
    """Análise completa de uma rota."""
    route_id: int
    best_times: Dict[str, List[int]]
    worst_times: Dict[str, List[int]]
    most_common_peak_hour: Optional[int] = None
    most_common_low_traffic_hour: Optional[int] = None


class TrainResponse(BaseModel):
    """Resposta do treinamento."""
    message: str
    accuracy: float = Field(..., ge=0.0, le=1.0)
    samples_used: int = Field(..., ge=0)
    regressor_mae: Optional[float] = Field(None, ge=0)
    regressor_r2: Optional[float] = None


class HealthResponse(BaseModel):
    """Response do health check."""
    status: str
    models_ready: bool
    last_trained: Optional[str] = None
    total_samples: Optional[int] = Field(None, ge=0)
    classifier_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)