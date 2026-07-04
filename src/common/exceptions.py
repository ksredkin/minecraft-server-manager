class MSMError(Exception):
    pass


class ServerAlreadyRunningError(MSMError):
    pass


class ServerFolderDoesNotExistError(MSMError):
    pass


class InvalidServerConfigurationError(MSMError):
    pass


class ServerStopTimeoutError(MSMError):
    pass


class ServerNotRunningError(MSMError):
    pass


class ServerResponseTimeoutError(MSMError):
    pass


class SettingsFileNotFoundError(MSMError):
    pass


class PluginsError(MSMError):
    pass


class PluginsFolderDoesNotExistError(PluginsError):
    pass


class PluginJarNotFoundError(PluginsError):
    pass


class PluginVersionNotFoundError(PluginsError):
    pass


class ApiClientError(MSMError):
    pass


class ApiClientTimeoutError(ApiClientError):
    pass


class ApiClientConnectionError(ApiClientError):
    pass


class ApiClientProtocolError(ApiClientError):
    pass


class ApiClientNetworkError(ApiClientError):
    pass


class ApiClientHttpError(ApiClientError):
    pass


class ApiClientInvalidResponseError(ApiClientError):
    pass


class EulaError(MSMError):
    pass


class EulaFileNotFoundError(EulaError):
    pass


class EulaStatusNotFoundError(EulaError):
    pass
