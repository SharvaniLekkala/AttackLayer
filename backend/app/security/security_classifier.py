"""Security classifier — delegates to unified attack registry."""

from app.security.attack_registry import classify_security, assess_all_attacks, SEVEN_ATTACKS

__all__ = ["classify_security", "assess_all_attacks", "SEVEN_ATTACKS"]
