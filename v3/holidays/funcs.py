from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd  # type: ignore
from holidays.constants import Couples, Families, Holidays, Status
from holidays.place import Place, PrimeSec


def couple_holiday_count(
    places: List[Place], couple: Couples, holiday: Optional[Holidays] = None
) -> Dict[Families, PrimeSec]:
    """Make count mapping of number of times a given couple visits each family primary/secondary.

    If holiday specified, only gives counts for holiday, else do all holidays.

    e.g Us visit palombo 1 prime 2 sec, pendola 2 prime 1 sec gresko 3 prime 2 sec.
    """
    couple_places = [place for place in places if place.couple == couple]
    if holiday is not None:
        couple_places = [place for place in couple_places if place.holiday == holiday]
    place_count: Dict[Families, PrimeSec] = {}
    for place in couple_places:
        if place.family not in place_count:
            place_count[place.family] = PrimeSec()
        if place.status == Status.PRIMARY:
            place_count[place.family].add_prime()
        else:
            place_count[place.family].add_sec()
    return place_count


def sibling_match_count(places: List[Place], couple: Couples) -> Dict[Couples, int]:
    """Checks for each other couple, how many times the main couple is at the sample place as them.

    Loops through all other places and then looks at all main couple places.
    If there is a main couple place that matches the other place, add to count for other couple, then move not next other place.

    Args:
        places (List[Place]): Places visited by main couple in question and others.

    Returns:
        Dict[Couples, int]: Mapping of other couples to number of matches where other couple's place is same as main couple.
    """
    couple_places = [place for place in places if place.couple == couple]
    other_places = [place for place in places if place.couple != couple]
    match_count = {}
    for other_place in other_places:
        for couple_place in couple_places:
            if other_place.same_place(couple_place):
                if other_place.couple not in match_count:
                    match_count[other_place.couple] = 0
                match_count[other_place.couple] += 1

    return match_count


def num_available(places: List[Place], couple: Couples) -> int:
    """Calculates the number of times the couple is not GONE and available to be matched with for all place objects."""
    return len(
        [
            place
            for place in places
            if place.family != Families.GONE and place.couple == couple
        ]
    )


def print_results(places: List[Place], main_couple: Couples) -> str:
    """Printable results based on schedule, including metrics."""
    print_str = "RESULTS\n\n"
    min_year = min(place.year for place in places)
    max_year = max(place.year for place in places)

    for year in range(min_year, max_year + 1):
        for holiday in Holidays:
            our_place = [
                place
                for place in places
                if place.couple == main_couple
                and place.year == year
                and place.holiday == holiday
            ]
            other_places = [
                place
                for place in places
                if place.couple != main_couple
                and place.year == year
                and place.holiday == holiday
            ]
            other_fam_str = "|".join(
                f"{place.couple.value:^8}|{place.family.value:^10}"
                for place in other_places
            )
            print_str += f"|{year:^3}|{holiday.value:^15}|{our_place[0].couple.value:^2}|{our_place[0].family.value:^10}|{other_fam_str}|\n"
    print_str += "\n"

    match_count = sibling_match_count(places, couple=main_couple)
    for couple, count in match_count.items():
        couple_avail = num_available(places, couple)
        if couple == main_couple:
            continue
        print_str += f"| {couple.value:^8} | Availble | {couple_avail} | Match | {count} | Percent | {count/couple_avail*100:.2f}% |\n"
    print_str += "\n"

    for holiday in Holidays:
        hol_spread = couple_holiday_count(places, main_couple, holiday=holiday)
        hol_str = "".join(
            [
                f"{family.value:^7}|{hol_spread[family].primary:^3}|"
                for family in Families
                if family is not Families.GONE
            ]
        )
        print_str += f"|{holiday.value:^15}|{hol_str}\n"
    all_spread = couple_holiday_count(places, main_couple)
    all_str = "".join(
        [
            f"{family.value:^7}|{all_spread[family].primary:^3}|"
            for family in Families
            if family is not Families.GONE
        ]
    )
    print_str += f"|      All      |{all_str}\n"

    return print_str


def import_places(csv_path: Path) -> List[Place]:
    """Given csv, import to get list of place objects.

    CSV has year header int, couple holiday family headers with strings that match values of corresponding structs case-insensitive.
    """
    pd_csv = pd.read_csv(csv_path)
    return [
        Place(
            year=row["year"],
            couple=Couples.__dict__[row["couple"].upper()],
            holiday=Holidays.__dict__[row["holiday"].upper()],
            family=Families.__dict__[row["family"].upper()],
            status=Status.PRIMARY,
        )
        for _, row in pd_csv.iterrows()
    ]


def export_csv(places: List[Place], csv_path: Path) -> None:
    """Export list of places to csv. If year just use int, else get value from enum type."""
    pd_dict: Dict[str, List[str]] = {
        "year": [],
        "couple": [],
        "holiday": [],
        "family": [],
    }
    for place in places:
        for key, val in pd_dict.items():
            if key == "year":
                val.append(place.__dict__[key])
                continue
            val.append(place.__dict__[key].value)
    pd_df = pd.DataFrame(pd_dict)
    pd_df.to_csv(csv_path)
