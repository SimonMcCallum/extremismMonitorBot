"""
Tests for configuration module.
"""
import pytest
from config import Settings


def test_settings_defaults():
    """Test that settings have appropriate defaults."""
    settings = Settings(
        discord_bot_token="test_token",
        discord_client_id="test_client_id",
        database_url="postgresql://test:test@localhost/test",
        anthropic_api_key="test_key",
        secret_key="test_secret"
    )

    assert settings.app_name == "Extremism Monitor Bot"
    assert settings.environment == "development"
    assert settings.risk_low_threshold == 30
    assert settings.risk_medium_threshold == 60
    assert settings.risk_high_threshold == 85
    assert settings.enable_risk_monitoring is True


def test_settings_custom_values():
    """Test that custom settings override defaults."""
    settings = Settings(
        discord_bot_token="test_token",
        discord_client_id="test_client_id",
        database_url="postgresql://test:test@localhost/test",
        anthropic_api_key="test_key",
        secret_key="test_secret",
        risk_low_threshold=40,
        enable_risk_monitoring=False
    )

    assert settings.risk_low_threshold == 40
    assert settings.enable_risk_monitoring is False


def test_required_settings():
    """Test that required settings are enforced."""
    with pytest.raises(Exception):
        # Missing required fields should raise an error
        Settings()
