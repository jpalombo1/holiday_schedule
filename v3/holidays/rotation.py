from dataclasses import dataclass
from typing import Dict

from holidays.constants import Families, Holidays


@dataclass
class Rotation:
    """Rotation Object used so that each holidayy in a year is assigned to a family,
    when other couples have a given rotation of one family per holiday.

    Dict object is actually used but this object is type safe to assure all holidays are completed with a
    family at intialization.
    """

    easter: Families
    thanks: Families
    eve: Families
    christmas: Families

    def dict(self) -> Dict[Holidays, Families]:
        """Dictionary dunder to convert this object to dictionary.

        Used in practice so this object can be indexed by enum holiday type when looping through holidays instead of getting class attributes.

        e.g. doing rotation.easter, rotation.eve, etc. is more annoying than dict(rotation)[holiday] for holiday in Holidays
        """
        return {
            Holidays.EASTER: self.easter,
            Holidays.THANKSGIVING: self.thanks,
            Holidays.EVE: self.eve,
            Holidays.CHRISTMAS: self.christmas,
        }
