from __future__ import annotations

import itertools
from dataclasses import dataclass

# Holiday Statuses
GONE = "GONE"
Gresko = "Gresko"
Palombo = "Palombo"
Pendola = "Pendola"


@dataclass
class Year:
    """Define where holidays are for given year."""

    easter: str
    thanksgiving: str
    eve: str
    christmas: str
    year: str = "2022"


class Couple:
    """Keeps years and holiday locations for different people."""

    def __init__(self, year_holidays: list[Year], name: str = "us"):
        self.year_holidays = year_holidays
        self.num_years = len(year_holidays)
        self.name = name

    @property
    def all_holidays(self) -> list[str]:
        """Get flattened list of all holidays over all years."""
        all_holidays = []
        for year in self.year_holidays:
            all_holidays.append(
                [year.easter, year.thanksgiving, year.eve, year.christmas]
            )
        return sum(all_holidays, [])

    @property
    def non_gone(self) -> int:
        """Get count of how many holidays couple is present."""
        non_gone_count = 0
        for year in self.year_holidays:
            if year.easter is not GONE:
                non_gone_count += 1
            if year.thanksgiving is not GONE:
                non_gone_count += 1
            if year.eve is not GONE:
                non_gone_count += 1
            if year.christmas is not GONE:
                non_gone_count += 1
        return non_gone_count

    @property
    def all_holidays_minus_easter(self) -> list[str]:
        """Get flattened list of all holidays minus easter over all years."""
        all_holidays = []
        for year in self.year_holidays:
            all_holidays.append([year.thanksgiving, year.eve, year.christmas])
        return sum(all_holidays, [])

    @property
    def all_print_excl_easter(self) -> list[str]:
        """Get printed list of all holidays minus easter replaced by blank over all years."""
        all_holidays = []
        for year in self.year_holidays:
            all_holidays.append(["", year.thanksgiving, year.eve, year.christmas])
        return sum(all_holidays, [])

    def common_all(self, couple: Couple) -> int:
        """Get number of common gatherings between 2 couples."""
        l1 = self.all_holidays
        l2 = couple.all_holidays
        return sum(x == y for x, y in zip(l1, l2))

    def common_all_minus_easter(self, couple: Couple) -> int:
        """Get number of common gatherings minus easter between 2 couples."""
        l1 = self.all_holidays_minus_easter
        l2 = couple.all_holidays_minus_easter
        return sum(x == y for x, y in zip(l1, l2))


class Rotation:
    """Holds possible rotations for main couple when compared to other couple schedule."""

    def __init__(self, possible_rot: list[str], use_easter: bool = True):
        self.possible = possible_rot
        self.all_rotations: list[list[str]] = list(
            itertools.permutations(self.possible)  # type: ignore
        )
        self.use_easter = use_easter

    def rotate(self, li: list[str], amount: int, left: bool = True) -> list[str]:
        """Rotate list by given number of elements in set direction."""
        rotate_by = amount % len(li)
        rotate_by = rotate_by if left else rotate_by * -1
        return list(li[rotate_by:] + li[:rotate_by])

    @property
    def filter_rotations(self) -> list[list[str]]:
        """Filter out possible rotations, only include ones non consecutive same values."""
        new_rotations = []
        for rotation in self.all_rotations:
            pass_val = False
            for val1, val2 in zip(rotation, rotation[1:]):
                if val1 == val2:
                    pass_val = True
                    break
            rot_once = self.rotate(rotation, 1)
            for val1, val2 in zip(rot_once, rot_once[1:]):
                if val1 == val2:
                    pass_val = True
                    break
            if not pass_val:
                new_rotations.append(rotation)
        return new_rotations

    def modified_rotation(
        self,
        ours: Couple,
        couple: Couple,
        target_families: list[str] = [Pendola, Palombo],
    ) -> Couple:
        """Modify our rotation compared to couple so that if on 2 given holidays, if target families are swapped, swap back to match"""
        for our_year, their_year in zip(ours.year_holidays, couple.year_holidays):
            our_year_dict = our_year.__dict__
            their_year_dict = their_year.__dict__
            ours_swaps = {val: key for key, val in our_year_dict.items()}
            our_holidays = [ours_swaps[family] for family in target_families]
            for hol, other_val in zip(our_holidays, target_families[::-1]):
                if their_year_dict[hol] == other_val:
                    setattr(our_year, hol, other_val)
        return ours

    def best_rotation(self, couples: list[Couple]) -> tuple[int, Couple]:
        """Find optimal rotation that best matches given couple schedule, return couple for given rotation."""
        max_num = 0
        max_couple = couples[0]
        for rotation in self.filter_rotations:
            # try left and right rotations
            for orient in [-1, 1]:
                # Set couple to given intital orientation then rotate through one element at a time for given number of years
                us = Couple(
                    [
                        Year(*self.rotate(rotation, i * orient), str(2022 + i))  # type: ignore
                        for i in range(couples[0].num_years)
                    ]
                )
                common_num = sum([us.common_all(couple) for couple in couples])
                if not self.use_easter:
                    common_num = sum(
                        [us.common_all_minus_easter(couple) for couple in couples]
                    )
                if common_num > max_num:
                    max_num = common_num
                    max_couple = us

        max_couple = self.modified_rotation(max_couple, couples[0])
        max_num = sum([max_couple.common_all(couple) for couple in couples])
        if not self.use_easter:
            max_num = sum(
                [max_couple.common_all_minus_easter(couple) for couple in couples]
            )
        return max_num, max_couple


def main():
    # All possible orders, filter out consecutive Greskos
    our_possible = [Gresko, Gresko, Palombo, Pendola]
    use_easter = True
    rotations = Rotation(our_possible, use_easter)

    # Other siblings to compare
    ali = Couple(
        [
            # Year(Pendola,GONE,Palombo,Pendola),
            Year(Palombo, Palombo, Pendola, GONE),
            Year(GONE, Pendola, GONE, Palombo),
            Year(Pendola, GONE, Palombo, Pendola),
        ]
        * 4,
        "ali",
    )

    # ali = Couple(
    #     [
    #         Year(Palombo, GONE, Pendola, GONE),
    #         Year(GONE, Pendola, GONE, Palombo),
    #         Year(Pendola, GONE, Palombo, GONE),
    #         Year(GONE, Palombo, GONE, Pendola),
    #     ] * 3,
    #     "ali"
    # )
    print("Ali schedule")
    print("\n".join(ali.all_holidays))

    lauren = Couple(
        [
            # Year(GONE,Gresko,Gresko,Gresko),
            # Year(GONE, GONE, GONE, GONE)
            Year(GONE, GONE, Gresko, Gresko),
            Year(GONE, Gresko, GONE, GONE),
            Year(GONE, GONE, Gresko, Gresko),
            Year(GONE, Gresko, GONE, GONE),
        ]
        * 3,
        "lauren",
    )
    print("Lauren schedule 1")
    print("\n".join(lauren.all_holidays))

    lauren_2 = Couple(
        [
            # Year(GONE,Gresko,Gresko,Gresko),
            # Year(GONE, GONE, GONE, GONE),
            Year(GONE, Gresko, GONE, GONE),
            Year(GONE, GONE, Gresko, Gresko),
            Year(GONE, Gresko, GONE, GONE),
            Year(GONE, GONE, Gresko, Gresko),
        ]
        * 3,
        "lauren2",
    )
    print("Lauren schedule 2")
    print("\n".join(lauren_2.all_holidays))

    max_ali_num, max_ali = rotations.best_rotation([ali])
    max_lauren_num, max_lauren = rotations.best_rotation([lauren])
    max_total_num, max_total = rotations.best_rotation([ali, lauren])

    print(max_total.year_holidays)

    print("Ali Optimal schedule, matching =", max_ali_num, "out of", ali.non_gone)
    print(
        "\n".join(max_ali.all_holidays if use_easter else max_ali.all_print_excl_easter)
    )
    print(
        "Lauren Optimal schedule, matching =", max_lauren_num, "out of", lauren.non_gone
    )
    print(
        "\n".join(
            max_lauren.all_holidays if use_easter else max_lauren.all_print_excl_easter
        )
    )
    print(
        "Our Optimal schedule, matching =",
        max_total_num,
        "out of",
        ali.non_gone + lauren.non_gone,
    )
    print(
        "\n".join(
            max_total.all_holidays if use_easter else max_total.all_print_excl_easter
        )
    )


if __name__ == "__main__":
    main()
