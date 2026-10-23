export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  isActive: boolean;
  createdAt: string;
}

export interface FarmLocation {
  latitude: number;
  longitude: number;
  address?: string;
  district?: string;
  state?: string;
}

export interface Farm {
  id: string;
  ownerUserId: string;
  name: string;
  location: FarmLocation;
  cropTypes: string[];
  sizeInAcres?: number;
  createdAt: string;
  updatedAt: string;
}

export interface NormalizedWeatherData {
  temperature_c: number;
  relative_humidity_pct: number;
  precipitation_mm: number;
  wind_speed_kmh: number;
  weather_code: number;
  weather_description: string;
  is_risk_favorable_for_fungal: boolean;
  is_risk_favorable_for_bacterial: boolean;
  is_risk_favorable_for_vector: boolean;
}

export interface WeatherSnapshot {
  id?: string;
  farmId: string;
  provider: string;
  fetchedAt: string;
  validTime: string;
  normalizedData: NormalizedWeatherData;
  qualityMetadata?: Record<string, any>;
}

export interface CandidateExplanation {
  diseaseKey: string;
  commonName: string;
  matchScore: number;
  reasoning: string;
  supportingEvidence: string[];
  opposingEvidence: string[];
  confidenceRationale: string;
}

export interface SourceReferenceItem {
  title: string;
  institution: string;
  url: string;
  diseaseKey: string;
  region: string;
  reviewStatus: string;
  limitations: string;
}

export interface SafetyReviewResult {
  passed: boolean;
  requiresExpertEscalation: boolean;
  warningFlags: string[];
  chemicalSafetyAdvisory: string;
  disallowedRecommendationsFiltered: string[];
}

export interface DecisionResult {
  primaryCondition: string;
  pathogenOrStressType: string;
  certaintyLevel: 'high' | 'medium' | 'low' | 'uncertain';
  needsFarmerInput: boolean;
  suggestedFollowupQuestion?: string | null;
  farmerActionPlan: string[];
  weatherRiskCorrelation: string;
  candidateExplanations: CandidateExplanation[];
  sourceReferences: SourceReferenceItem[];
  safetyReview: SafetyReviewResult;
}

export interface FollowupItem {
  id: string;
  question: string;
  answer: string;
  imageStorageKey?: string | null;
  createdAt: string;
}

export interface Assessment {
  id: string;
  ownerUserId: string;
  farmId: string;
  cropType: string;
  growthStage: string;
  status: 'queued' | 'processing' | 'awaiting_farmer_input' | 'completed' | 'failed';
  imageStorageKey: string;
  imageUrl: string;
  farmerReportedSymptoms: string[];
  observations: string[];
  candidateExplanations: CandidateExplanation[];
  weatherSnapshot?: WeatherSnapshot | null;
  sourceReferences: SourceReferenceItem[];
  decision?: DecisionResult | null;
  safetyReview?: SafetyReviewResult | null;
  followups: FollowupItem[];
  failureCode?: string | null;
  createdAt: string;
  updatedAt: string;
  completedAt?: string | null;
}

export interface AssessmentListItem {
  id: string;
  farmId: string;
  farmName?: string;
  cropType: string;
  growthStage: string;
  status: 'queued' | 'processing' | 'awaiting_farmer_input' | 'completed' | 'failed';
  primaryCondition?: string | null;
  certaintyLevel?: string | null;
  imageUrl: string;
  createdAt: string;
  completedAt?: string | null;
}
