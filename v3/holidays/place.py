from __future__ import annotations

from dataclasses import dataclass

from holidays.constants import Couples, Families, Holidays, Status


@dataclass
class PrimeSec:
    """Keeps track of primary and secondary visits for a given holiday to a given family from a couple."""

    primary: int = 0
    secondary: int = 0

    def add_prime(self) -> None:
        """Add to primary visit count."""
        self.primary += 1

    def add_sec(self) -> None:
        """Add to secondary visit count."""
        self.secondary += 1


@dataclass
class Place:
    """Object of event with one couple at one family for one holiday of given year and primary/secondary visit."""

    year: int
    couple: Couples
    holiday: Holidays
    family: Families
    status: Status

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
