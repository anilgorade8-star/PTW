from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CandidateExplanation(BaseModel):
    diseaseKey: str
    commonName: str
    matchScore: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    supportingEvidence: List[str] = Field(default_factory=list)
    opposingEvidence: List[str] = Field(default_factory=list)
    confidenceRationale: str

class SourceReferenceItem(BaseModel):
    title: str
    institution: str
    url: str
    diseaseKey: str
    region: str
    reviewStatus: str
    limitations: str

class SafetyReviewResult(BaseModel):
    passed: bool
    requiresExpertEscalation: bool = False
    warningFlags: List[str] = Field(default_factory=list)
    chemicalSafetyAdvisory: str
    disallowedRecommendationsFiltered: List[str] = Field(default_factory=list)

class DecisionResult(BaseModel):
    primaryCondition: str
    pathogenOrStressType: str
    certaintyLevel: str = Field(..., description="'high', 'medium', 'low', or 'uncertain'")
    needsFarmerInput: bool = False
    suggestedFollowupQuestion: Optional[str] = None
    farmerActionPlan: List[str] = Field(default_factory=list)
    weatherRiskCorrelation: str
    candidateExplanations: List[CandidateExplanation]
    sourceReferences: List[SourceReferenceItem]
    safetyReview: SafetyReviewResult
