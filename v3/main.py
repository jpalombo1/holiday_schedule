from pathlib import Path

from holidays.constants import Couples, Families
from holidays.funcs import export_csv, import_places, print_results
from holidays.rotation import Rotation
from holidays.schedule import Scheduler


def main() -> None:
    """Main execution function. Input sibling scheduled rotations, weights, and desired family visit distribution."""
    COUPLE = Couples.US
    NUM_YEARS = 13
    START_YEAR = 2023
    HOLIDAY_PLACES = Path(__file__).parent / "data" / "history.csv"
    HOLIDAY_OUT = Path(__file__).parent / "data" / "schedule.csv"
    rotations = {
        Couples.ALI: [
            Rotation(
                easter=Families.PALOMBO,
                thanks=Families.PALOMBO,
                eve=Families.PENDOLA,
                christmas=Families.GONE,
            ),
            Rotation(
                easter=Families.GONE,
                thanks=Families.PENDOLA,
                eve=Families.GONE,
                christmas=Families.PALOMBO,
            ),
            Rotation(
                easter=Families.PENDOLA,
                thanks=Families.GONE,
                eve=Families.PALOMBO,
                christmas=Families.PENDOLA,
            ),
        ],
        Couples.LAUREN: [
            Rotation(
                easter=Families.GONE,
                thanks=Families.GONE,
                eve=Families.GRESKO,
                christmas=Families.GRESKO,
            ),
            Rotation(
                easter=Families.GONE,
                thanks=Families.GRESKO,
                eve=Families.GONE,
                christmas=Families.GONE,
            ),
        ],
        Couples.JAMES: [
            Rotation(
                easter=Families.GRESKO,
                thanks=Families.GRESKO,
                eve=Families.GRESKO,
                christmas=Families.GRESKO,
            ),
        ],
    }
    fam_prim_dist = {
        Families.GRESKO: 0.44,
        Families.PALOMBO: 0.28,
        Families.PENDOLA: 0.28,
    }
    sib_weights = {Couples.ALI: 1.0, Couples.LAUREN: 1.0, Couples.JAMES: 0.01}
    history = import_places(HOLIDAY_PLACES)

    us_schedule = Scheduler(
        couple=COUPLE,
        start_year=START_YEAR,
        num_years=NUM_YEARS,
        fam_prime_dist=fam_prim_dist,
        rotations=rotations,
        sib_weights=sib_weights,
        history=history,
    )
    us_schedule.schedule()
    print(print_results(us_schedule.places, main_couple=COUPLE))
    export_csv(us_schedule.places, HOLIDAY_OUT)


if __name__ == "__main__":
    main()
