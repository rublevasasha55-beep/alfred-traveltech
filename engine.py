"""Детерминированные правила TravelTech-кейса. Только демонстрационные данные.

Время хранится как ISO 8601 с часовым поясом; сравнения — в UTC.
Паспортные данные НЕ собираются и НЕ хранятся.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from copy import deepcopy
from typing import Any

UTC = timezone.utc
MIN_CONNECTION_MIN = 90
FLIGHT_DATA_TTL_MIN = 30


def dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('Время должно содержать часовой пояс (например, +03:00 или Z)')
    return parsed.astimezone(UTC)


def iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec='seconds')


def initial_state() -> dict[str, Any]:
    now = iso_now()
    return {
        'trip_id': 'TRIP-DEMO-01', 'revision': 1, 'online': True,
        'flight_data_updated_at': now, 'processed_event_ids': [],
        'events': [], 'notifications': [], 'last_payload': None,
        'current_status': 'on_time', 'delay_minutes': 0,
        'selected_plan': None, 'transfer_status': 'confirmed',
        'travellers': [
            {'name':'Участник 1','checked_bag_kg':23,'schengen_visa':'verified','transit_visa':'unverified'},
            {'name':'Участник 2','checked_bag_kg':23,'schengen_visa':'verified','transit_visa':'unverified'},
            {'name':'Участник 3','checked_bag_kg':23,'schengen_visa':'verified','transit_visa':'unverified'},
        ],
        'flights': [
            {'id':'AF101', 'from':'Москва · SVO','to':'Стамбул · IST',
             'origin':'SVO', 'destination':'IST',
             'depart':'2026-11-20T09:00:00+03:00','arrive':'2026-11-20T13:00:00+03:00',
             'status':'on_time'},
            {'id':'AF202','from':'Стамбул · IST','to':'Рим · FCO',
             'origin':'IST','destination':'FCO',
             'depart':'2026-11-20T15:20:00+03:00','arrive':'2026-11-20T17:20:00+01:00',
             'status':'on_time'},
        ],
        'transfer': {'name':'Трансфер из FCO', 'pickup':'2026-11-20T18:20:00+01:00'},
        'hotel': {'name':'Отель в Риме', 'checkin':'2026-11-20T20:00:00+01:00'},
        'activity': {'name':'Экскурсия по Риму','start':'2026-11-21T09:30:00+01:00'},
        'last_approved_at': None,
    }


ALTERNATIVES = [
    # Варианты после риска пересадки: заменяют сегмент IST→FCO.
    {'id':'ALT-IST-1','flight':'AZ701','origin':'IST','destination':'FCO',
     'depart':'2026-11-20T19:20:00+03:00','arrive':'2026-11-20T20:50:00+01:00',
     'bag_kg':23,'transit':'none','price_eur':165,'note':'Прямой рейс, багаж включён'},
    {'id':'ALT-IST-2','flight':'AZ702','origin':'IST','destination':'FCO',
     'depart':'2026-11-20T18:10:00+03:00','arrive':'2026-11-20T19:40:00+01:00',
     'bag_kg':0,'transit':'none','price_eur':99,'note':'Без регистрируемого багажа'},
    {'id':'ALT-IST-3','flight':'AZ703','origin':'IST','destination':'FCO',
     'depart':'2026-11-20T20:30:00+03:00','arrive':'2026-11-20T22:00:00+01:00',
     'bag_kg':30,'transit':'none','price_eur':190,'note':'Поздний прилёт, возможен поздний заезд'},
    {'id':'ALT-IST-4','flight':'AZ704','origin':'IST','destination':'FCO',
     'depart':'2026-11-20T16:05:00+03:00','arrive':'2026-11-20T17:35:00+01:00',
     'bag_kg':23,'transit':'none','price_eur':220,'note':'Недостаточно времени на пересадку'},
    {'id':'ALT-IST-5','flight':'AZ705','origin':'IST','destination':'FCO',
     'depart':'2026-11-20T18:50:00+03:00','arrive':'2026-11-20T23:50:00+01:00',
     'bag_kg':23,'transit':'UK','price_eur':145,'note':'Транзит через третью страну, визы не проверены'},
    # При отмене первого сегмента выбираем альтернативный путь из Москвы.
    {'id':'ALT-SVO-1','flight':'AZ801','origin':'SVO','destination':'FCO',
     'depart':'2026-11-20T12:15:00+03:00','arrive':'2026-11-20T15:10:00+01:00',
     'bag_kg':23,'transit':'none','price_eur':280,'note':'Прямой рейс в Рим'},
    {'id':'ALT-SVO-2','flight':'AZ802','origin':'SVO','destination':'FCO',
     'depart':'2026-11-20T14:00:00+03:00','arrive':'2026-11-20T18:40:00+01:00',
     'bag_kg':30,'transit':'none','price_eur':240,'note':'Позднее прибытие'},
    {'id':'ALT-SVO-3','flight':'AZ803','origin':'SVO','destination':'FCO',
     'depart':'2026-11-20T10:40:00+03:00','arrive':'2026-11-20T15:50:00+01:00',
     'bag_kg':23,'transit':'UK','price_eur':200,'note':'Транзит, требующий проверки документов'},
]


def connection_minutes(state: dict) -> int:
    first, second = state['flights'][:2]
    arrival = dt(first['arrive']) + timedelta(minutes=state['delay_minutes'])
    return round((dt(second['depart']) - arrival).total_seconds() / 60)


def trip_impacts(state: dict) -> list[dict]:
    problems = []
    if state['current_status'] == 'cancelled':
        problems += [
            {'severity':'critical', 'title':'Первый рейс отменён', 'details':'Исходный маршрут невозможно выполнить'},
            {'severity':'critical','title':'Пересадка и второй рейс под угрозой','details':'Нужно перестроить авиамаршрут целиком'},
            {'severity':'warning','title':'Трансфер и заселение','details':'Время прибытия требует пересогласования'},
        ]
    elif state['current_status'] == 'delayed':
        minutes = connection_minutes(state)
        if minutes < MIN_CONNECTION_MIN:
            problems.append({'severity':'critical', 'title':'Не хватает времени на пересадку',
                             'details':f'Остаётся {minutes} мин вместо минимальных {MIN_CONNECTION_MIN} мин'})
            problems.append({'severity':'warning', 'title':'Трансфер может потребовать изменения',
                             'details':'Время встречи связано с исходным прибытием в Рим'})
        else:
            problems.append({'severity':'warning', 'title':'Первый рейс задержан',
                             'details':f'На пересадку остаётся {minutes} мин (минимум {MIN_CONNECTION_MIN} мин)'})
    if state.get('selected_plan'):
        # После подтверждения показываем только вопросы, которые остались открытыми.
        problems = [p for p in problems if p['title'] != 'Трансфер может потребовать изменения']
    return problems


def itinerary_risk(state: dict) -> bool:
    return state['current_status'] == 'cancelled' or (
        state['current_status'] == 'delayed' and connection_minutes(state) < MIN_CONNECTION_MIN
    )


def alternatives(state: dict) -> list[dict]:
    if not itinerary_risk(state):
        return []
    origin = 'SVO' if state['current_status'] == 'cancelled' else 'IST'
    first_arrival = dt(state['flights'][0]['arrive']) + timedelta(minutes=state['delay_minutes'])
    required_bag = max(t['checked_bag_kg'] for t in state['travellers'])
    results = []
    for candidate in ALTERNATIVES:
        if candidate['origin'] != origin:
            continue
        c = deepcopy(candidate)
        reasons = []
        if c['bag_kg'] < required_bag:
            reasons.append(f'Багаж: требуется {required_bag} кг, доступно {c["bag_kg"]} кг')
        if c['transit'] != 'none':
            reasons.append('Транзитные визы/документы не подтверждены')
        if any(t['schengen_visa'] != 'verified' for t in state['travellers']):
            reasons.append('Не подтверждены въездные документы всех участников')
        if origin == 'IST':
            mins = int((dt(c['depart'])-first_arrival).total_seconds()//60)
            c['connection_min'] = mins
            if mins < MIN_CONNECTION_MIN:
                reasons.append(f'Пересадка {mins} мин — меньше {MIN_CONNECTION_MIN} мин')
        c['allowed'] = len(reasons)==0
        c['reasons'] = reasons
        c['local_arrival'] = datetime.fromisoformat(c['arrive']).strftime('%d.%m %H:%M')
        c['local_departure'] = datetime.fromisoformat(c['depart']).strftime('%d.%m %H:%M')
        results.append(c)
    return sorted(results, key=lambda x: (not x['allowed'], dt(x['arrive']), x['price_eur']))


def push_notice(state: dict, title: str, text: str, *, kind: str='notice') -> None:
    state['notifications'].insert(0, {
        'id': f'N-{len(state["notifications"])+1:03d}', 'created_at':iso_now(),
        'title':title,'text':text,'kind':kind,
        'delivery':'delivered' if state['online'] else 'queued',
    })


def receive_event(state: dict, event: dict) -> dict:
    """Обработчик события поставщика; не меняет брони автоматически."""
    event_id = str(event.get('event_id', '')).strip()
    if not event_id or len(event_id)>100:
        return {'outcome':'invalid', 'message':'Некорректный event_id'}
    if event_id in state['processed_event_ids']:
        return {'outcome':'duplicate','message':'Повтор события проигнорирован (event_id уже обработан)'}
    flight_id = str(event.get('flight_id',''))
    if flight_id != 'AF101':
        return {'outcome':'invalid','message':'В демо отслеживается рейс AF101'}
    status = str(event.get('status',''))
    if status not in ('delayed','cancelled','on_time'):
        return {'outcome':'invalid','message':'Неизвестный статус'}
    try:
        recorded = dt(str(event['observed_at']))
    except (KeyError, ValueError, TypeError):
        return {'outcome':'invalid','message':'Требуется observed_at с часовым поясом'}
    try:
        delay = int(event.get('delay_minutes',0))
    except (ValueError,TypeError):
        return {'outcome':'invalid','message':'Некорректная длительность задержки'}
    if delay < 0 or delay > 1440:
        return {'outcome':'invalid','message':'Задержка должна быть от 0 до 1440 минут'}
    if status != 'delayed':
        delay=0
    state['processed_event_ids'].append(event_id)
    if recorded <= dt(state['flight_data_updated_at']):
        state['events'].insert(0, {'event_id':event_id,'observed_at':recorded.isoformat(),
                                    'status':status,'outcome':'stale',
                                    'message':'Устаревшее событие — состояние поездки не изменено'})
        return {'outcome':'stale','message':'Устаревшее событие не заменило более свежие данные'}
    # Имитация задержки/отмены поставщика, исходный план сохраняется до подтверждения.
    state['current_status'] = status
    state['delay_minutes'] = delay
    state['flight_data_updated_at'] = recorded.isoformat()
    state['selected_plan'] = None
    state['last_payload'] = deepcopy(event)
    state['events'].insert(0, {'event_id':event_id,'observed_at':recorded.isoformat(),
                                'status':status,'outcome':'accepted',
                                'message':f'Событие принято: {status}'})
    if itinerary_risk(state):
        push_notice(state, 'Пересадка под угрозой' if status=='delayed' else 'Рейс отменён',
                    'Подготовлены варианты перестроения поездки. Для изменения брони потребуется согласие.',kind='critical')
    elif status=='delayed':
        push_notice(state, 'Задержка рейса',
                    f'На пересадку остаётся {connection_minutes(state)} мин, проверьте свежесть статуса.',kind='warning')
    else:
        push_notice(state,'Статус рейса обновлён','По последним данным рейс выполняется по расписанию.',kind='notice')
    return {'outcome':'accepted','message':'Событие обработано; пользовательский план не перебронирован',
            'risk':itinerary_risk(state)}


def approve_alternative(state: dict, alternative_id: str) -> dict:
    candidate=next((c for c in alternatives(state) if c['id']==alternative_id),None)
    if candidate is None:
        return {'ok':False,'message':'Вариант больше не актуален'}
    if not candidate['allowed']:
        return {'ok':False,'message':'Вариант не соответствует ограничениям поездки'}
    if not state['online']:
        return {'ok':False,'message':'Офлайн: сохранить выбор можно после подключения; перебронирование не выполнено'}
    state['selected_plan']=candidate['id']
    state['revision']+=1
    state['last_approved_at']=iso_now()
    # Обновляем локальную версию маршрута/встречи, НЕ создаём бронирование у поставщика.
    state['planned_arrival']=candidate['arrive']
    state['proposed_transfer_pickup']=(dt(candidate['arrive'])+timedelta(minutes=60)).isoformat()
    state['transfer_status']='reschedule_required'
    state['events'].insert(0,{'event_id':f'approval-{state["revision"]}',
                               'observed_at':iso_now(),'status':'plan_approved',
                               'outcome':'accepted','message':f'Вариант {candidate["flight"]} согласован как черновик плана'})
    push_notice(state,'План поездки обновлён',
                f'Добавлен предложенный рейс {candidate["flight"]}; покупка и изменение трансфера не выполнялись.',kind='notice')
    return {'ok':True,'message':'Новый вариант сохранён в общем черновике; бронирования не изменялись'}


def change_online(state: dict, online: bool) -> int:
    state['online']=bool(online)
    delivered=0
    if online:
        for n in state['notifications']:
            if n['delivery']=='queued':
                n['delivery']='delivered'
                delivered+=1
    return delivered


def freshness(state: dict, now: datetime|None=None) -> tuple[bool,int]:
    now=now or datetime.now(UTC)
    age=max(0,int((now-dt(state['flight_data_updated_at'])).total_seconds()//60))
    return age <= FLIGHT_DATA_TTL_MIN, age
