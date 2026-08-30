from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Operational health status", json_schema_extra={"example": "healthy"})
    service: str = Field(default="PULSEiQ Backend", description="Service identifier", json_schema_extra={"example": "PULSEiQ Backend"})
    version: str = Field(default="1.0.0", description="API semantic version", json_schema_extra={"example": "1.0.0"})
    ai_modules: Dict[str, str] = Field(
        default_factory=dict,
        description="Operational status of connected AI/ML modules and fallback services",
    )
    environment: Optional[str] = Field(default="development", description="Runtime environment", json_schema_extra={"example": "development"})
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Health check execution timestamp",
    )
