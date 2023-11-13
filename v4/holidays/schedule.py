import random

from holidays.constants import Couples, Families, Holidays
from holidays.place import Place


def ali_rule(start_year: int, num_years: int) -> list[Place]:

    rotation = [Families.PALOMBO, Families.GONE, Families.PENDOLA]
    # Go from (Pendola,Gone,Palombo) -> (Palombo,Pendola,Gone) Easters
    # Go from (Pendola,Gone,Palombo) -> (Palombo,Pendola,Gone) Thanks,Eve,Christmas
    holidays = [
        [
            Place(
                year=year + start_year,
                couple=Couples.ALI,
                holiday=Holidays.EASTER,
                family=rotation[year % len(rotation)],
            ),
            Place(
                year=year + start_year,
                couple=Couples.ALI,
                holiday=Holidays.THANKSGIVING,
                family=rotation[year % len(rotation)],
            ),
            Place(
                year=year + start_year,
                couple=Couples.ALI,
                holiday=Holidays.EVE,
                family=rotation[(year + 2) % len(rotation)],
            ),
            Place(
                year=year + start_year,
                couple=Couples.ALI,
                holiday=Holidays.CHRISTMAS,
                family=rotation[(year + 1) % len(rotation)],
            ),
        ]
        for year in range(num_years)
    ]
    # flatten
    return sum(holidays, [])


def lauren_rule(start_year: int, num_years: int) -> list[Place]:
    rotation = [Families.GONE, Families.GRESKO]
    holidays = [
        [
            Place(
                year=year + start_year,
                couple=Couples.LAUREN,
                holiday=Holidays.EASTER,
                family=Families.GONE,
            ),
            Place(
                year=year + start_year,
                couple=Couples.LAUREN,
                holiday=Holidays.THANKSGIVING,
                family=rotation[year % len(rotation)],
            ),
            Place(
                year=year + start_year,
                couple=Couples.LAUREN,
                holiday=Holidays.EVE,
                family=rotation[year % len(rotation)],
            ),
            Place(
                year=year + start_year,
                couple=Couples.LAUREN,
                holiday=Holidays.CHRISTMAS,
                family=rotation[year % len(rotation)],
            ),
        ]
        for year in range(num_years)
    ]
    # flatten
    return sum(holidays, [])


def our_rule(start_year: int, num_years: int, old_places: list[Place]) -> list[Place]:
    ali_places = ali_rule(start_year=start_year, num_years=num_years)
    lauren_places = lauren_rule(start_year=start_year, num_years=num_years)

    places = []

    for year in range(num_years):
        off_year = year % 2 == 0
        unused_holiday = [Holidays.CHRISTMAS, Holidays.EVE, Holidays.THANKSGIVING]
        # Get non-easter holidays of given year for Ali
        ali_holidays = [
            pl
            for pl in ali_places[year * len(Holidays) + 1 : (year + 1) * len(Holidays)]
            if pl.family != Families.GONE
        ]
        if off_year:
            # On off year, Gresko easter
            easter = Place(
                year=year + start_year,
                couple=Couples.US,
                holiday=Holidays.EASTER,
                family=Families.GRESKO,
            )
            # Set our 2 places to same as Ali's
            hol1, hol2 = ali_holidays[:2]
            hol1.couple = Couples.US
            unused_holiday.pop(unused_holiday.index(hol1.holiday))
            hol2.couple = Couples.US
            unused_holiday.pop(unused_holiday.index(hol2.holiday))
            # Remaining holiday Gresko
            rem_holiday = Place(
                year=year + start_year,
                couple=Couples.US,
                holiday=unused_holiday[0],
                family=Families.GRESKO,
            )
        else:
            ali_gone = [
                pl
                for pl in ali_places[
                    year * len(Holidays) + 1 : (year + 1) * len(Holidays)
                ]
                if pl.family == Families.GONE
            ]
            lauren_holidays = [
                pl.holiday
                for pl in lauren_places[
                    year * len(Holidays) + 1 : (year + 1) * len(Holidays)
                ]
                if pl.family != Families.GONE
            ]
            # use gresko for holiday ali gone at if lauren there, else use minimum holiday in holiday counts where lauren is there
            hol1_holiday = ali_gone[0].holiday
            hol1 = Place(
                year=year + start_year,
                couple=Couples.US,
                holiday=hol1_holiday,
                family=Families.GRESKO,
            )
            unused_holiday.pop(unused_holiday.index(hol1.holiday))
            lauren_holidays.pop(lauren_holidays.index(hol1.holiday))
            # 2nd gresko holiday is the next minimum holiday used in holiday counts
            hol2_holiday = random.choice(lauren_holidays)
            hol2 = Place(
                year=year + start_year,
                couple=Couples.US,
                holiday=hol2_holiday,
                family=Families.GRESKO,
            )
            unused_holiday.pop(unused_holiday.index(hol2.holiday))
            lauren_holidays.pop(lauren_holidays.index(hol2.holiday))
            # Remaining holiday with Ali matches holiday Ali is at that isn't taken
            rem_holiday = [pl for pl in ali_holidays if pl.holiday == unused_holiday[0]]
            rem_holiday = rem_holiday[0]
            rem_holiday.couple = Couples.US

            # Easter is the opposite family
            rem_families = [Families.PENDOLA, Families.PALOMBO]
            rem_families.pop(rem_families.index(rem_holiday.family))
            easter = Place(
                year=year + start_year,
                couple=Couples.US,
                holiday=Holidays.EASTER,
                family=rem_families[0],
            )
        places += [easter, hol1, hol2, rem_holiday]
    return places
