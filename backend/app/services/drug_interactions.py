"""Drug interaction detection service"""

from typing import List, Dict, Set, Tuple
from app.models import Intervention, RiskFactor


# Known drug interaction database (simplified version)
# In production, this should be fetched from external APIs like DrugBank, RxNav, etc.
DRUG_INTERACTIONS: Dict[str, List[Dict[str, any]]] = {
    # Warfarin interactions
    "warfarin": [
        {
            "interacting_drug": "aspirin",
            "severity": "high",
            "mechanism": "Increased risk of bleeding",
            "effect_code": "BLEEDING",
            "management": "Monitor INR and signs of bleeding"
        },
        {
            "interacting_drug": "vitamin_e",
            "severity": "moderate",
            "mechanism": "May decrease warfarin effectiveness",
            "effect_code": "REDUCED_EFFICACY",
            "management": "Monitor INR levels"
        },
        {
            "interacting_drug": "natto_kinase",
            "severity": "moderate",
            "mechanism": "Natto kinase may reduce warfarin's effectiveness",
            "effect_code": "REDUCED_EFFICACY",
            "management": "Monitor INR levels"
        },
        {
            "interacting_drug": "garlic",
            "severity": "mild",
            "mechanism": "Possible reduction in warfarin effectiveness",
            "effect_code": "REDUCED_EFFICACY",
            "management": "Inform healthcare provider"
        },
        {
            "interacting_drug": "ginkgo_biloba",
            "severity": "moderate",
            "mechanism": "May increase bleeding risk",
            "effect_code": "BLEEDING",
            "management": "Monitor for bleeding"
        },
    ],
    
    # Statins interactions
    "simvastatin": [
        {
            "interacting_drug": "grapefruit",
            "severity": "moderate",
            "mechanism": "Grapefruit inhibits CYP3A4, increasing statin levels",
            "effect_code": "INCREASED_LEVELS",
            "management": "Avoid grapefruit products"
        },
        {
            "interacting_drug": "fibrates",
            "severity": "high",
            "mechanism": "Increased risk of myopathy/rhabdomyolysis",
            "effect_code": "MYOPATHY_RISK",
            "management": "Monitor muscle symptoms, consider alternative fibrate"
        },
        {
            "interacting_drug": "cyclosporine",
            "severity": "high",
            "mechanism": "Increased risk of myopathy",
            "effect_code": "MYOPATHY_RISK",
            "management": "Monitor CK levels, consider alternative"
        },
    ],
    
    # Metformin interactions
    "metformin": [
        {
            "interacting_drug": "contrast_media_iodine",
            "severity": "high",
            "mechanism": "Contrast iodine can cause lactic acidosis in patients on metformin",
            "effect_code": "LACTIC_ACIDOSIS",
            "management": "Stop metformin before contrast studies, monitor renal function"
        },
        {
            "interacting_drug": "alcohol",
            "severity": "moderate",
            "mechanism": "Increases risk of lactic acidosis",
            "effect_code": "LACTIC_ACIDOSIS",
            "management": "Limit alcohol intake, monitor renal function"
        },
        {
            "interacting_drug": "cimetidine",
            "severity": "mild",
            "mechanism": "May reduce metformin clearance",
            "effect_code": "REDUCED_CLEARANCE",
            "management": "Monitor renal function"
        },
    ],
}


class DrugInteraction:
    """Drug interaction model"""
    def __init__(
        self,
        drug_a: str,
        drug_b: str,
        severity: str,
        mechanism: str,
        effect_code: str,
        management: str
    ):
        self.drug_a = drug_a
        self.drug_b = drug_b
        self.severity = severity  # mild, moderate, high, contraindicated
        self.mechanism = mechanism
        self.effect_code = effect_code
        self.management = management
    
    def to_dict(self) -> dict:
        return {
            "drug_a": self.drug_a,
            "drug_b": self.drug_b,
            "severity": self.severity,
            "mechanism": self.mechanism,
            "effect_code": self.effect_code,
            "management": self.management
        }


def detect_interactions(medications: List[str]) -> List[DrugInteraction]:
    """
    Detect potential drug interactions
    
    Args:
        medications: List of medication names (lowercase, normalized)
    
    Returns:
        List of DrugInteraction objects
    """
    interactions = []
    
    # Normalize medication names
    normalized_meds = [med.lower().replace(" ", "_").replace("-", "_") for med in medications]
    
    # Check each pair of medications
    for i, med_a in enumerate(normalized_meds):
        for med_b in normalized_meds[i + 1:]:
            # Check if med_a has known interactions
            if med_a in DRUG_INTERACTIONS:
                for interaction in DRUG_INTERACTIONS[med_a]:
                    # Normalize interacting drug name for comparison
                    interacting_normalized = interaction["interacting_drug"].lower().replace(" ", "_").replace("-", "_")
                    
                    # Check if med_b matches the interacting drug
                    if med_b == interacting_normalized:
                        interactions.append(DrugInteraction(
                            drug_a=med_a.replace("_", " "),
                            drug_b=interaction["interacting_drug"],
                            severity=interaction["severity"],
                            mechanism=interaction["mechanism"],
                            effect_code=interaction["effect_code"],
                            management=interaction["management"]
                        ))
    
    return interactions


def categorize_interactions_by_severity(interactions: List[DrugInteraction]) -> Dict[str, List[DrugInteraction]]:
    """
    Categorize interactions by severity
    
    Returns:
        Dict with keys: high, moderate, mild
    """
    categorized = {
        "high": [],
        "moderate": [],
        "mild": []
    }
    
    for interaction in interactions:
        if interaction.severity in categorized:
            categorized[interaction.severity].append(interaction)
    
    return categorized


def get_interaction_summary(interactions: List[DrugInteraction]) -> dict:
    """
    Get summary of interactions
    
    Returns:
        Dict with counts and highest severity
    """
    if not interactions:
        return {
            "total": 0,
            "high": 0,
            "moderate": 0,
            "mild": 0,
            "highest_severity": None,
            "recommendation": "No interactions detected"
        }
    
    categorized = categorize_interactions_by_severity(interactions)
    
    # Determine highest severity
    highest_severity = None
    if categorized["high"]:
        highest_severity = "high"
    elif categorized["moderate"]:
        highest_severity = "moderate"
    elif categorized["mild"]:
        highest_severity = "mild"
    
    # Generate recommendation
    recommendation = "No major concerns"
    if highest_severity == "high":
        recommendation = "Consult healthcare provider immediately. Multiple high-severity interactions detected."
    elif highest_severity == "moderate":
        recommendation = "Consult healthcare provider. Moderate interactions detected that require monitoring."
    elif highest_severity == "mild":
        recommendation = "Minor interactions detected. Monitor for any changes."
    
    return {
        "total": len(interactions),
        "high": len(categorized["high"]),
        "moderate": len(categorized["moderate"]),
        "mild": len(categorized["mild"]),
        "highest_severity": highest_severity,
        "recommendation": recommendation
    }
