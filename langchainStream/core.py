import requests
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class NHMQuery:
    scientific_name: Optional[str] = None
    country: Optional[str] = None
    year: Optional[str] = None
    limit: int = 20
    offset: int = 0


GBIF_OCCURRENCE_SEARCH = "https://api.gbif.org/v1/occurrence/search"
NHM_INSTITUTION_CODE = "NHMUK"


def search_nhm_occurrences(
    scientific_name=None,
    country=None,
    year=None,
    limit=20,
    offset=0
):
    params = {
        "limit": limit,
        "offset": offset,
        "institutionCode": NHM_INSTITUTION_CODE
    }

    if scientific_name:
        params["scientificName"] = scientific_name
    if country:
        params["country"] = country
    if year:
        params["year"] = year

    response = requests.get(GBIF_OCCURRENCE_SEARCH, params=params)
    response.raise_for_status()
    return response.json()


def nhm_occurrence_tool(query: NHMQuery) -> Dict[str, Any]:
    raw = search_nhm_occurrences(
        scientific_name=query.scientific_name,
        country=query.country,
        year=query.year,
        limit=query.limit,
        offset=query.offset
    )

    df = pd.DataFrame(raw.get("results", []))

    return {
        "query_used": query.__dict__,
        "record_count": raw.get("count"),
        "returned_records": len(df),
        "dataframe": df,
        "raw_response": raw
    }


def summarize_occurrences(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"summary": "No records returned"}

    summary = {"total_records": len(df)}

    if "country" in df.columns:
        summary["top_countries"] = df["country"].value_counts().head(5).to_dict()

    if "year" in df.columns:
        summary["year_range"] = {
            "min": int(df["year"].min()),
            "max": int(df["year"].max())
        }

    if "recordedBy" in df.columns:
        summary["top_collectors"] = (
            df["recordedBy"]
            .astype(str)
            .value_counts()
            .head(5)
            .to_dict()
        )

    return summary


def run_structured_query(query: NHMQuery) -> Dict[str, Any]:
    result = nhm_occurrence_tool(query)
    df = result["dataframe"]
    summary = summarize_occurrences(df)

    return {
        "applied_filters": result["query_used"],
        "gbif_total_count": result["record_count"],
        "returned_records": result["returned_records"],
        "summary": summary,
        "example_records": df
    }
