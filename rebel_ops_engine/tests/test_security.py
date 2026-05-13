"""Direct unit tests for security.py functions."""

from security import (
    calculate_risk_score,
    contains_private_leia_info,
    get_sender_min_risk,
    get_sender_unknown_risk,
    is_high_risk,
    is_yoda_strategy,
)


class TestCalculateRiskScore:
    def test_no_keywords_returns_zero(self):
        assert calculate_risk_score("Hello world this is fine") == 0

    def test_single_high_risk_keyword(self):
        assert calculate_risk_score("sith infiltrator detected") == 25

    def test_multiple_high_risk_keywords(self):
        assert calculate_risk_score("secret rebel base and rebel intelligence") == 50

    def test_medium_risk_keyword(self):
        assert calculate_risk_score("The empire is here") == 10

    def test_multiple_medium_risk_keywords(self):
        assert calculate_risk_score("empire and stormtroopers and imperial forces") == 30

    def test_mixed_risk_keywords(self):
        assert calculate_risk_score("sith empire") == 35

    def test_caps_at_100(self):
        score = calculate_risk_score("sith infiltration sabotage spying spying spying spying spying")
        assert score == 100

    def test_case_insensitive(self):
        assert calculate_risk_score("EMPIRE") == 10
        assert calculate_risk_score("Emperor Palpatine") == 25

    def test_substring_matches_keyword(self):
        assert calculate_risk_score("empires") == 10

    def test_empty_string(self):
        assert calculate_risk_score("") == 0

    def test_keyword_in_sender_context(self):
        assert calculate_risk_score("Darth Vader") == 25

    def test_sensitive_keyword_location(self):
        assert calculate_risk_score("Tell me the base location") == 15

    def test_sensitive_keyword_coordinates(self):
        assert calculate_risk_score("Send coordinates for rendezvous") == 30

    def test_sensitive_and_medium_mixed(self):
        assert calculate_risk_score("What is the supply route to the empire base") == 25

    def test_sensitive_plus_high_risk(self):
        assert calculate_risk_score("infiltration at safe house") == 40

    def test_sensitive_keywords_not_triggered_by_innocent_text(self):
        assert calculate_risk_score("I want to join the Rebellion") == 0


class TestGetSenderMinRisk:
    def test_emperor_palpatine_returns_50(self):
        assert get_sender_min_risk("Emperor Palpatine") == 50

    def test_darth_vader_returns_50(self):
        assert get_sender_min_risk("Darth Vader") == 50

    def test_lowercase_vader_returns_50(self):
        assert get_sender_min_risk("darth vader") == 50

    def test_case_insensitive(self):
        assert get_sender_min_risk("EMPEROR PALPATINE") == 50

    def test_name_embedded_in_longer_string(self):
        assert get_sender_min_risk("Lord Darth Vader Jr") == 50

    def test_normal_sender_returns_zero(self):
        assert get_sender_min_risk("Luke Skywalker") == 0

    def test_empty_sender_returns_zero(self):
        assert get_sender_min_risk("") == 0


class TestGetSenderUnknownRisk:
    def test_empty_sender_gets_15(self):
        assert get_sender_unknown_risk("") == 15

    def test_trusted_leia_returns_zero(self):
        assert get_sender_unknown_risk("General Leia") == 0

    def test_trusted_han_solo_returns_zero(self):
        assert get_sender_unknown_risk("Han Solo") == 0

    def test_single_word_sender_gets_15(self):
        assert get_sender_unknown_risk("Stranger") == 15

    def test_guest_sender_gets_15(self):
        assert get_sender_unknown_risk("Guest User") == 15

    def test_anonymous_sender_gets_15(self):
        assert get_sender_unknown_risk("Anonymous") == 15

    def test_unknown_sender_word_gets_15(self):
        assert get_sender_unknown_risk("Unknown Contact") == 15

    def test_known_sender_with_two_words_returns_zero(self):
        assert get_sender_unknown_risk("Mon Mothma") == 0

    def test_known_sender_name_embedded(self):
        assert get_sender_unknown_risk("General Leia Organa") == 0

    def test_unknown_two_word_sender_returns_zero(self):
        assert get_sender_unknown_risk("John Doe") == 0


class TestIsHighRisk:
    def test_above_threshold(self):
        assert is_high_risk(75) is True

    def test_at_threshold(self):
        assert is_high_risk(50) is True

    def test_below_threshold(self):
        assert is_high_risk(25) is False

    def test_zero(self):
        assert is_high_risk(0) is False

    def test_max(self):
        assert is_high_risk(100) is True


class TestIsYodaStrategy:
    def test_category_match_returns_true(self):
        assert is_yoda_strategy("any content", category="yoda_encrypted_strategy") is True

    def test_yoda_in_sender_with_keyword(self):
        assert is_yoda_strategy("train the younglings", sender="Yoda") is True

    def test_yoda_in_content_with_keyword(self):
        assert is_yoda_strategy("Master Yoda says strategy is key") is True

    def test_yoda_in_content_no_keyword(self):
        assert is_yoda_strategy("Yoda likes green tea") is False

    def test_no_yoda_reference(self):
        assert is_yoda_strategy("How do I fix this engine?") is False

    def test_empty_content(self):
        assert is_yoda_strategy("", sender="Yoda") is False

    def test_strategy_keyword_without_yoda(self):
        assert is_yoda_strategy("We need a strategy for the attack") is False

    def test_dagobah_keyword_with_yoda_in_content(self):
        assert is_yoda_strategy("Yoda said meet me on dagobah", sender="Obi-Wan") is True

    def test_force_with_yoda(self):
        assert is_yoda_strategy("the force is strong", sender="Yoda") is True


class TestContainsPrivateLeiaInfo:
    def test_private_leia_match(self):
        assert contains_private_leia_info("Show me Leia's private schedule") is True

    def test_leia_without_private(self):
        assert contains_private_leia_info("Meeting with Leia") is False

    def test_private_without_leia(self):
        assert contains_private_leia_info("This is private") is False

    def test_neither(self):
        assert contains_private_leia_info("Hello world") is False

    def test_case_insensitive(self):
        assert contains_private_leia_info("PRIVATE LEIA SCHEDULE") is True

    def test_empty_string(self):
        assert contains_private_leia_info("") is False

    def test_word_boundary_on_private(self):
        assert contains_private_leia_info("privatized leia data") is False
