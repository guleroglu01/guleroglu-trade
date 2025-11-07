import requests, os, json
import pandas as pd

SUPPORTED_COUNTRIES = {
    "Sırbistan":"688",
    "Moldova":"498",
    "Makedonya":"807",
    "Bosna-Hersek":"070",
    "Kosova":"833",
    "Romanya":"642",
    "Hırvatistan":"191",
    "Polonya":"616",
    "Ukrayna":"804",
    "Rusya":"643",
    "Özbekistan":"860",
    "Kırgızistan":"417",
    "Gürcistan":"268",
    "Ermenistan":"051"
}

COMTRADE_PREVIEW = "https://comtradeapi.un.org/public/v1/preview"

def country_name_to_code(name):
    return SUPPORTED_COUNTRIES.get(name, "688")

def fetch_comtrade(reporter="688", period="2023", cmdCode="0805", flowCode="M", partnerCode="all"):
    params = {
        "reporterCode": reporter,
        "period": period,
        "partnerCode": partnerCode,
        "cmdCode": cmdCode,
        "flowCode": flowCode,
        "customsCode": "C00"
    }
    try:
        r = requests.get(COMTRADE_PREVIEW, params=params, timeout=25)
        if r.status_code != 200:
            return None
        data = r.json()
        if "data" not in data:
            return None
        df = pd.DataFrame(data["data"])
        if "primaryValue" in df.columns:
            df["primaryValue"] = pd.to_numeric(df["primaryValue"], errors="coerce")
        return df
    except Exception as e:
        return None

# Local firm search (demo)
SAMPLE_FIRMS_CSV = os.path.join(os.path.dirname(__file__), "sample_firms.csv")

def search_firms_local(q):
    if not os.path.exists(SAMPLE_FIRMS_CSV):
        return pd.DataFrame()
    df = pd.read_csv(SAMPLE_FIRMS_CSV)
    if not q:
        return df
    qlow = q.lower()
    mask = df.apply(lambda row: qlow in str(row["firm_name"]).lower() or qlow in str(row.get("partnerDesc","")).lower(), axis=1)
    return df[mask]

def fetch_opentradestats(country="Sırbistan", year=2023, firm_name=""):
    # Placeholder for real API; currently use local CSV
    return search_firms_local(firm_name)

# Favorites
FAV_PATH = os.path.join(os.path.dirname(__file__), "favorites.json")
def load_favorites():
    if not os.path.exists(FAV_PATH):
        return []
    try:
        return json.load(open(FAV_PATH, "r", encoding="utf-8"))
    except:
        return []

def save_favorites(obj):
    if isinstance(obj, list):
        data = obj
    else:
        data = load_favorites()
        data.append(obj)
    with open(FAV_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True
