from src.common.core.config import SERVER_PATH, JAVA, JAVA_ARGS, JAR_NAME, JAR_ARGS
import subprocess

class ProcessService:
    def __init__(self):
        self._process = None
        self._status = None
    
    def start(self) -> bool:
        if not self._process or self._process.poll() is not None:
            if not SERVER_PATH:
                raise ValueError("В конфиге не установлен путь к серверу.")
            
            if not JAVA:
                raise ValueError("В конфиге не указана java.")
            
            if not JAR_NAME:
                raise ValueError("В конфиге не указано имя jar файла.")
            
            start_command = [JAVA, *JAVA_ARGS, "-jar", JAR_NAME, *JAR_ARGS]
            self._process = subprocess.Popen(start_command, cwd=SERVER_PATH, stdin=subprocess.PIPE, text=True)
            
            return True
        return False

    def stop(self) -> bool:
        if not self._process or self._process.poll() is not None:
            return False
        
        self._process.stdin.write("stop\n")
        self._process.stdin.flush()
        return True

    def restart(self) -> bool:
        self.stop()
        self.start()
        return True

    def status(self) -> str:
        if self._process is None:
            return "stopped"

        if self._process.poll() is None:
            return "running"

        return "stopped"
    
    def execute_command(self, command: str) -> bool:
        if not self._process or self._process.poll() is not None:
            return False
        
        self._process.stdin.write(command + "\n")
        self._process.stdin.flush()

        return True
