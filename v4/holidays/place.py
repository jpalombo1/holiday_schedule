from __future__ import annotations

from dataclasses import dataclass

from holidays.constants import Couples, Families, Holidays


@dataclass
class Place:
    """Object of event with one couple at one family for one holiday of given year and primary/secondary visit."""

    year: int
    couple: Couples
    holiday: Holidays
    family: Families

    def same_place(self, other: Place) -> bool:
        """Checks if 2 place objects, mainly for 2 couples, are at the same place if the year holiday and family are the same.

        Used for metrics.
        """
        return (
            self.year == other.year
            and self.holiday == other.holiday
            and self.family == other.family
        )

    def __repr__(self) -> str:
        """Printable format for this object."""
        return f"{self.couple.value} at {self.family.value} for {self.holiday.value} in {self.year}"

    def __lt__(self, other: Place) -> bool:
        holiday_order = [holiday for holiday in Holidays]
        if self.year != other.year:
            return self.year < other.year
        return holiday_order.index(self.holiday) < holiday_order.index(other.holiday)

    def __gt__(self, other: Place) -> bool:
        holiday_order = [holiday for holiday in Holidays]
        if self.year != other.year:
            return self.year > other.year
        return holiday_order.index(self.holiday) > holiday_order.index(other.holiday)
