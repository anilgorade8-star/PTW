import pytest
from backend.app.safety_checks import SafetyChecker

def test_safety_checker_filters_prohibited_advice():
    dangerous_actions = [
        "Prune affected lower leaves to improve air circulation.",
        "Apply heavy streptomycin sulfate spray directly on tomatoes.",
        "Mix with pesticide cocktail in 50 gallon tank for maximum kill.",
        "Spray 1% Bordeaux mixture on leaves."
    ]

    filtered_actions, review = SafetyChecker.evaluate_safety(
        disease_key="bacterial_spot",
        pathogen_type="Xanthomonas (bacterial)",
        recommended_actions=dangerous_actions,
        source_reference={"title": "Test Source", "institution": "IARI"}
    )

    # 1. Prohibited advice must be removed from farmerActionPlan
    assert any("streptomycin" in d for d in review.disallowedRecommendationsFiltered)
    assert any("cocktail" in d for d in review.disallowedRecommendationsFiltered)
    assert len(filtered_actions) == 2
    assert "Prune affected lower leaves to improve air circulation." in filtered_actions
    assert "Spray 1% Bordeaux mixture on leaves." in filtered_actions

    # 2. Statutory PPE and PHI advisories must be present
    assert "Personal Protective Equipment" in review.chemicalSafetyAdvisory
    assert "Pre-Harvest Interval" in review.chemicalSafetyAdvisory

def test_viral_disease_fungicide_warning():
    filtered_actions, review = SafetyChecker.evaluate_safety(
        disease_key="yellow_leaf_curl",
        pathogen_type="Begomovirus (viral)",
        recommended_actions=["Install yellow sticky traps."],
        source_reference={"title": "TYLCV Advisory", "institution": "UAS Bangalore"}
    )

    assert any("Viral Disease Notice" in w for w in review.warningFlags)
