"""
DarkSideSecurityAgent — Security Scanner

Analyzes incoming requests for Dark Side threats.
Returns structured security assessment.

Prompt (documentation):
    You are the Rebel Command Security Officer.
    Classify as HIGH risk if the message:
    - asks for secret Rebel base locations
    - asks for General Leia's private schedule
    - requests confidential Rebel intelligence
    - mentions Darth Vader, Emperor Palpatine, Sith activity
    - mentions stormtroopers in a suspicious/threatening way
    - mentions Imperial surveillance, sabotage, spying, infiltration
    - includes suspicious links or attachments
    - pressures for immediate restricted access
    - asks to bypass security checks
    - appears to impersonate a Rebel ally
"""

import logging

from agents.base import Agent
from models import Message, MessageStatus, SecurityRisk
from security import (
    HIGH_RISK_KEYWORDS,
    MEDIUM_RISK_KEYWORDS,
    SENSITIVE_KEYWORDS,
    calculate_risk_score,
    get_sender_min_risk,
    get_sender_unknown_risk,
    is_high_risk,
)

logger = logging.getLogger(__name__)


class DarkSideSecurityAgent(Agent):
    @property
    def name(self) -> str:
        return "DarkSideSecurityAgent"

    def process(self, message: Message) -> Message:
        combined = (message.sender + " " + message.content).lower()
        score = calculate_risk_score(combined, message.sender)
        sender_score = get_sender_min_risk(message.sender)
        sender_unknown = get_sender_unknown_risk(message.sender)
        score = max(score, sender_score)
        score = max(score, sender_unknown)
        message.risk_score = score

        indicators = []
        for kw in HIGH_RISK_KEYWORDS:
            if kw in combined:
                indicators.append(kw)
        for kw in MEDIUM_RISK_KEYWORDS:
            if kw in combined:
                indicators.append(kw)
        for kw in SENSITIVE_KEYWORDS:
            if kw in combined:
                indicators.append(kw)
        message.dark_side_indicators = indicators

        if is_high_risk(score):
            message.security_risk = SecurityRisk.HIGH.value
            message.trusted_request = False
            message.status = MessageStatus.QUARANTINED
            message.error = (
                f"High-risk content detected (score: {score}). "
                f"Indicators: {', '.join(indicators)}. "
                f"Message quarantined by DarkSideSecurityAgent."
            )
            message.trace.append({
                "agent": self.name, "action": "quarantined",
                "details": {"risk_score": score, "indicators": indicators},
            })
            logger.warning(
                "Quarantined message from %s (score: %d, indicators: %s)",
                message.sender, score, indicators,
            )
        elif score >= 25:
            message.security_risk = SecurityRisk.MEDIUM.value
            message.status = MessageStatus.SECURITY_REVIEW
            message.trace.append({
                "agent": self.name, "action": "flagged",
                "details": {"risk_score": score, "indicators": indicators},
            })
            logger.info(
                "Medium-risk message from %s (score: %d)",
                message.sender, score,
            )
        elif score >= 15:
            message.security_risk = SecurityRisk.LOW.value
            message.status = MessageStatus.FLAGGED
            message.trace.append({
                "agent": self.name, "action": "flagged",
                "details": {"risk_score": score, "indicators": indicators},
            })
            logger.info(
                "Flagged message from %s (score: %d)",
                message.sender, score,
            )
        else:
            message.security_risk = SecurityRisk.LOW.value
            message.trace.append({
                "agent": self.name, "action": "cleared",
                "details": {"risk_score": 0, "indicators": []},
            })

        if self.name not in message.processed_by:
            message.processed_by.append(self.name)
        return message
