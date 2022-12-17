from typing import Dict, List, Optional

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
        couple_places = [place for place in places if place.holiday == holiday]

    place_count: Dict[Families, PrimeSec] = {}
    for place in couple_places:
        if place.family not in place_count:
            place_count[place.family] = PrimeSec()
        if place.status == Status.PRIMARY:
            place_count[place.family].add_prime()
        else:
            place_count[place.family].add_sec()
    return place_count


def sibling_match_count(
    couple_places: List[Place], other_places: List[Place]
) -> Dict[Couples, int]:
    """Checks for each other couple, how many times the main couple is at the sample place as them.

    Loops through all other places and then looks at all main couple places.
    If there is a main couple place that matches the other place, add to count for other couple, then move not next other place.

    Args:
        couple_places (List[Place]): Places visited by main couple in question.
        other_places (List[Place]): Places visited by other couples wish to match to.

    Returns:
        Dict[Couples, int]: Mapping of other couples to number of matches where other couple's place is same as main couple.
    """
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
