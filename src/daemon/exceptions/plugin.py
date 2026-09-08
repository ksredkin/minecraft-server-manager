from src.daemon.exceptions.server import MSMDaemonError, NoDiskSpaceError


class PluginError(MSMDaemonError):
    pass


class PluginsFolderDoesNotExistError(PluginError):
    pass


class PluginNotFoundError(PluginError):
    pass


class PluginAlreadyExists(PluginError):
    pass


class PluginStorageFullError(NoDiskSpaceError):
    pass
