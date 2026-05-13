"""
C3POClassifierAgent — Executive Operations Assistant

Classifies incoming requests and recommends the best owner.

Prompt (documentation):
    You are C-3PO, Executive Operations Assistant to General Leia.
    Categories: calendar_booking, planet_help, recruitment, soldier_support,
    population_training, logistics, investor_partner, urgent_security,
    jedi_training_diplomacy, ahsoka_special_mission, yoda_encrypted_strategy,
    field_operations, special_protection, data_support, other.

    Decision rules:
    - Meeting with Leia -> calendar_booking
    - Planet needing help, aid, defense -> planet_help
    - Someone wants to join -> recruitment
    - Rebel soldier needs help -> soldier_support
    - Civilians need training -> population_training
    - Supplies, delivery, transport -> logistics
    - Allies, senators, donors -> investor_partner
    - Immediate threat, stormtroopers nearby -> urgent_security
    - Training, diplomacy, mediation, mentorship -> jedi_training_diplomacy
    - Complex unclear mission requiring judgment -> ahsoka_special_mission
    - Long-term strategic ethical question -> yoda_encrypted_strategy
    - Repairs, field support -> field_operations
    - Protection, extraction, confidential transport -> special_protection
    - Status report, data lookup -> data_support
    - Force-sensitive vulnerable case -> jedi_training_diplomacy / Grogu Care Team
    - If unclear -> other
"""

import logging

from agents.base import Agent
from models import Category, JediCaseType, Message
from security import (
    CATEGORY_NEXT_ACTION,
    CATEGORY_REQUIRES_JEDI,
    CATEGORY_REQUIRES_LEIA,
)

logger = logging.getLogger(__name__)


def any_word_starts_with(text: str, prefix: str) -> bool:
    return any(w.lower().startswith(prefix) for w in text.split())


CATEGORY_RULES: list[tuple[str, Category]] = [
    ("yoda", "strategy", Category.YODA_ENCRYPTED_STRATEGY),
    ("yoda", "encrypt", Category.YODA_ENCRYPTED_STRATEGY),
    ("yoda", "dagobah", Category.YODA_ENCRYPTED_STRATEGY),
    ("should", "join", Category.YODA_ENCRYPTED_STRATEGY),
    ("join", "openly", Category.YODA_ENCRYPTED_STRATEGY),
    ("grogu", "force", Category.JEDI_TRAINING_DIPLOMACY),
    ("grogu", "train", Category.JEDI_TRAINING_DIPLOMACY),
    ("grogu", "sensitive", Category.JEDI_TRAINING_DIPLOMACY),
    ("sense", "danger", Category.JEDI_TRAINING_DIPLOMACY),
    ("child", "empire", Category.JEDI_TRAINING_DIPLOMACY),
    ("force", "child", Category.JEDI_TRAINING_DIPLOMACY),
    ("force", "sensitive", Category.JEDI_TRAINING_DIPLOMACY),
    ("private", "meeting", Category.CALENDAR_BOOKING),
    ("briefing", "leia", Category.CALENDAR_BOOKING),
    ("briefing", "funding", Category.CALENDAR_BOOKING),
    ("calendar", Category.CALENDAR_BOOKING),
    ("booking", Category.CALENDAR_BOOKING),
    ("schedule", Category.CALENDAR_BOOKING),
    ("briefing", Category.CALENDAR_BOOKING),
    ("informant", Category.SPECIAL_PROTECTION),
    ("extraction", Category.SPECIAL_PROTECTION),
    ("senator", Category.INVESTOR_PARTNER),
    ("funding", Category.INVESTOR_PARTNER),
    ("donor", Category.INVESTOR_PARTNER),
    ("sponsor", Category.INVESTOR_PARTNER),
    ("alliance", Category.INVESTOR_PARTNER),
    ("investor", Category.INVESTOR_PARTNER),
    ("partner", Category.INVESTOR_PARTNER),
    ("suspicious", Category.AHSOKA_SPECIAL_MISSION),
    ("ahsoka", Category.AHSOKA_SPECIAL_MISSION),
    ("artifact", Category.AHSOKA_SPECIAL_MISSION),
    ("relic", Category.AHSOKA_SPECIAL_MISSION),
    ("jedi", "artifact", Category.AHSOKA_SPECIAL_MISSION),
    ("jedi", Category.JEDI_TRAINING_DIPLOMACY),
    ("lightsaber", Category.JEDI_TRAINING_DIPLOMACY),
    ("diplomacy", Category.JEDI_TRAINING_DIPLOMACY),
    ("mediation", Category.JEDI_TRAINING_DIPLOMACY),
    ("mediat", Category.JEDI_TRAINING_DIPLOMACY),
    ("recruit", Category.RECRUITMENT),
    ("enlist", Category.RECRUITMENT),
    ("join", "rebellion", Category.RECRUITMENT),
    ("join", "rebel", Category.RECRUITMENT),
    ("pilot", "join", Category.RECRUITMENT),
    ("protect", Category.SPECIAL_PROTECTION),
    ("protection", Category.SPECIAL_PROTECTION),
    ("asset", Category.SPECIAL_PROTECTION),
    ("field", "support", Category.FIELD_OPERATIONS),
    ("field", "operation", Category.FIELD_OPERATIONS),
    ("field", Category.FIELD_OPERATIONS),
    ("backup", Category.FIELD_OPERATIONS),
    ("patrol", Category.FIELD_OPERATIONS),
    ("repair", Category.FIELD_OPERATIONS),
    ("logistics", Category.LOGISTICS),
    ("logistic", Category.LOGISTICS),
    ("fuel", Category.LOGISTICS),
    ("transport", Category.LOGISTICS),
    ("cargo", Category.LOGISTICS),
    ("supply", Category.LOGISTICS),
    ("delivery", Category.LOGISTICS),
    ("medical", "supplies", Category.LOGISTICS),
    ("stormtrooper", Category.URGENT_SECURITY),
    ("alert", "command", Category.URGENT_SECURITY),
    ("urgent", Category.URGENT_SECURITY),
    ("threat", Category.URGENT_SECURITY),
    ("danger", Category.URGENT_SECURITY),
    ("immediate", Category.URGENT_SECURITY),
    ("status", "request", Category.DATA_SUPPORT),
    ("status", "aid", Category.DATA_SUPPORT),
    ("data", Category.DATA_SUPPORT),
    ("analysis", Category.DATA_SUPPORT),
    ("coordinate", Category.DATA_SUPPORT),
    ("intel", Category.DATA_SUPPORT),
    ("beep", Category.DATA_SUPPORT),
    ("supplies", Category.SOLDIER_SUPPORT),
    ("soldier", Category.SOLDIER_SUPPORT),
    ("trooper", Category.SOLDIER_SUPPORT),
    ("medical", Category.SOLDIER_SUPPORT),
    ("aid", Category.SOLDIER_SUPPORT),
    ("support", Category.SOLDIER_SUPPORT),
    ("population", Category.POPULATION_TRAINING),
    ("civilian", Category.POPULATION_TRAINING),
    ("village", Category.POPULATION_TRAINING),
    ("train", Category.POPULATION_TRAINING),
    ("education", Category.POPULATION_TRAINING),
    ("teach", Category.POPULATION_TRAINING),
    ("learn", Category.POPULATION_TRAINING),
    ("planet", Category.PLANET_HELP),
    ("invasion", Category.PLANET_HELP),
    ("help", Category.PLANET_HELP),
    ("crisis", Category.PLANET_HELP),
    ("defense", Category.PLANET_HELP),
    ("security", Category.URGENT_SECURITY),
]

JEDI_CASE_MAP = {
    "train": JediCaseType.TRAINING,
    "diplomacy": JediCaseType.DIPLOMACY,
    "mediation": JediCaseType.MEDIATION,
    "mediat": JediCaseType.MEDIATION,
    "strategy": JediCaseType.STRATEGY,
    "mentor": JediCaseType.MENTORSHIP,
    "force": JediCaseType.FORCE_SENSITIVE,
    "sense": JediCaseType.FORCE_SENSITIVE,
    "ethics": JediCaseType.ETHICS,
    "artifact": JediCaseType.SPECIAL_MISSION,
    "relic": JediCaseType.SPECIAL_MISSION,
}


class C3POClassifierAgent(Agent):
    @property
    def name(self) -> str:
        return "C3POClassifierAgent"

    def process(self, message: Message) -> Message:
        combined = (message.sender + " " + message.content).lower()

        for i, rule in enumerate(CATEGORY_RULES):
            if len(rule) == 2:
                keyword, category = rule
                if any_word_starts_with(combined, keyword):
                    message.category = category
                    logger.debug("Rule %d matched: single '%s' -> %s", i, keyword, category.value)
                    break
            elif len(rule) == 3:
                kw1, kw2, category = rule
                if any_word_starts_with(combined, kw1) and \
                   any_word_starts_with(combined, kw2):
                    message.category = category
                    logger.debug("Rule %d matched: pair '%s'+'%s' -> %s", i, kw1, kw2, category.value)
                    break

        if message.category is None:
            message.category = Category.OTHER

        cat_val = message.category.value
        message.summary = message.content[:150]
        message.requires_leia = CATEGORY_REQUIRES_LEIA.get(cat_val, False)
        message.requires_jedi = CATEGORY_REQUIRES_JEDI.get(cat_val, False)
        message.suggested_next_action = CATEGORY_NEXT_ACTION.get(cat_val, "")

        if message.requires_jedi:
            for keyword, case_type in JEDI_CASE_MAP.items():
                if any_word_starts_with(combined, keyword):
                    message.jedi_case_type = case_type.value
                    break
            else:
                message.jedi_case_type = JediCaseType.NONE.value

        message.trace.append({
            "agent": self.name, "action": "classified",
            "details": {
                "category": cat_val, "priority": message.priority,
                "requires_leia": message.requires_leia,
                "requires_jedi": message.requires_jedi,
                "jedi_case_type": message.jedi_case_type,
            },
        })
        logger.debug(
            "Classified %s as %s (leia=%s, jedi=%s, action=%s)",
            message.sender, cat_val,
            message.requires_leia, message.requires_jedi,
            message.suggested_next_action[:50],
        )
        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message
