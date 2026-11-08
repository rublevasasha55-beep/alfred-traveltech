"""Альфред — интерактивный прототип системного аналитика для TravelTech.

Запуск: python -m streamlit run app.py
Все данные вымышлены. Прототип не связан с авиакомпаниями и не бронирует билеты.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from uuid import uuid4
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import (initial_state, connection_minutes, trip_impacts,
                    itinerary_risk, alternatives, receive_event,
                    approve_alternative, change_online, freshness, dt, iso_now)
from store import load, save, reset
from ui import apply_style, sidebar, shell, kpi, section, note, insight, icon, h, INK, YELLOW, GREEN, RED, SUB

st.set_page_config(page_title="Альфред — путешествие под контролем",
                   page_icon="✈️", layout="wide", initial_sidebar_state="expanded")
apply_style()

PAGES = [
    ('overview','Обзор поездки','home'),
    ('trip','Маршрут','route'),
    ('events','Симулятор рейса','pulse'),
    ('planb','План Б','plane'),
    ('notifs','Уведомления','bell'),
    ('api','API и архитектура','code'),
]
page=st.query_params.get('view','overview')
if page not in [p[0] for p in PAGES]:
    page='overview'
sidebar(page,PAGES)
state=load()


def change_and_rerun(action, *args):
    result=action(state,*args)
    save(state)
    if isinstance(result, dict):
        st.session_state['last_result']=result
    st.rerun()


def time_local(text):
    obj=datetime.fromisoformat(text.replace('Z','+00:00'))
    return obj.strftime('%d.%m, %H:%M')


def risk_badge():
    if state.get('selected_plan'):
        return 'Новый план согласован'
    if state['current_status']=='cancelled':
        return 'Рейс отменён'
    if itinerary_risk(state):
        return 'Пересадка под угрозой'
    if state['current_status']=='delayed':
        return 'Задержка рейса'
    return 'Без критичных сбоев'


def event_payload(status: str, delay: int=0) -> dict:
    # +1 сек помогает гарантировать новизну по сравнению с предыдущей записью.
    recorded=max(datetime.now(timezone.utc),dt(state['flight_data_updated_at']))+timedelta(seconds=1)
    return {'event_id':f'DEMO-{uuid4().hex[:9]}','flight_id':'AF101',
            'status':status,'delay_minutes':delay,'observed_at':recorded.isoformat(),
            'source':'mock_provider'}


def event_action(status: str, delay: int=0):
    res=receive_event(state,event_payload(status,delay))
    save(state)
    st.session_state['last_result']=res
    st.rerun()


def flight_row(flight, status, subline=''):
    if status=='cancelled':
        status_html='<span class="status-pill critical">Отменён</span>'
    elif status=='delayed':
        status_html='<span class="status-pill">Задержан</span>'
    else:
        status_html='<span class="status-pill ok">По плану</span>'
    st.markdown('<div class="flight-line"><span class="flight-icon">'+icon('plane',20,INK)+'</span>'+
                f'<div class="flight-text"><b>{h(flight["id"])} · {h(flight["from"])} → {h(flight["to"])}</b>'+
                f'<small>{h(time_local(flight["depart"]))} → {h(time_local(flight["arrive"]))} (местное время)'+
                (f' · {h(subline)}' if subline else '')+'</small></div>'+status_html+'</div>',
                unsafe_allow_html=True)


def render_impacts():
    items=trip_impacts(state)
    if not items:
        insight('План без критичных конфликтов',
                'По имеющимся демо-данным время пересадки достаточно. Но статус рейса следует обновлять по актуальному источнику.')
        return
    for item in items:
        hue=RED if item['severity']=='critical' else '#E5A72B'
        st.markdown(f'<div class="incident-line"><span class="incicon" style="background:{h(hue)}18">'+
                    icon('alert' if item['severity']=='critical' else 'clock',21,hue)+'</span>'+
                    f'<span class="incbody"><b>{h(item["title"])}</b><small>{h(item["details"])}</small></span></div>',
                    unsafe_allow_html=True)


def alternatives_table():
    result=alternatives(state)
    if not result:
        st.info('Сейчас критичного сбоя маршрута нет. Создай задержку +120 минут или отмену в разделе «Симулятор рейса».')
        return
    suitable=sum(x['allowed'] for x in result)
    st.caption(f'Показано {len(result)} демонстрационных вариантов. Из них соответствуют проверяемым ограничениям: {suitable}.')
    for item in result:
        with st.container(border=True):
            left,right=st.columns([5,1.3])
            with left:
                st.markdown(f'**{item["flight"]} · {item["origin"]} → {item["destination"]}**')
                st.caption(f'{item["local_departure"]} → {item["local_arrival"]} · багаж до {item["bag_kg"]} кг · {item["price_eur"]} € / человек (демо)')
                st.caption(item['note'])
                if item['allowed']:
                    st.success('Подходит по проверяемым условиям. Доступность мест и правила тарифа нужно подтвердить у поставщика.', icon='✅')
                else:
                    st.warning('Не подходит: '+'; '.join(item['reasons']),icon='⚠️')
            with right:
                if item['allowed']:
                    if st.button('Выбрать', key='choose_'+item['id'],type='primary',use_container_width=True):
                        change_and_rerun(approve_alternative,item['id'])
                else:
                    st.button('Недоступно',key='blocked_'+item['id'],disabled=True,use_container_width=True)


# HEADER AND OVERVIEW
if page=='overview':
    shell('СВОДКА · ДЕМОНСТРАЦИЯ','Путешествие под контролем',
          'Отслеживаем рейсы, проверяем пересадки и помогаем сохранить планы при изменениях.')
    note('Независимый учебный прототип. Рейсы, тарифы и события вымышлены; подключение к авиакомпаниям не выполняется.')
    fresh,age=freshness(state)
    cols=st.columns(5)
    stats=[
        ('Поездка','Москва → Рим','через Стамбул','route'),
        ('Участников','3','групповой маршрут','users'),
        ('Статус рейса',{'on_time':'По плану','delayed':'Задержка','cancelled':'Отмена'}[state['current_status']],
         f'обновлено {age} мин назад','plane'),
        ('Пересадка',f'{connection_minutes(state)} мин' if state['current_status']!='cancelled' else 'нет рейса',
         'требуется 90 минут','clock'),
        ('Уведомления',str(len([n for n in state['notifications'] if n['delivery']=='queued'])),
         'ожидают синхронизации','bell'),
    ]
    for col,(label,value,foot,symbol) in zip(cols,stats):
        with col:kpi(label,value,foot,symbol)
    st.write('')
    left,right=st.columns([1.48,1],gap='medium')
    with left:
        st.markdown('<div class="panel-inside"></div>',unsafe_allow_html=True)
        section('Маршрут поездки','Расписание — демонстрационные данные, время каждого аэропорта местное')
        flight_row(state['flights'][0],state['current_status'],
                   'новое прибытие: '+time_local((dt(state['flights'][0]['arrive'])+timedelta(minutes=state['delay_minutes'])).isoformat()) if state['current_status']=='delayed' else '')
        flight_row(state['flights'][1],'on_time')
        if state.get('selected_plan'):
            st.success('Согласован черновик нового плана: '+state['selected_plan']+'. Бронирования пока не менялись.')
    with right:
        st.markdown('<div class="panel-inside"></div>',unsafe_allow_html=True)
        section('Что важно сейчас','Система оценивает всю поездку, а не только один рейс')
        render_impacts()
    st.write('')
    c1,c2=st.columns([1.45,1],gap='medium')
    with c1:
        st.markdown('<div class="panel-inside"></div>',unsafe_allow_html=True)
        section('Последние события','Источник, время обновления и итог обработки')
        if not state['events']:
            st.info('Событий пока нет. Попробуй задержать рейс в симуляторе.')
        else:
            for e in state['events'][:4]:
                st.markdown(f'**{h(e["status"])}** · {h(e["message"])}')
                st.caption(f'event_id: {e["event_id"]} · {e["observed_at"]}')
        if st.button('Смоделировать задержку +120 мин',type='primary'):
            event_action('delayed',120)
    with c2:
        st.markdown('<div class="panel-inside"></div>',unsafe_allow_html=True)
        section('Условия группы','Проверяемые ограничения на альтернативы')
        for k,v,symbol in [('Багаж','23 кг на участника','briefcase'),
                           ('Въезд в Италию','Визы отмечены как подтверждённые (демо)','shield'),
                           ('Транзит через третью страну','Документы не проверены','alert')]:
            st.markdown('<div class="incident-line"><span class="incicon" style="background:#fff7dc">'+icon(symbol,18,INK)+'</span><span class="incbody"><b>'+h(k)+'</b><small>'+h(v)+'</small></span></div>',unsafe_allow_html=True)
    st.write('')
    if not fresh:
        st.warning(f'Последнее подтверждение статуса было {age} мин назад. Требуется новое событие от поставщика; автоматическое перебронирование запрещено.')

elif page=='trip':
    shell('ЕДИНЫЙ ПЛАН ПОЕЗДКИ','Маршрут и бронирования',
          'Расписание перелётов, трансфер, отель и активность — в одной версии плана для группы.')
    c1,c2,c3=st.columns(3)
    with c1:kpi('Ревизия плана',str(state['revision']),'общая для участников','layers')
    with c2:kpi('Состав группы','3 человека','багаж у каждого: 23 кг','users')
    with c3:kpi('Подтверждение изменений','Нужно согласие','никаких автопокупок','shield')
    st.write('')
    a,b=st.columns([1.6,1],gap='large')
    with a:
        section('Перелёты','Локальное время отправления и прибытия')
        flight_row(state['flights'][0],state['current_status'])
        flight_row(state['flights'][1],'on_time')
        if state.get('selected_plan'):
            st.success(f'Согласованный вариант: {state["selected_plan"]}. Новое предполагаемое прибытие {time_local(state["planned_arrival"])}.')
        section('Связанные бронирования','Подтверждения у поставщиков здесь не имитируются')
        st.markdown(f'**Трансфер** · {state["transfer"]["name"]} — встреча {time_local(state["transfer"]["pickup"])}')
        if state.get('selected_plan'):
            st.caption('Требуется согласовать новое время встречи: '+time_local(state['proposed_transfer_pickup'])+' (пока только черновик).')
        st.markdown(f'**Отель** · {state["hotel"]["name"]} — заселение {time_local(state["hotel"]["checkin"])}')
        st.markdown(f'**Активность** · {state["activity"]["name"]} — {time_local(state["activity"]["start"])}')
    with b:
        section('Последствия изменения рейса','Правила и ограничения')
        render_impacts()
        insight('Почему изменения не происходят автоматически',
                'Цена, документы, правила тарифа и возможность пересадки требуют проверки. Без явного согласия система не покупает билеты и не переносит бронирования.')
        if state['current_status']!='on_time':
            st.markdown('Перейди во вкладку **«План Б»** для выбора безопасного варианта.')

elif page=='events':
    shell('ДЕМО ПОСТАВЩИКА','Симулятор событий рейса',
          'Проверяем, как система реагирует на задержку, отмену, повторные и устаревшие события.')
    note('Это локальный симулятор, а не реальные сведения авиакомпаний. Каждое событие содержит event_id и время источника.')
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button('Задержка +120 мин',type='primary',use_container_width=True): event_action('delayed',120)
    with c2:
        if st.button('Отмена рейса',use_container_width=True): event_action('cancelled')
    with c3:
        if st.button('Восстановить статус',use_container_width=True): event_action('on_time')
    with c4:
        if st.button('Сбросить демо',use_container_width=True):
            reset();st.session_state.pop('last_result',None);st.rerun()
    st.write('')
    left,right=st.columns([1.2,1],gap='large')
    with left:
        section('Имитация внешнего API','Обработка событий не зависит от оформления веб-интерфейса')
        event_json=st.text_area('Пример события JSON (можно редактировать)',
                               value=json.dumps(event_payload('delayed',45),ensure_ascii=False,indent=2),
                               height=215)
        if st.button('Отправить событие',type='primary',key='send_event'):
            try:
                obj=json.loads(event_json)
                result=receive_event(state,obj)
                save(state)
                st.session_state['last_result']=result
                st.rerun()
            except (ValueError,TypeError) as exc:
                st.error('Невозможно разобрать JSON: '+str(exc))
        c5,c6=st.columns(2)
        with c5:
            if st.button('Повторить последнее событие',use_container_width=True):
                if state.get('last_payload'):
                    st.session_state['last_result']=receive_event(state,state['last_payload'])
                    save(state);st.rerun()
                else:st.info('Сначала отправь хотя бы одно событие.')
        with c6:
            if st.button('Прислать устаревшее событие',use_container_width=True):
                payload=event_payload('cancelled')
                payload['observed_at']=(dt(state['flight_data_updated_at'])-timedelta(minutes=120)).isoformat()
                st.session_state['last_result']=receive_event(state,payload)
                save(state);st.rerun()
        if st.session_state.get('last_result'):
            st.json(st.session_state['last_result'])
    with right:
        section('Реакция системы','Альфред смотрит на последствия для всей поездки')
        render_impacts()
        s,age=freshness(state)
        if s: st.success(f'Статус обновлён {age} мин назад.')
        else: st.warning(f'Данные устарели: последнее подтверждение было {age} мин назад.')
        insight('Защита от дублей и «опоздавших» данных',
                'Повторный event_id не создаёт новый инцидент. Событие с более старым временем источника не перезаписывает свежий статус. Пример можно проверить кнопками слева.')
    st.write('')
    section('Журнал событий','Показывает принятые и отклонённые события')
    if state['events']:
        st.dataframe(pd.DataFrame(state['events'])[['event_id','observed_at','status','outcome','message']],hide_index=True,use_container_width=True)
    else:st.info('История событий появится после первой симуляции.')

elif page=='planb':
    shell('НАША ГЛАВНАЯ ФУНКЦИЯ','План Б: сохранить поездку',
          'При сбое предлагаем не просто другой билет, а согласованный маршрут с учётом всей поездки.')
    note('Все тарифы и варианты демонстрационные. Доступность мест, правила багажа и документы надо подтвердить у реального поставщика.')
    if state.get('selected_plan'):
        st.success('Согласован черновик: '+state['selected_plan']+'. Версия плана: '+str(state['revision'])+'. Никакие реальные бронирования не менялись.')
        st.caption('Трансфер требует пересогласования; отель и активности пока остаются без изменений.')
    elif not itinerary_risk(state):
        insight('Критичных изменений пока нет',
                'Чтобы увидеть фильтрацию неподходящих рейсов и согласование маршрута, смоделируй задержку или отмену первого рейса.')
        if st.button('Смоделировать задержку +120 минут',type='primary'):
            event_action('delayed',120)
    else:
        section('Почему нужен новый план','Расчёт времени пересадки в UTC, отображение по местному времени')
        render_impacts()
        if state['current_status']=='delayed':
            st.caption(f'После задержки до второй посадки остаётся {connection_minutes(state)} мин, минимум {90} мин. Сравнение выполнено после нормализации временных зон.')
    section('Рекомендованные и отклонённые варианты','Варианты с недостаточным багажом, визовыми рисками и короткой пересадкой не предлагаются к подтверждению')
    alternatives_table()
    section('Альтернативы активностям', 'Если прибытие сдвигается, планы на вечер тоже требуют внимания')
    st.markdown("""- **Поздний прилёт:** предложить отдых вместо вечерней прогулки и перенести активность на следующий день.
- **Нет подходящих рейсов:** предложить перенести экскурсию, а не выбирать перелёт с визовым риском.
- **Групповая поездка:** согласовать изменение активности со всеми участниками до обращения к поставщику.""")
    insight('Что происходит после согласия',
            'В общей версии плана появляется новый вариант перелёта, а трансфер помечается как требующий пересогласования. В реальной системе подтверждённые изменения должны приходить от поставщиков бронирования.')

elif page=='notifs':
    shell('ОФЛАЙН-РЕЖИМ','Уведомления и синхронизация',
          'Даже если путешественник без связи, события не должны теряться.')
    online='Онлайн' if state['online'] else 'Офлайн'
    q=len([n for n in state['notifications'] if n['delivery']=='queued'])
    c1,c2,c3=st.columns(3)
    with c1:kpi('Статус устройства',online,'симуляция отсутствия связи','wifi-off' if not state['online'] else 'globe')
    with c2:kpi('В очереди',str(q),'будут показаны при подключении','clock')
    with c3:kpi('Всего уведомлений',str(len(state['notifications'])),'события этой сессии','bell')
    if st.button('Переключиться в офлайн' if state['online'] else 'Восстановить подключение и синхронизировать',type='primary'):
        delivered=change_online(state,not state['online'])
        save(state)
        st.session_state['last_delivery']=delivered
        st.rerun()
    if st.session_state.get('last_delivery') and state['online']:
        st.success('После восстановления связи доставлено из очереди: '+str(st.session_state['last_delivery']))
    note('Офлайн-режим здесь моделирует отсутствие связи у пользователя. Система-сервер продолжает принимать события в локальном демо.')
    section('История уведомлений','Уведомления создаются при событии, а при офлайне получают статус «В очереди»')
    if not state['notifications']:
        st.info('Пока уведомлений нет. Перейди в офлайн, затем в симулятор и задержи рейс.')
    else:
        for n in state['notifications']:
            with st.container(border=True):
                c1,c2=st.columns([4,1])
                with c1:
                    st.markdown('**'+n['title']+'**')
                    st.write(n['text'])
                    st.caption(n['created_at'])
                with c2:
                    if n['delivery']=='queued':st.warning('В очереди')
                    else:st.success('Доставлено')
    insight('Поведение в полноценной системе',
            'Сервер хранит очередь уведомлений с TTL и ключом идемпотентности. Push не гарантирует доставку офлайн; после подключения клиент запрашивает непрочитанные события и актуальную ревизию поездки.')

elif page=='api':
    shell('СИСТЕМНЫЙ ДИЗАЙН','API и логика интеграций',
          'Локальный FastAPI позволяет воспроизвести сценарий с событиями без реальных внешних сервисов.')
    c1,c2=st.columns([1.1,1],gap='large')
    with c1:
        section('Минимальный контракт события','POST /api/events')
        st.code('''{
  "event_id": "evt-101",
  "flight_id": "AF101",
  "status": "delayed",
  "delay_minutes": 120,
  "observed_at": "2026-11-08T14:00:00+00:00",
  "source": "mock_provider"
}''',language='json')
        st.markdown('**Основные endpoint-ы**')
        st.code('''GET   /health
GET   /api/trips/demo
GET   /api/flights/AF101
POST  /api/events
GET   /api/trips/demo/alternatives
POST  /api/trips/demo/approve
POST  /api/connectivity
POST  /api/demo/reset''',language='text')
        st.info('Запуск во втором терминале: `python -m uvicorn demo_api:app --host 127.0.0.1 --port 8000`. Swagger: http://127.0.0.1:8000/docs')
    with c2:
        section('Событийная архитектура','Какие компоненты понадобятся в полноценной системе')
        st.markdown('''**API авиапоставщиков / письма**  
↓ Адаптеры и нормализация форматов  
**Очередь событий + дедупликация**  
↓ Проверка времени источника  
**Оркестратор путешествия**  
↓ Правила пересадок, багажа, виз  
**Кандидаты «Плана Б» и подтверждение**  
↓  
**Общий план + уведомления + аудит**''')
        insight('Устаревшие данные',
                'Храним event_id, observed_at и received_at; для решения сравниваем времена источника. При ошибке API выполняем ограниченные повторы с backoff, показываем свежесть статуса и не делаем незаметную перебронь.')
        insight('Персональные и паспортные данные',
                'В демо хранятся только условные визовые флаги. В реальной системе доступ по ролям, шифрование и минимизация полей; паспортные данные удаляются по согласованному сроку после поездки или когда исчезает правовая необходимость.')
    section('Ключевые правила','Это демонстрация логики, а не подключение к реальным авиакомпаниям')
    st.markdown('''- **Идемпотентность:** повторный `event_id` не вызывает повторных изменений.
- **Порядок событий:** более старый `observed_at` не заменяет свежий статус.
- **Временные зоны:** сравнение в UTC, отображение в местном времени каждого аэропорта.
- **Групповая поездка:** учитываем ограничения всех участников, а не только организатора.
- **Надёжность:** при отсутствии связи уведомление ставится в очередь.
- **Безопасность:** варианты требуют подтверждения; реальные покупки и изменения бронирований не выполняются.''')

st.markdown('<p style="color:#929aa5;font-size:10px;margin-top:24px">Альфред · самостоятельный учебный прототип для кейса ИТ-аналитика · все маршруты и сведения демонстрационные.</p>',unsafe_allow_html=True)
