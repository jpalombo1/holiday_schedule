from typing import Optional

import numpy as np
from holidays.constants import Couples, Families, Holidays
from holidays.place import Place


def total_filter(
    places: list[Place],
    holiday: Optional[Holidays] = None,
    family: Optional[Families] = None,
    couple: Optional[Couples] = None,
) -> int:
    place_filter = (
        np.array([place.holiday == holiday for place in places])
        if holiday is not None
        else np.array([True] * len(places))
    )
    holiday_filter = (
        np.array([place.family == family for place in places])
        if family is not None
        else np.array([True] * len(places))
    )
    couple_filter = (
        np.array([place.couple == couple for place in places])
        if couple is not None
        else np.array([True] * len(places))
    )
    return sum(place_filter & holiday_filter & couple_filter)


def matches(our_schedule: list[Place], other_schedule: list[Place]):
    our_schedule.sort()
    other_schedule.sort()
    for our_pl, other_pl in zip(our_schedule, other_schedule):
        if our_pl.year != other_pl.year or our_pl.holiday != other_pl.holiday:
            print("Schedules out of align!, cannot make matches")
            return 0
    return sum(
        our_pl.same_place(other_pl)
        for our_pl, other_pl in zip(our_schedule, other_schedule)
    )


def spread_table(our_schedule: list[Place]):
    table = []
    print(
        "".join(
            ["Holiday" + " " * 15] + [f"{fam.value:10}" for fam in Families] + ["Total"]
        )
    )
    for idx, holiday in enumerate(Holidays):
        table.append([])
        row_val = 0
        for family in Families:
            val = total_filter(our_schedule, holiday, family, Couples.US)
            row_val += val
            table[idx].append(f"{val:10}")
        print("".join([f"{holiday.value:15}"] + table[idx] + [f"{row_val:10}"]))
    total = []
    for family in Families:
        val = total_filter(our_schedule, holiday=None, family=family, couple=Couples.US)
        total.append(f"{val:10}")
    print("".join(["Total" + " " * 10] + total))
