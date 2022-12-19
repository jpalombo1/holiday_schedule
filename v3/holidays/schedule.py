from dataclasses import dataclass
from typing import Dict, List, Optional

from holidays.constants import Couples, Families, Holidays, Status
from holidays.funcs import couple_holiday_count, sibling_match_count
from holidays.place import Place
from holidays.rotation import Rotation


@dataclass
class Scheduler:
    """For a given couple devise a schedule that optimizes family distribution and matching others schedules.

    Parameters
    ----------

    couple: Couple
        target couple to schedule
    num_years: int
        Number of years to construct schedule to optimize
    fam_prime_dist: Dict[Families, float]:
        Target distribution of family spread of holidays e.g. Palombo 0.25 Pendola 0.25 Gresko 0.5 means Gresko 50% holidays etc.
    sib_weights: Dict[Couples, float]:
        Importance of matching with each sibling. Weights add to 1. e.g. Ali 50 Lauren 33 James 16
    rotations: Dict[Couples, List[Rotation]]:
        Schedule of each couple where Rotation is 1 year of holidays and list is regular rotation. Just need minimum num rotations until cycle.
    """

    couple: Couples
    start_year: int
    num_years: int
    fam_prime_dist: Dict[Families, float]
    sib_weights: Dict[Couples, float]
    rotations: Dict[Couples, List[Rotation]]
    history: Optional[List[Place]] = None

    def __post_init__(self) -> None:
        """Declare list of places to construct schedule.

        Attributes
        ----------
        places: List[Place]
            List of places ventured by couple for year holiday which family at.
        other_places: List[Place]
            List of places gone to by other couples scheduling with.
        """
        self.places: List[Place] = self.history if self.history is not None else []

    def _calc_fam_spread(
        self, places: List[Place], holiday: Optional[Holidays] = None
    ) -> float:
        """Get real time distribution of family per couple then score compared to objective.

        First get count of number of times couple visits each family, then normalizes distribution by dividing count by total occurances.
        Then score is average(1 - abs(actual_share - target_share)/target_score) for each family where 0 is worst and 1 is best.

        e.g. actual share [3,5,2] notmalized [0.3,0.5,0.2] target dist [0.25,0.5,0.2],
        score = avg[1-2*abs(0.3-0.25)/0.25, 1-2*abs(0.5-0.5)/0.5, 1-2*abs(0.2-0.25)/0.25]=avg[1-0.2 1-0 1-0.2]=avg[0.8,1,0.8]=0.82
        """
        fam_count = couple_holiday_count(places, self.couple, holiday=holiday)
        num_places = sum(fcount.primary for fcount in fam_count.values())
        fam_act_dist = {
            fam: fcount.primary / num_places for fam, fcount in fam_count.items()
        }
        if len(fam_act_dist) == 0:
            return 1
        return sum(
            1 - abs(self.fam_prime_dist[fam] - fam_actual) / self.fam_prime_dist[fam]
            for fam, fam_actual in fam_act_dist.items()
        )

    def _calc_sib_match(
        self, places: List[Place], year: int, holiday: Holidays
    ) -> float:
        """Get score of sibling matches with the more out of total being best.

        First get number of matches between places of ocuple and other places of other couples with map of other couple to num matches.
        Multiple match by weight of sibling match and divide by number of couples to match to normalize.

        e.g places is 4 for year of couple, 2 match for Lauren 1 for Ali, weights 0.5 Ali 0.4 Lauren for both score is sum(1*0.5 + 2*0.4)/4 = 0.325
        """
        places = [
            place for place in places if place.year == year and place.holiday == holiday
        ]
        sib_matches = sibling_match_count(places, couple=self.couple)
        return sum(
            sib_match * self.sib_weights[sib] for sib, sib_match in sib_matches.items()
        ) * sum(self.sib_weights.values())

    def _add_other_couples(self, year: int, holiday: Holidays) -> List[Place]:
        """Based on the other couples and given rotation of holidays for the year, add the place a couple is at the given year and holiday.

        Get the family the holiday is on by first getting rotation based on years rotating through it with modulo,
        then get family by indexing dict version of rotation object by given holiday.
        Then form place with family couple year holiday and add a new place object for each couple in rotations object.

        e.g. Lets say Ali schedule alternates every 2 years and on year 3, rotation index = 3 % 2 = 1 so rotation[1],
        family for easter is rotation[1].easter or rotation[1].dict[Holidays.EASTER] = Palombo, in dict form so no attr needed in loop.
        Then make place with Palombo fam Ali couple year 3 holiday easter.

        Args:
            year (int): Year to make place.
            holiday (Holidays): Holiday to make place.

        Returns:
            List[Place]: Other places that couples go to based on location.
        """
        other_places = []
        for couple, rotation in self.rotations.items():
            this_rotation = year % len(rotation)
            family = rotation[this_rotation].dict()[holiday]
            other_places.append(
                Place(
                    year=year,
                    couple=couple,
                    holiday=holiday,
                    family=family,
                    status=Status.PRIMARY,
                )
            )
        return other_places

    def _attempt_allocation(self, year: int, holiday: Holidays) -> Place:
        """For each family, try it to see which best helps couple get closer to overall distribution and matches other couples.

        Get other couple's current place given the year and holiday based on their schedules.
        Then try every family option for given year and holiday.
        Based on main couple current visits, determine distribution score if visit given family, higher score is dist closer to ideal.
        Match score then if choosing family will match sibling given their places and current attempted place.

        Final choice will be max score whic his highest addtion of match and dist scores.

        Args:
            year (int): year for attempt.
            holiday (Holidays):holiday for attempt

        Returns:
            Place: Place object that contains family visited for year and holiday.
        """
        max_score = -1e10
        max_place: Place
        other_places = self._add_other_couples(year, holiday)
        self.places += other_places
        for family in Families:
            if family is Families.GONE:
                continue
            place = Place(
                year=year,
                couple=self.couple,
                holiday=holiday,
                family=family,
                status=Status.PRIMARY,
            )
            tmp_places = self.places + [place]

            dist_score = self._calc_fam_spread(tmp_places)
            hol_dist_score = sum(
                self._calc_fam_spread(tmp_places, sel_holiday)
                for sel_holiday in Holidays
            ) / len(Holidays)
            match_score = self._calc_sib_match(tmp_places, year=year, holiday=holiday)
            score = dist_score + match_score + hol_dist_score
            if score > max_score:
                max_place = place
                max_score = score
        return max_place

    def schedule(self):
        """Main method to do scheduling for every yer and holiday."""
        for year in range(self.start_year, self.num_years + self.start_year):
            for holiday in Holidays:
                self.places.append(self._attempt_allocation(year, holiday))
