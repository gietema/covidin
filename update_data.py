from pathlib import Path
import requests
import re
import pandas as pd

URL = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"


def main():
    response = requests.get("https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv")
    save_path = Path("static") / "data" / "data"
    save_path.write_bytes(response.content)
    df = pd.read_csv(save_path, sep=";")
    # clean df
    df = df.rename(columns={col_name: col_name.lower() for col_name in df.columns})
    assert "municipality_name" in df.columns
    df = df.dropna(subset=["municipality_name"])
    # add municipality slug
    df["municipality_slug"] = df.municipality_name.apply(slugify)
    # add date
    df["date"] = pd.to_datetime(df.date_of_report).dt.date
    df["date"] = pd.to_datetime(df.date)
    # add week number
    df["week_number"] = df["date"].dt.week
    df.to_csv(str(save_path) + ".csv", index=False)


def slugify(word: str) -> str:
    return re.sub("[^a-zA-Z0-9 \n\.]", "", word).replace(" ", "").strip().lower()


if __name__ == "__main__":
    main()
