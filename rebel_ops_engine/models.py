from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Channel(Enum):
    INTERGALACTIC_WHATSAPP = "intergalactic_whatsapp"
    HOLOGRAM_EMAIL = "hologram_email"


class MessageStatus(Enum):
    NEW = "new"
    SECURITY_REVIEW = "security_review"
    FLAGGED = "flagged"
    QUARANTINED = "quarantined"
    ROUTED = "routed"
    ASSIGNED = "assigned"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    COMPLETED = "completed"
    ERROR = "error"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JediCaseType(Enum):
    NONE = "none"
    TRAINING = "training"
    DIPLOMACY = "diplomacy"
    MEDIATION = "mediation"
    STRATEGY = "strategy"
    MENTORSHIP = "mentorship"
    FORCE_SENSITIVE = "force_sensitive"
    ETHICS = "ethics"
    SPECIAL_MISSION = "special_mission"


class Category(Enum):
    CALENDAR_BOOKING = "calendar_booking"
    PLANET_HELP = "planet_help"
    RECRUITMENT = "recruitment"
    SOLDIER_SUPPORT = "soldier_support"
    POPULATION_TRAINING = "population_training"
    LOGISTICS = "logistics"
    INVESTOR_PARTNER = "investor_partner"
    URGENT_SECURITY = "urgent_security"
    JEDI_TRAINING_DIPLOMACY = "jedi_training_diplomacy"
    AHSOKA_SPECIAL_MISSION = "ahsoka_special_mission"
    YODA_ENCRYPTED_STRATEGY = "yoda_encrypted_strategy"
    FIELD_OPERATIONS = "field_operations"
    SPECIAL_PROTECTION = "special_protection"
    DATA_SUPPORT = "data_support"
    OTHER = "other"


class Owner(Enum):
    GENERAL_LEIA = "General Leia"
    YODA = "Yoda"
    LUKE_BEN = "Luke Skywalker + Ben Kenobi"
    AHSOKA_TANO = "Ahsoka Tano"
    R2D2 = "R2-D2"
    HAN_SOLO = "Han Solo"
    CHEWBACCA = "Chewbacca"
    DIN_DJARIN = "Din Djarin"
    GROGU_CARE = "Grogu Care Team"
    BB8 = "BB-8"
    JEDI_COUNCIL = "Jedi Council"
    REBEL_DEFENSE = "Rebel Defense Team"
    REBEL_RECRUITMENT = "Rebel Recruitment Team"
    SECURITY_TEAM = "Security Team"
    PARTNERSHIPS_TEAM = "Partnerships Team"
    OPERATIONS_TEAM = "Operations Team"
    TRAINING_TEAM = "Training Team"
    LOGISTICS_TEAM = "Logistics Team"
    PROTECTION_TEAM = "Protection Team"
    FIELD_OPS_TEAM = "Field Operations Team"
    EXECUTIVE_OFFICE = "Executive Office"
    OPERATIONS_ANALYTICS = "Operations Analytics"
    SPECIAL_MISSION_REVIEW = "Special Mission Review"
    INTAKE_REVIEW = "Intake Review"


@dataclass
class Message:
    channel: Channel
    sender: str
    content: str
    id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    category: Optional[Category] = None
    owner: Optional[Owner] = None
    status: MessageStatus = MessageStatus.NEW
    risk_score: int = 0
    encrypted: bool = False
    error: Optional[str] = None
    processed_by: list[str] = field(default_factory=list)

    priority: str = "medium"
    security_risk: str = "low"
    jedi_case_type: str = "none"
    requires_leia: bool = False
    requires_jedi: bool = False
    trusted_request: bool = True
    dark_side_indicators: list[str] = field(default_factory=list)
    summary: str = ""
    suggested_next_action: str = ""
    assigned_team: str = ""
    sender_contact: str = ""
    subject: str = ""
    planet_or_sector: str = ""
    proposals: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)


@dataclass
class CalendarBooking:
    message_id: str
    requestor: str
    date: str
    time: str
    duration: str
    subject: str
    is_private: bool = False
    attendees: list[str] = field(default_factory=list)


@dataclass
class Task:
    id: str
    request_id: str
    owner: str
    assigned_team: str
    title: str
    description: str
    priority: str = "medium"
    status: str = "open"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EncryptedTransmission:
    id: str
    request_id: str
    recipient: str
    ciphertext: str
    encryption_method: str = "demo_reverse_string"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DailyBriefing:
    date: str
    total_messages: int
    quarantined: int
    encrypted: int
    by_category: dict
    by_owner: dict
    urgent_items: list
    calendar_bookings: list
    critical_items: list = field(default_factory=list)
    security_items: list = field(default_factory=list)
    leia_decisions: list = field(default_factory=list)
    blocked_items: list = field(default_factory=list)
    recommended_focus: str = ""
