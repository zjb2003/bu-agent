class BUAgentError(Exception):
    """Base application error."""


class SkillConfigurationError(BUAgentError):
    """Skill installation is missing or unsafe."""


class ProviderCompatibilityError(BUAgentError):
    """Configured provider API mode is not supported."""

