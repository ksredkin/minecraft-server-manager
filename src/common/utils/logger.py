from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    LogRecord,
    StreamHandler,
    getLogger,
)


class ColorFormatter(Formatter):
    COLORS = {
        DEBUG: "\033[37m",
        INFO: "\033[32m",
        WARNING: "\033[33m",
        ERROR: "\033[31m",
        CRITICAL: "\033[41m",
    }

    RESET = "\033[0m"

    def format(self, record: LogRecord) -> str:
        original = record.levelname

        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{original}{self.RESET}"

        result = super().format(record)

        record.levelname = original
        return result


class Logger:
    def __init__(self, name: str) -> None:
        self._logger = getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        self._logger.setLevel(INFO)

        formatter = ColorFormatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream_handler = StreamHandler()

        stream_handler.setFormatter(formatter)

        if not self._logger.handlers:
            self._logger.addHandler(stream_handler)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def critical(self, message: str) -> None:
        self._logger.critical(message)
