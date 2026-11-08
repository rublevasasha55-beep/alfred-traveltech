"""Минимальное файловое хранилище только для локального демо.

Для production нужны транзакционное хранилище, блокировки и аудит.
Файл не содержит паспортных данных или платёжной информации.
"""
from pathlib import Path
from threading import Lock
import json
import os
import tempfile
from engine import initial_state

ROOT = Path(__file__).resolve().parent
STORE = ROOT / 'storage' / 'demo_state.json'
LOCK = Lock()


def load() -> dict:
    with LOCK:
        if not STORE.exists():
            return initial_state()
        try:
            return json.loads(STORE.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            return initial_state()


def save(state: dict) -> None:
    STORE.parent.mkdir(parents=True,exist_ok=True)
    with LOCK:
        fd, temp_path=tempfile.mkstemp(dir=str(STORE.parent),prefix='demo_',suffix='.json')
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                json.dump(state,f,ensure_ascii=False,indent=2)
            os.replace(temp_path,STORE)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def reset() -> dict:
    s=initial_state()
    save(s)
    return s
