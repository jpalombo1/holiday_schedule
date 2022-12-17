from holidays.schedule import Scheduler
from holidays.constants import Couples, Families
from holidays.rotation import Rotation


def main() -> None:
    """Main execution function. Input sibling scheduled rotations, weights, and desired family visit distribution."""
    couple = Couples.US
    NUM_YEARS = 13
    YEAR = 2022
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
        Families.GRESKO: 0.5,
        Families.PALOMBO: 0.25,
        Families.PENDOLA: 0.25,
    }

    sib_weights = {Couples.ALI: 0.5, Couples.LAUREN: 0.5, Couples.JAMES: 0.005}

    us_schedule = Scheduler(
        couple=couple,
        num_years=NUM_YEARS,
        fam_prime_dist=fam_prim_dist,
        rotations=rotations,
        sib_weights=sib_weights,
    )
    us_schedule.schedule()
    us_schedule.results(YEAR)


if __name__ == "__main__":
    main()
