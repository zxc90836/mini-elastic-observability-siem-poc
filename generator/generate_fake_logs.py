import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
INTERVAL_SECONDS = float(os.getenv("INTERVAL_SECONDS", "5"))

MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))  # 5MB
BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "3"))

DATA_DIR.mkdir(parents=True, exist_ok=True)

services = ["order-service", "payment-service", "user-service", "inventory-service"]
endpoints = ["/api/orders", "/api/payments", "/api/users", "/api/login", "/api/inventory"]
hosts = ["vm-01", "vm-02", "vm-03"]
ips = ["203.0.113.10", "198.51.100.23", "192.0.2.55", "10.0.0.88"]
users = ["admin", "root", "test", "operator", "service_account"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_json_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = RotatingFileHandler(
        DATA_DIR / filename,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


app_logger = create_json_logger("app_log", "app.log")
system_logger = create_json_logger("system_metric", "system.log")
security_logger = create_json_logger("security_event", "security.log")


def write_event(logger: logging.Logger, event: dict) -> None:
    logger.info(json.dumps(event, ensure_ascii=False))


def generate_app_log() -> dict:
    status_code = random.choices(
        population=[200, 201, 400, 401, 404, 500, 502, 503],
        weights=[45, 10, 8, 6, 8, 10, 7, 6],
        k=1,
    )[0]

    return {
        "@timestamp": utc_now(),
        "source_type": "app_log",
        "service": random.choice(services),
        "endpoint": random.choice(endpoints),
        "status_code": status_code,
        "level": "ERROR" if status_code >= 500 else "WARN" if status_code >= 400 else "INFO",
        "response_time_ms": random.randint(30, 2200),
        "message": "Application error detected" if status_code >= 500 else "API request completed",
    }


def generate_system_metric() -> dict:
    cpu_usage = round(random.uniform(5, 96), 2)
    memory_usage = round(random.uniform(20, 92), 2)
    disk_usage = round(random.uniform(30, 98), 2)
    is_warning = cpu_usage >= 80 or memory_usage >= 85 or disk_usage >= 90

    return {
        "@timestamp": utc_now(),
        "source_type": "system_metric",
        "host_name": random.choice(hosts),
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "level": "WARN" if is_warning else "INFO",
        "message": "High resource usage detected" if is_warning else "System metric collected",
    }


def generate_security_event() -> dict:
    failed_count = random.randint(1, 25)
    risk_score = random.randint(10, 98)

    return {
        "@timestamp": utc_now(),
        "source_type": "security_event",
        "event_type": "failed_login",
        "src_ip": random.choice(ips),
        "username": random.choice(users),
        "failed_count": failed_count,
        "risk_score": risk_score,
        "level": "WARN" if failed_count >= 10 or risk_score >= 80 else "INFO",
        "message": "Multiple failed login attempts" if failed_count >= 10 else "Login failure observed",
    }


def main() -> None:
    print(
        f"Fake log generator started. DATA_DIR={DATA_DIR}, "
        f"interval={INTERVAL_SECONDS}s, maxBytes={MAX_BYTES}, backups={BACKUP_COUNT}",
        flush=True,
    )

    while True:
        app_event = generate_app_log()
        system_event = generate_system_metric()
        security_event = generate_security_event()

        write_event(app_logger, app_event)
        write_event(system_logger, system_event)
        write_event(security_logger, security_event)

        print(
            f"generated: app={app_event['status_code']}, "
            f"cpu={system_event['cpu_usage']}, "
            f"failed_login={security_event['failed_count']}",
            flush=True,
        )

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
