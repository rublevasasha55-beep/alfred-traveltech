from datetime import datetime, timedelta, timezone
from engine import (initial_state, receive_event, connection_minutes, itinerary_risk,
                    alternatives, approve_alternative, change_online, freshness)


def event(state, ident, status='delayed', delay=120, delta=1):
    base=datetime.fromisoformat(state['flight_data_updated_at'])
    return {'event_id':ident,'flight_id':'AF101','status':status,
            'delay_minutes':delay,'observed_at':(base+timedelta(seconds=delta)).isoformat(),
            'source':'demo'}


def test_delay_impact_and_local_timezone():
    state=initial_state()
    assert connection_minutes(state)==140
    result=receive_event(state,event(state,'evt-1'))
    assert result['outcome']=='accepted'
    assert itinerary_risk(state)
    assert connection_minutes(state)==20
    assert any('пересадку' in x['title'] for x in __import__('engine').trip_impacts(state))


def test_duplicate_event_no_repeated_notification():
    state=initial_state();p=event(state,'evt-2')
    assert receive_event(state,p)['outcome']=='accepted'
    assert len(state['notifications'])==1
    assert receive_event(state,p)['outcome']=='duplicate'
    assert len(state['notifications'])==1


def test_stale_event_does_not_undo_fresh():
    state=initial_state();receive_event(state,event(state,'evt-3'))
    old=event(state,'evt-4','cancelled',0,delta=-3600)
    assert receive_event(state,old)['outcome']=='stale'
    assert state['current_status']=='delayed'


def test_baggage_visa_connection_filters():
    state=initial_state();receive_event(state,event(state,'evt-5'))
    choices={x['id']:x for x in alternatives(state)}
    assert choices['ALT-IST-1']['allowed']
    assert not choices['ALT-IST-2']['allowed']
    assert any('Багаж' in r for r in choices['ALT-IST-2']['reasons'])
    assert not choices['ALT-IST-4']['allowed']
    assert any('Пересадка' in r for r in choices['ALT-IST-4']['reasons'])
    assert not choices['ALT-IST-5']['allowed']
    assert any('Транзитные' in r for r in choices['ALT-IST-5']['reasons'])
    state['travellers'][0]['schengen_visa']='unverified'
    assert not any(x['allowed'] for x in alternatives(state))


def test_cancel_flight_origins():
    state=initial_state();receive_event(state,event(state,'evt-6','cancelled',0))
    assert itinerary_risk(state)
    assert all(x['origin']=='SVO' for x in alternatives(state))
    assert any(x['allowed'] for x in alternatives(state))


def test_user_approval_is_only_a_draft_and_transfer_is_flagged():
    state=initial_state();receive_event(state,event(state,'evt-7'))
    assert not approve_alternative(state,'ALT-IST-2')['ok']
    assert approve_alternative(state,'ALT-IST-1')['ok']
    assert state['selected_plan']=='ALT-IST-1'
    assert state['revision']==2
    assert state['transfer_status']=='reschedule_required'
    assert state['transfer']['pickup']=='2026-11-20T18:20:00+01:00'


def test_offline_queue_sync():
    state=initial_state()
    assert change_online(state,False)==0
    receive_event(state,event(state,'evt-8'))
    assert state['notifications'][0]['delivery']=='queued'
    assert change_online(state,True)==1
    assert state['notifications'][0]['delivery']=='delivered'


def test_offline_cannot_approve():
    state=initial_state();receive_event(state,event(state,'evt-9'))
    change_online(state,False)
    assert not approve_alternative(state,'ALT-IST-1')['ok']


def test_freshness():
    state=initial_state()
    then=datetime.fromisoformat(state['flight_data_updated_at'])+timedelta(minutes=45)
    assert freshness(state,then)[0] is False
    assert freshness(state,then)[1]==45


def test_invalid_event_and_timezone():
    state=initial_state()
    assert receive_event(state,{'event_id':'bad','flight_id':'AF101','status':'delayed',
           'delay_minutes':120,'observed_at':'2026-11-08T11:00:00'})['outcome']=='invalid'
    assert len(state['events'])==0
