from pathlib import Path
from typing import Dict, List

import pandas as pd  # type: ignore
from holidays.constants import Couples, Families, Holidays
from holidays.place import Place


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
        )
        for _, row in pd_csv.iterrows()
    ]


def export_final_csv(
    our_places: List[Place],
    ali_places: List[Place],
    lauren_places: List[Place],
    csv_path: Path,
) -> None:
    pd_dict: Dict[str, List[str]] = {
        "year": [],
        "holiday": [],
        "our_family": [],
        "ali_family": [],
        "lauren_family": [],
    }
    for our, ali, lauren in zip(our_places, ali_places, lauren_places):
        pd_dict["year"].append(our.year)
        pd_dict["holiday"].append(our.holiday.value)
        pd_dict["our_family"].append(our.family.value)
        pd_dict["ali_family"].append(ali.family.value)
        pd_dict["lauren_family"].append(lauren.family.value)
    pd_df = pd.DataFrame(pd_dict)
    pd_df.to_csv(csv_path, index=None)
