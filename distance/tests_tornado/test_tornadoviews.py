from urllib3.util import Retry
from requests import Session
from requests.adapters import HTTPAdapter


class TornadoAdapter(HTTPAdapter):
    def __init__(self) -> None:
        # cv from https://requests.readthedocs.io/en/latest/user/advanced/#example-automatic-retries
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504],
            allowed_methods={'POST'},
        )
        super().__init__(max_retries=retries)

def requests_client() -> Session:
    c = Session()
    adapter = TornadoAdapter()
    for scheme in ("https://", "http://"):
        c.mount(scheme, adapter)
    return c

