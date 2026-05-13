import re

from models import Owner

SENDER_HIGH_RISK_NAMES = [
    "emperor palpatine",
    "darth vader",
]

HIGH_RISK_KEYWORDS = [
    "emperor palpatine",
    "darth vader",
    "secret rebel base",
    "private leia schedule",
    "bypass security",
    "rebel intelligence",
    "sith",
    "imperial surveillance",
    "sabotage",
    "spying",
    "infiltration",
]

MEDIUM_RISK_KEYWORDS = [
    "empire",
    "imperial forces",
    "stormtroopers",
    "imperial patrol",
]

SENSITIVE_KEYWORDS = [
    "base location", "coordinates", "safe house",
    "meeting point", "supply route", "hidden base",
    "rebel identities", "agent list", "informant name",
    "patrol schedule", "operation time", "departure time",
    "movement plan", "supply delivery", "rendezvous",
    "frequency", "encrypted channel", "code name",
]

TRUSTED_SENDERS = [
    "leia", "mon mothma", "han solo", "chewbacca",
    "luke skywalker", "ben kenobi", "ahsoka tano",
    "r2-d2", "c-3po", "yoda", "din djarin",
]

CATEGORY_OWNER = {
    "calendar_booking": Owner.GENERAL_LEIA,
    "planet_help": Owner.REBEL_DEFENSE,
    "recruitment": Owner.REBEL_RECRUITMENT,
    "soldier_support": Owner.OPERATIONS_TEAM,
    "population_training": Owner.LUKE_BEN,
    "logistics": Owner.HAN_SOLO,
    "investor_partner": Owner.PARTNERSHIPS_TEAM,
    "urgent_security": Owner.SECURITY_TEAM,
    "jedi_training_diplomacy": Owner.LUKE_BEN,
    "ahsoka_special_mission": Owner.AHSOKA_TANO,
    "yoda_encrypted_strategy": Owner.YODA,
    "field_operations": Owner.CHEWBACCA,
    "special_protection": Owner.DIN_DJARIN,
    "data_support": Owner.R2D2,
    "other": Owner.OPERATIONS_TEAM,
}

CATEGORY_TEAM = {
    "calendar_booking": "Executive Office",
    "planet_help": "Defense Team",
    "recruitment": "Recruitment Team",
    "soldier_support": "Operations",
    "population_training": "Jedi Training & Diplomacy Team",
    "logistics": "Logistics Team",
    "investor_partner": "Partnerships",
    "urgent_security": "Security Team",
    "jedi_training_diplomacy": "Jedi Training & Diplomacy Team",
    "ahsoka_special_mission": "Special Mission Review",
    "yoda_encrypted_strategy": "Jedi Council",
    "field_operations": "Field Operations",
    "special_protection": "Protection Team",
    "data_support": "Operations Analytics",
    "other": "Intake Review",
}

CATEGORY_REQUIRES_LEIA = {
    "calendar_booking": True,
    "planet_help": False,
    "recruitment": False,
    "soldier_support": False,
    "population_training": False,
    "logistics": False,
    "investor_partner": False,
    "urgent_security": True,
    "jedi_training_diplomacy": False,
    "ahsoka_special_mission": True,
    "yoda_encrypted_strategy": False,
    "field_operations": False,
    "special_protection": True,
    "data_support": False,
    "other": False,
}

CATEGORY_REQUIRES_JEDI = {
    "calendar_booking": False,
    "planet_help": False,
    "recruitment": False,
    "soldier_support": False,
    "population_training": True,
    "logistics": False,
    "investor_partner": False,
    "urgent_security": False,
    "jedi_training_diplomacy": True,
    "ahsoka_special_mission": True,
    "yoda_encrypted_strategy": True,
    "field_operations": False,
    "special_protection": False,
    "data_support": False,
    "other": False,
}

CATEGORY_NEXT_ACTION = {
    "calendar_booking": "Check Leia's availability and propose three time slots",
    "planet_help": "Dispatch planetary aid team and assess crisis level",
    "recruitment": "Send recruitment intake package and schedule orientation",
    "soldier_support": "Route to Operations for resource allocation",
    "population_training": "Assign trainers and prepare civilian curriculum",
    "logistics": "Coordinate supply route and assign transport",
    "investor_partner": "Schedule partnership follow-up and send materials",
    "urgent_security": "Immediate threat verification and emergency protocol",
    "jedi_training_diplomacy": "Assess case type and assign appropriate Jedi resource",
    "ahsoka_special_mission": "Review special mission dossier and assess risk",
    "yoda_encrypted_strategy": "Encrypt strategic question and transmit to Yoda",
    "field_operations": "Deploy field support and coordinate backup",
    "special_protection": "Activate protection protocol and assign security detail",
    "data_support": "Retrieve relevant records and prepare data summary",
    "other": "Review and determine appropriate handling",
}


def calculate_risk_score(combined_text: str, sender: str = "") -> int:
    text_lower = combined_text.lower()
    score = 0
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            score += 25
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in text_lower:
            score += 10
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            score += 15
    score = min(score, 100)
    return score


def get_sender_min_risk(sender: str) -> int:
    sender_lower = sender.lower()
    for name in SENDER_HIGH_RISK_NAMES:
        if name in sender_lower:
            return 50
    return 0


def get_sender_unknown_risk(sender: str) -> int:
    sender_lower = sender.lower().strip()
    if not sender_lower:
        return 15
    for trusted in TRUSTED_SENDERS:
        if trusted in sender_lower:
            return 0
    words = sender_lower.split()
    if len(words) < 2:
        return 15
    if any(w in ("stranger", "guest", "unknown", "anonymous") for w in words):
        return 15
    return 0


def is_high_risk(risk_score: int) -> bool:
    return risk_score >= 50


def is_yoda_strategy(content: str, category: str = None, sender: str = "") -> bool:
    content_lower = content.lower()
    sender_lower = sender.lower()
    if category == "yoda_encrypted_strategy":
        return True
    has_yoda_indicators = (
        ("yoda" in sender_lower or "yoda" in content_lower)
        and any(
            word in content_lower
            for word in ["strategy", "train", "jedi", "force", "encrypt", "dagobah"]
        )
    )
    return has_yoda_indicators


def contains_private_leia_info(content: str) -> bool:
    content_lower = content.lower()
    return bool(re.search(r'\bprivate\b', content_lower)) \
       and bool(re.search(r'\bleia\b', content_lower))
