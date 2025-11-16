from enum import Enum, auto

class State(Enum):
    START             = auto()
    WAIT_CONFIRMATION = auto()
    WAIT_DESCRIPTION  = auto()
    WAIT_LOCATION     = auto()
    WAIT_PHOTO        = auto()
    COMPLETED         = auto()