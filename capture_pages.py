"""Автоматически сохраняет РЕАЛЬНЫЕ PNG экранов Streamlit на Mac.

Перед использованием: pip install -r requirements-dev.txt
python -m playwright install chromium
python capture_pages.py
"""
from __future__ import annotations

from pathlib import Path
import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/'report'/'screenshots'
PAGES=[
    ('overview','01_obzor','Путешествие под контролем'),
    ('trip','02_marshrut','Маршрут и бронирования'),
    ('events','03_simuliator','Симулятор событий рейса'),
    ('planb','04_plan_b','План Б: сохранить поездку'),
    ('notifs','05_uvedomleniya','Уведомления и синхронизация'),
    ('api','06_api','API и логика интеграций'),
]

def find_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        return s.getsockname()[1]


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    port=find_port()
    base=f'http://127.0.0.1:{port}'
    env=os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS']='false'
    cmd=[sys.executable,'-m','streamlit','run',str(ROOT/'app.py'),
         '--server.headless=true','--server.address=127.0.0.1',
         f'--server.port={port}','--browser.gatherUsageStats=false']
    process=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError('Streamlit не запустился; проверь зависимости.')
            try:
                if urlopen(base+'/_stcore/health',timeout=1).status==200:
                    break
            except Exception:
                pass
            time.sleep(.5)
        else:raise TimeoutError('Не дождались запуска Streamlit')
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                for view,name,title in PAGES:
                    ctx=browser.new_context(viewport={'width':1650,'height':1050},device_scale_factor=1.3,locale='ru-RU',color_scheme='light')
                    pg=ctx.new_page()
                    pg.goto(f'{base}/?view={view}&capture=1',wait_until='domcontentloaded')
                    pg.get_by_text(title,exact=True).first.wait_for(timeout=45000)
                    pg.wait_for_timeout(1800)
                    out=OUTPUT/(name+'.png')
                    pg.screenshot(path=str(out),full_page=True,animations='disabled')
                    print('Сохранено:',out.relative_to(ROOT))
                    ctx.close()
            finally:
                browser.close()
        print('Готово. PNG находятся в report/screenshots/')
    finally:
        process.terminate()
        try:process.wait(timeout=6)
        except subprocess.TimeoutExpired:process.kill()

if __name__=='__main__':
    main()
