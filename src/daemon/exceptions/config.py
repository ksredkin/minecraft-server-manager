from src.daemon.exceptions.server import MSMDaemonError


class ConfigError(MSMDaemonError):
    pass


class InvalidConfigError(ConfigError):
    pass


class ConfigNotFoundError(ConfigError):
    pass
