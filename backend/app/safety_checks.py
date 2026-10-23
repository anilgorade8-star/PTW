from typing import List, Dict, Any, Tuple
from backend.app.schemas.decision import SafetyReviewResult

PROHIBITED_CHEMICAL_PATTERNS = [
    ("streptomycin", "Unauthorized agricultural antibiotic usage is strictly prohibited due to antimicrobial resistance (AMR) risks."),
    ("cocktail", "Unverified chemical tank mixes or cocktails cause phytotoxicity and severe chemical hazards."),
    ("mix with pesticide", "Do not combine random chemical products without explicit compatibility guidelines."),
    ("ddt", "Banned organochlorine pesticide."),
    ("endosulfan", "Banned pesticide hazardous to human health.")
]

class SafetyChecker:
    @classmethod
    def evaluate_safety(
        cls,
        disease_key: str,
        pathogen_type: str,
        recommended_actions: List[str],
        source_reference: Dict[str, Any]
    ) -> Tuple[List[str], SafetyReviewResult]:
        """
        Filters recommendations against agricultural safety rules.
        Attaches statutory chemical and personal safety advisories.
        """
        filtered_actions: List[str] = []
        disallowed: List[str] = []
        warning_flags: List[str] = []

        # 1. Biological match check
        if disease_key == "yellow_leaf_curl" or "virus" in pathogen_type.lower():
            warning_flags.append(
                "Viral Disease Notice: Chemical fungicides have zero biological efficacy against plant viruses. Vector management (whitefly suppression) is essential."
            )

        # 2. Check each recommended action for dangerous chemical advice
        for action in recommended_actions:
            action_lower = action.lower()
            blocked = False
            for pattern, reason in PROHIBITED_CHEMICAL_PATTERNS:
                if pattern in action_lower:
                    disallowed.append(f"{action} (Reason: {reason})")
                    blocked = True
                    break
            if not blocked:
                filtered_actions.append(action)

        # 3. Add statutory PPE and Pre-Harvest Interval (PHI) guidance
        chemical_advisory = (
            "Safety Advisory: Always wear Personal Protective Equipment (gloves, eye protection, respirator) "
            "during any spraying operation. Adhere strictly to the Pre-Harvest Interval (PHI) specified on the approved product label. "
            "Never spray against wind direction or during high noon heat."
        )

        requires_escalation = False
        if disease_key in ["late_blight"]:
            requires_escalation = True
            warning_flags.append(
                "High Severity Warning: Late Blight is an aggressive, fast-moving pathogen. "
                "Consult the nearest Krishi Vigyan Kendra (KVK) or State Agricultural University extension immediately."
            )

        result = SafetyReviewResult(
            passed=len(disallowed) == 0,
            requiresExpertEscalation=requires_escalation,
            warningFlags=warning_flags,
            chemicalSafetyAdvisory=chemical_advisory,
            disallowedRecommendationsFiltered=disallowed
        )

        return filtered_actions, result
