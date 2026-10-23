from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.weather import WeatherSnapshotResponse
from backend.app.schemas.decision import DecisionResult, CandidateExplanation, SourceReferenceItem, SafetyReviewResult

class FollowupItem(BaseModel):
    id: str
    question: str
    answer: str
    imageStorageKey: Optional[str] = None
    createdAt: datetime

class AssessmentCreateRequest(BaseModel):
    farmId: str = Field(..., description="ID of the farm to assess")
    cropType: str = Field(default="tomato")
    growthStage: str = Field(..., description="e.g. 'seedling', 'vegetative', 'flowering', 'fruiting', 'harvest'")
    farmerReportedSymptoms: List[str] = Field(default_factory=list, description="List of observed symptoms by farmer")

class FollowupSubmitRequest(BaseModel):
    answer: str = Field(..., min_length=2, max_length=1000)

class AssessmentResponse(BaseModel):
    id: str
    ownerUserId: str
    farmId: str
    cropType: str
    growthStage: str
    status: str = Field(..., description="'queued', 'processing', 'awaiting_farmer_input', 'completed', 'failed'")
    imageStorageKey: str
    imageUrl: str
    farmerReportedSymptoms: List[str]
    observations: List[str] = Field(default_factory=list)
    candidateExplanations: List[CandidateExplanation] = Field(default_factory=list)
    weatherSnapshot: Optional[WeatherSnapshotResponse] = None
    sourceReferences: List[SourceReferenceItem] = Field(default_factory=list)
    decision: Optional[DecisionResult] = None
    safetyReview: Optional[SafetyReviewResult] = None
    followups: List[FollowupItem] = Field(default_factory=list)
    failureCode: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    completedAt: Optional[datetime] = None

class AssessmentListItem(BaseModel):
    id: str
    farmId: str
    farmName: Optional[str] = None
    cropType: str
    growthStage: str
    status: str
    primaryCondition: Optional[str] = None
    certaintyLevel: Optional[str] = None
    imageUrl: str
    createdAt: datetime
    completedAt: Optional[datetime] = None
