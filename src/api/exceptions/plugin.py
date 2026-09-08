from src.api.exceptions.api import MSMAPIError


class PluginError(MSMAPIError):
    status_code = 500


class UnsupportedPluginProviderError(PluginError):
    status_code = 400


class PluginNotFoundError(PluginError):
    status_code = 404
