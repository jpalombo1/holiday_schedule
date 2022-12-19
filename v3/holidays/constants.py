from enum import Enum

GONE = "GONE"


class Status(Enum):
    """Status of Get Together, mostly primary."""

    PRIMARY = "Primary"
    SECOND = "Secondary"


class Couples(Enum):
    """Names of couples, main and others ot match."""

    US = "Us"
    ALI = "Ali"
    LAUREN = "Lauren"
    JAMES = "James"
    GEORGE = "George"


class Families(Enum):
    """Name of families to go to."""

    GRESKO = "Gresko"
    PALOMBO = "Palombo"
    PENDOLA = "Pendola"
    GONE = "GONE"


class Holidays(Enum):
    """Name of holidays to get together."""

    EASTER = "Easter"
    THANKSGIVING = "Thanksgiving"
    CHRISTMAS = "Christmas"
    EVE = "Chirstmas Eve"
