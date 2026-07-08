from src.api.exceptions.server import MSMError


class PluginsError(MSMError):
    pass


class PluginsFolderDoesNotExistError(PluginsError):
    pass


class PluginJarNotFoundError(PluginsError):
    pass


class PluginVersionNotFoundError(PluginsError):
    pass
