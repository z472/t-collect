from dataclasses import dataclass
from abc import ABC, abstractmethod
import weakref


class BaseNotes(ABC):
    def __init_subclass__(cls, **kw) -> None:
        super().__init_subclass__(**kw)
        # ?
        if not hasattr(cls, "__notes_map"):
            cls.__notes_map = weakref.WeakKeyDictionary()
    
    @classmethod
    def get_notes(cls, key:any):
        # why unuse 'not in' 
        try:
            return cls.__notes_map[key]
        except KeyError:
            cls.__notes_map[key] = cls.init_notes()
            return cls.__notes_map[key]


class RequestNotes(BaseNotes):
    ...