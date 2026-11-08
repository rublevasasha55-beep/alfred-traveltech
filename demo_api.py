"""Локальный демонстрационный API внешнего поставщика / оркестратора.

Запуск отдельно: uvicorn demo_api:app --reload --host 127.0.0.1 --port 8000
Документация: http://127.0.0.1:8000/docs
Никаких реальных авиабронирований и обращений к авиакомпаниям.
Не выставлять этот API в публичную сеть (нет production-аутентификации).
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from engine import receive_event, trip_impacts, alternatives, change_online, approve_alternative
from store import load, save, reset

app=FastAPI(title='Альфред — демонстрационное API',version='0.1.0',
            description='Локальный симулятор TravelTech событий. Все данные вымышлены.')

class FlightEvent(BaseModel):
    event_id: str = Field(...,min_length=1,max_length=100)
    flight_id: str = 'AF101'
    status: str
    delay_minutes: int = Field(default=0,ge=0,le=1440)
    observed_at: str
    source: str = 'mock_provider'

class Connectivity(BaseModel):
    online: bool

class Approval(BaseModel):
    alternative_id: str
    confirmed_by_user: bool

@app.get('/health')
def health():
    return {'ok':True,'mode':'demo','real_supplier_connected':False}

@app.get('/api/trips/demo')
def get_trip():
    s=load()
    return {'trip':s,'impacts':trip_impacts(s),'alternatives':alternatives(s)}

@app.get('/api/flights/AF101')
def get_flight():
    s=load()
    return {'flight_id':'AF101','status':s['current_status'],
            'delay_minutes':s['delay_minutes'],
            'observed_at':s['flight_data_updated_at'],
            'source':'demo feed', 'is_real':False}

@app.post('/api/events')
def ingest_event(payload: FlightEvent):
    s=load()
    result=receive_event(s,payload.model_dump() if hasattr(payload,'model_dump') else payload.dict())
    if result['outcome']=='invalid':
        raise HTTPException(status_code=422,detail=result['message'])
    save(s)
    return result

@app.get('/api/trips/demo/alternatives')
def get_alternatives():
    return {'alternatives':alternatives(load())}

@app.post('/api/trips/demo/approve')
def approve(payload: Approval):
    if not payload.confirmed_by_user:
        raise HTTPException(status_code=400,detail='Требуется явное подтверждение пользователя')
    s=load()
    result=approve_alternative(s,payload.alternative_id)
    if not result['ok']:
        raise HTTPException(status_code=409,detail=result['message'])
    save(s)
    return result

@app.post('/api/connectivity')
def set_connectivity(payload: Connectivity):
    s=load()
    n=change_online(s,payload.online)
    save(s)
    return {'online':s['online'],'delivered_from_queue':n}

@app.post('/api/demo/reset')
def reset_demo():
    s=reset()
    return {'ok':True,'revision':s['revision']}
