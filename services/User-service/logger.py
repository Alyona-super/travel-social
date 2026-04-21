import logging
import sys
import json
from datetime import datetime


#  Форматирование логов в JSON
class JSONFormatter(logging.Formatter):

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Добавляем исключение, если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


# логирование для сервиса
def setup_logging(service_name: str, log_level: str = "INFO"):

    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level))

    # вывод в консоль в формате JSON
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    return logger
