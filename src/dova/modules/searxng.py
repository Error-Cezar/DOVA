from typing import Literal, Optional
from pydantic import BaseModel
import requests

api_endpoint = "http://localhost:8080"


class SearchResult(BaseModel):
    title: str
    url: str
    content: Optional[str] = None
    publishdDate: Optional[str] = None
    thumbnail: Optional[str] = None
    engine: str
    template: str
    parsed_url: Optional[list] = None
    img_src: str
    priority: str
    engines: list
    positions: list
    score: float
    category: str


class SearchResponse(BaseModel):
    query: str
    number_of_results: int = 0
    results: list[SearchResult] = []

TimeRange = Literal["all", "day", "week", "month", "year"]
Category = Literal["general", "images", "videos", "news", "map", "music", "it", "science", "files", "social_media"]
Language = Literal[
    "auto", "af", "ar", "ar-SA", "be", "bg", "bg-BG", "ca", "cs", "cs-CZ", "cy", "da", "da-DK",
    "de", "de-AT", "de-BE", "de-CH", "de-DE", "el", "el-GR", "en", "en-AU", "en-CA",
    "en-GB", "en-IE", "en-IN", "en-NZ", "en-PH", "en-PK", "en-SG", "en-US", "en-ZA",
    "es", "es-AR", "es-CL", "es-CO", "es-ES", "es-MX", "es-PE", "et", "et-EE", "eu",
    "fa", "fi", "fi-FI", "fr", "fr-BE", "fr-CA", "fr-CH", "fr-FR", "ga", "gd", "gl",
    "he", "hi", "hr", "hu", "hu-HU", "id", "id-ID", "is", "it", "it-CH", "it-IT",
    "ja", "ja-JP", "kn", "ko", "ko-KR", "lt", "lv", "ml", "mr", "nb", "nb-NO", "nl",
    "nl-BE", "nl-NL", "pl", "pl-PL", "pt", "pt-BR", "pt-PT", "ro", "ro-RO", "ru",
    "ru-RU", "sk", "sl", "sq", "sv", "sv-SE", "ta", "te", "th", "th-TH", "tr", "tr-TR",
    "uk", "ur", "vi", "vi-VN", "zh", "zh-CN", "zh-HK", "zh-TW"
]

def search(query: str,
language: Optional[Language] = "auto",
categories: Optional[Category] = "general",
page: Optional[int] = 1,
time_range: Optional[TimeRange] = "all",
max_results: Optional[int] = None) -> SearchResponse | str:
    params = {
        "q": query,
        "format": "json",
        "language": language,
        "categories": categories,
        "page": page,
        "time_range": "" if time_range == "all" else time_range,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            f"{api_endpoint}/search", params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        return SearchResponse(
            query=query,
            number_of_results=results["number_of_results"],
            results=results["results"][:max_results]
        )

    except requests.exceptions.RequestException as e:
        print(f"Error during search: {e}")
        return "Query failed: " + str(e)
