import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# Note: Root models use Pydantic V2
from pydantic import BaseModel, Field, HttpUrl


SERVICE_NAME = os.getenv("SERVICE_NAME", "camera-stream-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")


app = FastAPI(
    title="Camera Stream Service",
    version=SERVICE_VERSION,
    description="Service quản lý luồng camera và gửi dữ liệu phân tích, tuân thủ Contract Lab 03.",
)

# --- Models ---

class AnalysisType(str, Enum):
    PERSON_DETECTION = "PERSON_DETECTION"
    VEHICLE_DETECTION = "VEHICLE_DETECTION"
    INTRUSION_DETECTION = "INTRUSION_DETECTION"

class DetectionType(str, Enum):
    PERSON = "PERSON"
    VEHICLE = "VEHICLE"
    UNKNOWN_OBJECT = "UNKNOWN_OBJECT"

class DetectionStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class BoundingBox(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    width: int = Field(..., ge=1)
    height: int = Field(..., ge=1)

class HealthStatus(BaseModel):
    status: str = "ok"
    service: str
    time: str

class AnalyzeFrameRequest(BaseModel):
    cameraId: str = Field(..., pattern="^CAM-[0-9]{2}$")
    frameUrl: HttpUrl
    timestamp: datetime
    requestId: str
    analysisType: AnalysisType

class DetectionResult(BaseModel):
    detectionId: uuid.UUID
    detectionType: DetectionType
    confidence: float = Field(..., ge=0, le=1)
    cameraId: str
    frameUrl: str
    timestamp: str
    detectedAt: str
    trackingId: Optional[str] = None
    status: DetectionStatus
    boundingBox: BoundingBox

class DetectionPage(BaseModel):
    items: List[DetectionResult]
    nextCursor: Optional[str] = None
    hasMore: bool = False

# --- In-memory Store ---
DETECTIONS: List[DetectionResult] = []

# --- Helpers ---

def build_problem(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    problem_type: str = "about:blank"
) -> Dict:
    return {
        "type": problem_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    problem = exc.detail if isinstance(exc.detail, dict) else build_problem(
        exc.status_code, "Error", str(exc.detail), request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem,
        media_type="application/problem+json"
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_problem(
            422,
            "Validation Error",
            str(exc.errors()),
            request.url.path,
            "https://campus.local/errors/validation"
        ),
        media_type="application/problem+json"
    )

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail=build_problem(401, "Unauthorized", "Invalid or missing token", "/detect")
        )

# --- Endpoints ---

@app.get("/health", response_model=HealthStatus)
async def get_health():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.post("/detect", response_model=DetectionResult, status_code=202, dependencies=[Depends(verify_token)])
async def analyze_frame(payload: AnalyzeFrameRequest):
    # Mock logic: Camera Stream simulates sending a frame and getting a result
    det_type = DetectionType.PERSON if payload.analysisType == AnalysisType.PERSON_DETECTION else DetectionType.VEHICLE

    result = DetectionResult(
        detectionId=uuid.uuid4(),
        detectionType=det_type,
        confidence=0.98,
        cameraId=payload.cameraId,
        frameUrl=str(payload.frameUrl),
        timestamp=payload.timestamp.isoformat(),
        detectedAt=datetime.now(timezone.utc).isoformat(),
        trackingId=f"TRACK-{uuid.uuid4().hex[:6].upper()}",
        status=DetectionStatus.COMPLETED,
        boundingBox=BoundingBox(x=100, y=100, width=50, height=150)
    )
    DETECTIONS.append(result)
    return result

@app.get("/detections", response_model=DetectionPage, dependencies=[Depends(verify_token)])
async def list_detections(cursor: Optional[str] = None, limit: int = 20):
    return DetectionPage(items=DETECTIONS[-limit:], nextCursor=None, hasMore=False)

@app.get("/detections/recent", response_model=DetectionPage, dependencies=[Depends(verify_token)])
async def get_recent_detections(limit: int = 20):
    return DetectionPage(items=DETECTIONS[-limit:], nextCursor=None, hasMore=False)

@app.get("/detections/{detectionId}", response_model=DetectionResult, dependencies=[Depends(verify_token)])
async def get_detection_by_id(detectionId: uuid.UUID):
    for d in DETECTIONS:
        if d.detectionId == detectionId:
            return d
    raise HTTPException(
        status_code=404,
        detail=build_problem(
            404,
            "Not Found",
            f"Detection {detectionId} not found",
            f"/detections/{detectionId}"
        )
    )
