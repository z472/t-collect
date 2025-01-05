from pydantic import BaseModel
from django.http import HttpRequest, HttpResponse
from requests.models import Request, Response
from ..lib.django_request import RequestNotes
from .event_queue import ClientDescriptor,fetch_events
from asgiref.sync import async_to_sync

class UserForTest(BaseModel):   
    id : int 
    name : str
    age : int


def get_events_backend(request: Request, *,
                       user_profile_id:id, 
                       queue_id : str=None,
                       last_event_id : int, ) -> Response:  
    # not only get event from event_queue but also create client at first time.
    # like rpc in zulip this view is important but don't as restful api 
    # handler_id : distinguish every request for the long polling
    handler_id = RequestNotes.get_notes(request).tornado_handler_id
    assert handler_id is not None
    
    if queue_id is None:
        # many parameters are ommited.
        new_queue_data = dict(
            user_profile_id=user_profile.id,)
    
    result = in_tornado_thread(fetch_events)(
        queue_id=queue_id,
        last_event_id=last_event_id,
        user_profile_id=user_profile_id,
        handler_id=handler_id,
        new_queue_data=new_queue_data)
        
# fetch_events is a sync func with a async action (loop.call_later())
# and we want to run it in sync context(func get_events_backend).
def in_tornado_thread(afnc):    
    async def wrap(*args,**kw):
        return afnc(*args, **kw)
    return async_to_sync(wrap)
    