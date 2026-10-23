from typing import List, Dict, Any, Tuple, Optional
from backend.app.schemas.decision import (
    DecisionResult,
    CandidateExplanation,
    SourceReferenceItem,
    SafetyReviewResult
)
from backend.app.services.gemini_service import GeminiVisualAnalysis
from backend.app.safety_checks import SafetyChecker
from backend.app.core.logging import logger

class DecisionEngine:
    @classmethod
    def evaluate(
        cls,
        visual_analysis: GeminiVisualAnalysis,
        reported_symptoms: List[str],
        crop_type: str,
        growth_stage: str,
        weather: Dict[str, Any],
        knowledge_sources: List[Dict[str, Any]]
    ) -> DecisionResult:
        """
        Deterministic decision engine for the Farm Evidence Loop.
        Combines visual evidence, reported symptoms, weather risk, and reviewed ICAR sources.
        """
        # If image is unusable, immediately trigger farmer input request
        if not visual_analysis.is_image_usable:
            return cls._handle_unusable_image(visual_analysis, knowledge_sources)

        temp_c = weather.get("temperature_c", 25.0)
        humidity = weather.get("relative_humidity_pct", 65.0)
        precip = weather.get("precipitation_mm", 0.0)

        candidate_explanations: List[CandidateExplanation] = []
        source_reference_items: List[SourceReferenceItem] = []

        all_text_symptoms = " ".join(reported_symptoms + visual_analysis.visible_symptoms).lower()

        for source in knowledge_sources:
            disease_key = source.get("diseaseKey", "")
            common_name = source.get("commonName", "")
            diagnostics = source.get("diagnosticCharacteristics", [])
            favorable_weather = source.get("favorableWeather", {})
            temp_range = favorable_weather.get("temperatureRangeC", [15, 35])
            min_humidity = favorable_weather.get("relativeHumidityMinPct", 60)

            supporting_evidence: List[str] = []
            opposing_evidence: List[str] = []

            # 1. Visual match (Weight: 40%)
            visual_score = 0.0
            matched_diag_count = 0
            for diag in diagnostics:
                diag_lower = diag.lower()
                diag_words = [w for w in diag_lower.split() if len(w) > 3]
                matches = sum(1 for w in diag_words if w in all_text_symptoms)
                if matches >= 2:
                    matched_diag_count += 1
                    supporting_evidence.append(f"Visual pattern matches: '{diag[:80]}...'")

            if matched_diag_count > 0:
                visual_score = min(1.0, 0.4 + (matched_diag_count * 0.2))
            elif disease_key in visual_analysis.preliminary_hypotheses:
                visual_score = 0.6
                supporting_evidence.append(f"Preliminary visual appearance aligns with {common_name}")
            else:
                visual_score = 0.15
                opposing_evidence.append("Key visual characteristics not evident in the photograph")

            # 2. Farmer reported symptoms match (Weight: 30%)
            farmer_score = 0.0
            if reported_symptoms:
                matches_in_symptoms = 0
                for diag in diagnostics:
                    if any(rs.lower() in diag.lower() or diag.lower() in rs.lower() for rs in reported_symptoms):
                        matches_in_symptoms += 1
                if matches_in_symptoms > 0:
                    farmer_score = min(1.0, 0.5 + (matches_in_symptoms * 0.25))
                    supporting_evidence.append(f"Farmer reported symptoms align with known {common_name} manifestation")
                else:
                    farmer_score = 0.2
            else:
                farmer_score = 0.35  # neutral when no symptoms entered

            # 3. Weather correlation (Weight: 20%)
            weather_score = 0.5
            temp_match = (temp_range[0] <= temp_c <= temp_range[1])
            humidity_match = (humidity >= min_humidity)

            if temp_match and humidity_match:
                weather_score = 0.95
                supporting_evidence.append(
                    f"Microclimate ({temp_c:.1f}°C, {humidity:.0f}% RH) is highly favorable for {common_name} progression"
                )
            elif not humidity_match and min_humidity >= 85 and humidity < 55:
                # Contradiction: fungal blight requires high humidity
                weather_score = 0.2
                opposing_evidence.append(
                    f"Current dry microclimate ({humidity:.0f}% RH) is unfavorable for rapid {common_name} spore development"
                )
            else:
                weather_score = 0.5
                supporting_evidence.append(f"Ambient weather ({temp_c:.1f}°C, {humidity:.0f}% RH) is moderately conducive")

            # 4. Growth stage plausibility (Weight: 10%)
            stage_score = 0.7
            if growth_stage in ["flowering", "fruiting", "harvest"] and disease_key in ["early_blight", "bacterial_spot"]:
                stage_score = 0.9
            elif growth_stage in ["seedling", "vegetative"] and disease_key == "yellow_leaf_curl":
                stage_score = 0.9

            # Weighted aggregate score
            aggregate_score = (
                (visual_score * 0.40) +
                (farmer_score * 0.30) +
                (weather_score * 0.20) +
                (stage_score * 0.10)
            )

            # Special case for Healthy foliage
            if disease_key == "healthy":
                if len(visual_analysis.visible_symptoms) == 0 or "healthy" in visual_analysis.preliminary_hypotheses:
                    if not reported_symptoms:
                        aggregate_score = 0.88
                        supporting_evidence.append("Foliage shows vibrant color and absence of necrotic spotting")
                else:
                    aggregate_score = 0.05
                    opposing_evidence.append("Active disease symptoms visible on foliage")

            candidate_explanations.append(
                CandidateExplanation(
                    diseaseKey=disease_key,
                    commonName=common_name,
                    matchScore=round(aggregate_score, 3),
                    reasoning=f"Combined visual confidence ({visual_score:.2f}), farmer symptoms ({farmer_score:.2f}), and weather correlation ({weather_score:.2f}).",
                    supportingEvidence=supporting_evidence,
                    opposingEvidence=opposing_evidence,
                    confidenceRationale=f"Based on reviewed {source.get('institution', 'ICAR')} diagnostic protocols."
                )
            )

            source_reference_items.append(
                SourceReferenceItem(
                    title=source.get("title", ""),
                    institution=source.get("institution", ""),
                    url=source.get("url", ""),
                    diseaseKey=disease_key,
                    region=source.get("region", ""),
                    reviewStatus=source.get("reviewStatus", "reviewed"),
                    limitations=source.get("limitations", "")
                )
            )

        # Sort candidate explanations by matchScore descending
        candidate_explanations.sort(key=lambda x: x.matchScore, reverse=True)
        top_candidate = candidate_explanations[0]
        second_candidate = candidate_explanations[1] if len(candidate_explanations) > 1 else None

        # Determine certainty and ambiguity
        score_diff = (top_candidate.matchScore - second_candidate.matchScore) if second_candidate else 1.0
        
        needs_input = False
        suggested_question = visual_analysis.suggested_followup_question
        certainty = "high"

        if top_candidate.matchScore < 0.55 or score_diff < 0.08:
            certainty = "uncertain"
            needs_input = True
            if second_candidate and not suggested_question:
                suggested_question = (
                    f"Symptoms could indicate either {top_candidate.commonName} or {second_candidate.commonName}. "
                    f"Are the spots mainly on the lower older leaves, or is there curling on new young growth?"
                )
        elif top_candidate.matchScore < 0.75:
            certainty = "medium"
            if len(visual_analysis.missing_evidence) > 0 and not suggested_question:
                suggested_question = f"For confirmation: {visual_analysis.missing_evidence[0]}."
                needs_input = True
        else:
            certainty = "high"

        # Retrieve matched source for top candidate
        top_source = next((s for s in knowledge_sources if s.get("diseaseKey") == top_candidate.diseaseKey), {})
        raw_actions = top_source.get("safeManagementSteps", ["Inspect plants and consult local extension."])

        # Evaluate safety rules
        filtered_actions, safety_review = SafetyChecker.evaluate_safety(
            disease_key=top_candidate.diseaseKey,
            pathogen_type=top_source.get("pathogen", ""),
            recommended_actions=raw_actions,
            source_reference=top_source
        )

        weather_correlation_summary = (
            f"Weather observation: {temp_c:.1f}°C, {humidity:.0f}% RH, {precip:.1f}mm rain. "
            f"Microclimate factors were incorporated as epidemiological risk catalysts, not definitive proof."
        )

        return DecisionResult(
            primaryCondition=top_candidate.commonName,
            pathogenOrStressType=top_source.get("pathogen", "N/A"),
            certaintyLevel=certainty,
            needsFarmerInput=needs_input,
            suggestedFollowupQuestion=suggested_question if needs_input else None,
            farmerActionPlan=filtered_actions,
            weatherRiskCorrelation=weather_correlation_summary,
            candidateExplanations=candidate_explanations,
            sourceReferences=source_reference_items,
            safetyReview=safety_review
        )

    @classmethod
    def _handle_unusable_image(cls, visual_analysis: GeminiVisualAnalysis, knowledge_sources: List[Dict[str, Any]]) -> DecisionResult:
        reason = visual_analysis.unusable_reason or "The uploaded photograph is too blurry, dark, or does not clearly show the plant foliage."
        
        safety = SafetyReviewResult(
            passed=True,
            requiresExpertEscalation=False,
            warningFlags=["Unusable image. Diagnosis deferred until clear photograph provided."],
            chemicalSafetyAdvisory="No chemicals should be applied without a verified diagnosis.",
            disallowedRecommendationsFiltered=[]
        )

        return DecisionResult(
            primaryCondition="Uncertain / Poor Image Quality",
            pathogenOrStressType="Unknown",
            certaintyLevel="uncertain",
            needsFarmerInput=True,
            suggestedFollowupQuestion=f"Please upload a clearer photograph: {reason}",
            farmerActionPlan=[
                "Take a focused photograph in natural daylight.",
                "Ensure both the upper surface and lower surface of affected leaves are visible.",
                "Avoid blurry motion or deep shadows."
            ],
            weatherRiskCorrelation="Weather evaluation deferred pending clear image.",
            candidateExplanations=[],
            sourceReferences=[],
            safetyReview=safety
        )
