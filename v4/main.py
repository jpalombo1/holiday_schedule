import random
from pathlib import Path

from holidays.io import export_final_csv, import_places
from holidays.schedule import ali_rule, lauren_rule, our_rule
from holidays.stats import matches, spread_table

SEED = 49471
# SEED = random.randint(0, 1000000)
# print("seed", SEED)

INPUT_HISTORY = Path("history.csv")
YEARS_AHEAD = 13

random.seed(SEED)
old_places = import_places(INPUT_HISTORY)
next_year = max(place.year for place in old_places) + 1

ali_places = ali_rule(num_years=YEARS_AHEAD, start_year=next_year)
lauren_places = lauren_rule(num_years=YEARS_AHEAD, start_year=next_year)
our_places = our_rule(num_years=YEARS_AHEAD, start_year=next_year)
our_places.sort()

export_final_csv(our_places, ali_places, lauren_places, "schedule_all.csv")

print("Matches Us Lauren", matches(our_places, lauren_places))
print("Matches Us Ali", matches(our_places, ali_places))
print()
spread_table(our_places)
