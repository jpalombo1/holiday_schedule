from __future__ import annotations

import itertools
from dataclasses import dataclass

# Holiday Statuses
GONE = "GONE"
GRESKO = "Gresko"
PALOMBO = "Palombo"
PENDOLA = "Pendola"


@dataclass
class Year:
    """Define where holidays are for given year."""

    easter: str
    thanksgiving: str
    eve: str
    christmas: str

    @property
    def list(self) -> list[str]:
        return [self.easter, self.thanksgiving, self.eve, self.christmas]


class Couple:
    """Keeps years and holiday locations for different people."""

    def __init__(self, year_list: list[Year], name: str = "us"):
        self.init_year: int = 2022
        self.year_dict: dict[str, Year] = {
            str(self.init_year + year_num): year
            for year_num, year in enumerate(year_list)
        }
        self.years = sorted(list(self.year_dict.keys()))
        self.num_years: int = len(self.years)
        self.name: str = name

    def holidays_year_list(self, year: str) -> list[str]:
        """Return year object of given year to list"""
        return self.year_dict[year].list

    @property
    def all_holidays(self) -> list[str]:
        """Get flattened list of all holidays over all years."""
        all_holidays = []
        for year in self.years:
            that_year = self.year_dict[year]
            all_holidays.append(
                [
                    that_year.easter,
                    that_year.thanksgiving,
                    that_year.eve,
                    that_year.christmas,
                ]
            )
        return sum(all_holidays, [])


class Schedule:
    """Holds possible scheduless for main couple when compared to other couple schedule."""

    def __init__(self, possible: list[str]):
        self.possible = possible
        self.schedule_by_year: dict[str, Year] = {}

    @property
    def all_schedules(self) -> list[list[str]]:
        """Get all possible combinations of schedules given families and holidays. If less length, get combos of known, then combos of missing and combine."""
        if len(self.possible) < 4:
            missing_sched = 4 - len(self.possible)
            known_perms = list(itertools.permutations(self.possible))
            fill_perms = list(itertools.permutations(self.possible, missing_sched))
            possible_list = [
                known + fill for fill in fill_perms for known in known_perms
            ]
        else:
            possible_list = [
                possible[:4] for possible in itertools.permutations(self.possible)
            ]

        unique_possible_list = []
        for possible in possible_list:
            if possible not in unique_possible_list:
                unique_possible_list.append(list(possible))
        return unique_possible_list

    def get_matches(self, schedule: list[str], couple: Couple, year: str) -> int:
        """get number of matches between our schedule"""
        our_year = schedule
        couple_year = couple.holidays_year_list(year)
        return sum(o == c for o, c in zip(our_year, couple_year))

    @property
    def all_holidays(self) -> list[str]:
        """Get flattened list of all holidays over all years."""
        all_holidays = []
        years = sorted(list(self.schedule_by_year.keys()))
        for year in years:
            that_year = self.schedule_by_year[year]
            all_holidays.append(that_year.list)
        return sum(all_holidays, [])

    def calculate_spread(
        self, schedule: dict[str, Year]
    ) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
        """Calculate occurance dictionaries indexed by holiday then family per holiday, also holiday and holiday per family."""
        holiday_spread: dict[str, dict[str, int]] = {}
        family_spread: dict[str, dict[str, int]] = {}
        holidays = ["easter", "thanksgiving", "eve", "christmas"]
        families = [GRESKO, PALOMBO, PENDOLA]
        for default_holiday in holidays:
            if default_holiday not in holiday_spread:
                holiday_spread[default_holiday] = {}
                for default_fam in families:
                    holiday_spread[default_holiday][default_fam] = 0
        for default_fam in families:
            if default_fam not in family_spread:
                family_spread[default_fam] = {}
                for default_holiday in holidays:
                    family_spread[default_fam][default_holiday] = 0

        years = sorted(list(schedule.keys()))
        for year in years:
            that_year = schedule[year]
            year_dict = that_year.__dict__
            for holiday, family in year_dict.items():
                holiday_spread[holiday][family] += 1
                family_spread[family][holiday] += 1

        return holiday_spread, family_spread

    @property
    def holiday_spread(self) -> dict[str, dict[str, int]]:
        return self.calculate_spread(self.schedule_by_year)[0]

    @property
    def family_spread(self) -> dict[str, dict[str, int]]:
        return self.calculate_spread(self.schedule_by_year)[1]

    def optimize_spread(
        self, schedules: list[list[str]], matches: list[int]
    ) -> list[str]:
        """Optimize year by year best schedule by # of matches to relatives and spread of holidays between families."""
        metrics = []
        for schedule, match in zip(schedules, matches):
            possible_schedule = self.schedule_by_year.copy()
            possible_schedule["next"] = Year(*schedule)
            holiday_spread, family_spread = self.calculate_spread(possible_schedule)

            # Score per family of difference of # min occurances of holiday compared to other holidays for the family
            # Higher this is, more uneven of some families only getting some holidays
            # e.g family= Gresko, ea,th,eve,chr occur = [3,2,4,5] score = sum([3,2,4,5] - 2) = sum(1,0,2,3) = 6, score+=6, next family
            family_across_holiday_metric = 0
            for holiday_dict in family_spread.values():
                family_freq = list(holiday_dict.values())
                family_across_holiday_metric += sum(family_freq) - min(
                    family_freq
                ) * len(family_freq)

            # Score per holiday of difference of # min occurances of family compared to other families for the holiday
            # Higher this is, more uneven of different families dominate different holidays
            # e.g. holiday = eve, gre,pa,pe occur = [6,4,2] socre = sum([6,4,2] - 20 = sum(4,2,0) = 6, score +=6 next holiday
            family_per_holiday_metric = 0
            for family_dict in holiday_spread.values():
                holiday_freq = list(family_dict.values())
                family_per_holiday_metric += sum(holiday_freq) - min(
                    holiday_freq
                ) * len(holiday_freq)

            # Score accounts # of matches most heavily, then spread of holidays per fam and spread of families per holiday weighed equally
            metrics.append(
                -10 * match + family_per_holiday_metric + family_across_holiday_metric
            )
        min_index = metrics.index(min(metrics))
        return schedules[min_index]

    def add_year(self, schedule: list[str], year: str):
        """Append best schedule for given year to overall schedule dict."""
        self.schedule_by_year[year] = Year(*schedule)

    def best_year_by_year(self, couples: list[Couple], year: str) -> list[str]:
        """Get best schedule for given year, calculating matches that year then optimizing based on that and existing holiday spread."""
        matches = [
            [self.get_matches(schedule, couple, year) for couple in couples]
            for schedule in self.all_schedules
        ]
        schedule_total_matches = [sum(couple_matches) for couple_matches in matches]
        optimal_schedule = self.optimize_spread(
            self.all_schedules, schedule_total_matches
        )
        return optimal_schedule

    def calc_best_schedule(self, couples: list[Couple]):
        """Calculate best schedule over all years for couple"""
        years = couples[0].years
        for year in years:
            self.add_year(self.best_year_by_year(couples, year), year)


def main():
    our_possible = [GRESKO, GRESKO, PALOMBO, PENDOLA]
    ours = Schedule(our_possible)

    # Other siblings to compare
    ali = Couple(
        [
            # Year(PENDOLA,GONE,PALOMBO,PENDOLA),
            Year(PALOMBO, PALOMBO, PENDOLA, GONE),
            Year(GONE, PENDOLA, GONE, PALOMBO),
            Year(PENDOLA, GONE, PALOMBO, PENDOLA),
        ]
        * 4,
        "ali",
    )
    print("Ali schedule")
    print("\n".join(ali.all_holidays))

    lauren = Couple(
        [
            # Year(GONE,GRESKO,GRESKO,GRESKO),
            # Year(GONE, GONE, GONE, GONE)
            Year(GONE, GONE, GRESKO, GRESKO),
            Year(GONE, GRESKO, GONE, GONE),
            Year(GONE, GONE, GRESKO, GRESKO),
            Year(GONE, GRESKO, GONE, GONE),
        ]
        * 3,
        "lauren",
    )
    print("Lauren schedule 1")
    print("\n".join(lauren.all_holidays))

    # lauren_2 = Couple(
    #     [
    #         # Year(GONE,GRESKO,GRESKO,GRESKO),
    #         # Year(GONE, GONE, GONE, GONE),
    #         Year(GONE, GRESKO, GONE, GONE),
    #         Year(GONE, GONE, GRESKO, GRESKO),
    #         Year(GONE, GRESKO, GONE, GONE),
    #         Year(GONE, GONE, GRESKO, GRESKO),
    #     ] * 3,
    #     "lauren2"
    # )
    # print("Lauren schedule 2")
    # print("\n".join(lauren_2.all_holidays))

    ours.calc_best_schedule([ali, lauren])
    print("Our schedule")
    print("\n".join(ours.all_holidays))
    print(ours.holiday_spread)
    print(ours.family_spread)


if __name__ == "__main__":
    main()
