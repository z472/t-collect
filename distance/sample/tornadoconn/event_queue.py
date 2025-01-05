from collections import deque
from typing import Any,MutableMapping
import random,time,tornado

HEARTBEAT_MIN_FREQ_SECS = 45

class ClientDescriptor:
    def __init__( 
        self,
        user_profile_id: int,
        realm_id: int,
        event_queue: "EventQueue",
        ):
        self.user_profile_id = user_profile_id
        self.realm_id = realm_id
        self.event_queue = event_queue
        
    
    def connect_handler(self, handler_id: int, client_name: str) -> None:
        self.current_handler_id = handler_id
        self.current_client_name = client_name
        descriptors_by_handler_id[handler_id] = self
        self.last_connection_time = time.time()

        def timeout_callback() -> None:
            self._timeout_handle = None                        
            self.add_event(dict(type="heartbeat"))

        ioloop = tornado.ioloop.IOLoop.current()
        interval = HEARTBEAT_MIN_FREQ_SECS + random.randint(0, 10)
        self._timeout_handle = ioloop.call_later(interval, timeout_callback)
        
class EventQueue:
    def __init__(self, id: str) -> None:
        self.queue: deque[dict[str, Any]] = deque()
        self.next_event_id: int = 0
        # will only be None for migration from old versions
        self.newest_pruned_id: int | None = -1
        self.id: str = id
    
def fetch_events(
    queue_id: str | None,
    last_event_id: int | None,
    user_profile_id: int,
    handler_id: int,
    new_queue_data: MutableMapping[str, Any] | None,
)-> dict[str, Any]:
    try:        
        if queue_id is None:
            client = allocate_client_descriptor(new_queue_data)
            queue_id = client.event_queue.id                        
        else:            
            # last_event_id made when (browser)client got the last event.
            if last_event_id is None:
                raise RuntimeError("Missing 'last_event_id' argument")
            client = access_client_descriptor(user_profile_id, queue_id)
            if (
                client.event_queue.newest_pruned_id is not None
                and last_event_id < client.event_queue.newest_pruned_id
            ):
                raise RuntimeError(
                    ("An event newer than {event_id} has already been pruned!").format(
                        event_id=last_event_id,
                    )
                )
            client.event_queue.prune(last_event_id)
            was_connected = client.finish_current_handler()
        if not client.event_queue.empty():
            response: dict[str, Any] = dict(
                events=client.event_queue.contents(),
            )
            response["queue_id"] = queue_id
            extra_log_data = "[{}/{}]".format(queue_id, len(response["events"]))
            if was_connected:
                extra_log_data += " [was connected]"
            return dict(type="response", response=response, extra_log_data=extra_log_data)            
    except RuntimeError as e:
        return dict(type="error", exception=e)

    client.connect_handler(handler_id)
    return dict(type="async")


        
# maps queue ids to client descriptors
clients: dict[str, ClientDescriptor] = {}
# maps user id to list of client descriptors
user_clients: dict[id, list[ClientDescriptor]] = {}
# ...
descriptors_by_handler_id: dict[int, "ClientDescriptor"] = {}