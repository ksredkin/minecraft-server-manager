from src.daemon.exceptions.server import MSMDaemonError


class PluginError(MSMDaemonError):
    pass


class PluginsFolderDoesNotExistError(PluginError):
    pass


class PluginNotFoundError(PluginError):
    pass
