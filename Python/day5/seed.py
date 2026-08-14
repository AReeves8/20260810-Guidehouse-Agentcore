""" 
    Creating a tickets.json file that can be used with store.py

    Faker is a library used to crete fake data
        here it is being used to make titles that are semi-realistic and at least 6 characters

        it could also be used for tenants if you wanted
"""

import json
import random
from pathlib import Path
from faker import Faker

fake = Faker()
random.seed(11) 

# possible options to use for the seed data
PRIORITIES = ["low", "medium", "high", "urgent"]
TENANTS = ["acme-corp", "globex", "initech"]

# building n number of sample rows
def build_row(n: int) -> dict:
    return {
        "id": f"TKT-{n:04d}",
        "tenant": random.choice(TENANTS),
        "title": fake.sentence(nb_words=6).rstrip("."),
        "priority": random.choice(PRIORITIES),
    }

# adjusting the rows to purposefully include bad data
def build_fixture(count: int = 40) -> list[dict]:
    rows = [build_row(n) for n in range(1, count + 1)]

    # Plant bad rows on purpose so store.py has error tickets.
    rows[4]["priority"] = "asap"  # not in the Literal set
    rows[9]["title"] = "hi"       # below Field(min_length=5)
    del rows[14]["priority"]      # missing required field

    return rows

def main():
    fixture = build_fixture()

    # creating the path of where to write data to
    out_path = Path("data/seed-tickets.json")

    # creating the directory, if necessary
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # writing JSON data to the file
    out_path.write_text(json.dumps(fixture, indent=2), encoding="utf-8")

    print(f"wrote {len(fixture)} rows to {out_path}")


if __name__ == "__main__":
    main()
