import pytest
from backend.app.decision_engine import DecisionEngine
from backend.app.services.gemini_service import GeminiVisualAnalysis
from backend.app.services.knowledge_service import KnowledgeService

@pytest.fixture
def mock_sources():
    return [
        {
            "diseaseKey": "early_blight",
            "commonName": "Early Blight",
            "pathogen": "Alternaria solani",
            "diagnosticCharacteristics": [
                "Concentric dark rings forming target board or bullseye pattern on older leaves",
                "Yellow chlorotic halo surrounding brown or dark brown necrotic spots",
                "Lower canopy foliage infected first"
            ],
            "favorableWeather": {
                "temperatureRangeC": [24, 30],
                "relativeHumidityMinPct": 80
            },
            "safeManagementSteps": ["Prune affected lower leaves", "Mulch base"],
            "institution": "ICAR-IIHR",
            "url": "https://www.iihr.res.in",
            "region": "South Asia",
            "reviewStatus": "reviewed",
            "limitations": "Check progression."
        },
        {
            "diseaseKey": "late_blight",
            "commonName": "Late Blight",
            "pathogen": "Phytophthora infestans",
            "diagnosticCharacteristics": [
                "Water-soaked pale to dark green irregular lesions turning brown-black rapidly",
                "White or grayish downy fungal-like growth visible on underside of leaves"
            ],
            "favorableWeather": {
                "temperatureRangeC": [12, 22],
                "relativeHumidityMinPct": 90
            },
            "safeManagementSteps": ["Rogue infected plants", "Spray Bordeaux mixture"],
            "institution": "TNAU",
            "url": "https://agritech.tnau.ac.in",
            "region": "Highlands",
            "reviewStatus": "reviewed",
            "limitations": "Rapidly destructive."
        },
        {
            "diseaseKey": "yellow_leaf_curl",
            "commonName": "Tomato Yellow Leaf Curl Virus (TYLCV)",
            "pathogen": "Begomovirus",
            "diagnosticCharacteristics": [
                "Marked stunting and erect bushy appearance of plants",
                "Upward curling and cupping of leaflet margins with pronounced yellowing"
            ],
            "favorableWeather": {
                "temperatureRangeC": [28, 38],
                "relativeHumidityMinPct": 40
            },
            "safeManagementSteps": ["Install yellow sticky traps", "Neem oil spray"],
            "institution": "UAS Bangalore",
            "url": "https://uasbangalore.edu.in",
            "region": "Tropical",
            "reviewStatus": "reviewed",
            "limitations": "Viral."
        },
        {
            "diseaseKey": "healthy",
            "commonName": "Healthy Tomato Foliage",
            "pathogen": "None",
            "diagnosticCharacteristics": [
                "Uniform vibrant green foliage without chlorotic spots",
                "Vigorous stem and leaf turgidity"
            ],
            "favorableWeather": {
                "temperatureRangeC": [20, 28],
                "relativeHumidityMinPct": 50
            },
            "safeManagementSteps": ["Continue scheduled drip irrigation"],
            "institution": "ICAR-NAARM",
            "url": "https://naarm.org.in",
            "region": "General",
            "reviewStatus": "reviewed",
            "limitations": "None."
        }
    ]

def test_early_blight_reasoning(mock_sources):
    obs = GeminiVisualAnalysis(
        is_image_usable=True,
        visible_symptoms=["Concentric dark rings with target board appearance on lower leaves", "Yellow halo"],
        affected_plant_parts=["lower leaves"],
        preliminary_hypotheses=["early_blight"],
        missing_evidence=[],
        suggested_followup_question=None
    )
    weather = {"temperature_c": 26.5, "relative_humidity_pct": 85.0, "precipitation_mm": 1.2}
    
    decision = DecisionEngine.evaluate(
        visual_analysis=obs,
        reported_symptoms=["brown bullseye spots on bottom leaves", "yellow halo around spots"],
        crop_type="tomato",
        growth_stage="vegetative",
        weather=weather,
        knowledge_sources=mock_sources
    )

    assert decision.primaryCondition == "Early Blight"
    assert decision.certaintyLevel in ["high", "medium"]
    assert len(decision.farmerActionPlan) > 0
    assert "ICAR-IIHR" in decision.sourceReferences[0].institution

def test_unusable_image_triggers_clarification(mock_sources):
    obs = GeminiVisualAnalysis(
        is_image_usable=False,
        unusable_reason="Camera out of focus; blur obscures leaf surface texture.",
        visible_symptoms=[],
        affected_plant_parts=[],
        preliminary_hypotheses=[],
        missing_evidence=["Clear sharp leaf focus"],
        suggested_followup_question=None
    )
    weather = {"temperature_c": 24.0, "relative_humidity_pct": 60.0}

    decision = DecisionEngine.evaluate(
        visual_analysis=obs,
        reported_symptoms=["leaf problems"],
        crop_type="tomato",
        growth_stage="vegetative",
        weather=weather,
        knowledge_sources=mock_sources
    )

    assert decision.certaintyLevel == "uncertain"
    assert decision.needsFarmerInput is True
    assert "clearer photograph" in decision.suggestedFollowupQuestion.lower()
