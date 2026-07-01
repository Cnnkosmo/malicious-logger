from __future__ import annotations

from datetime import datetime 
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class URLHausRecord(BaseModel):
    urlhaus_id: int
    date_added: datetime
    url: str
    url_status: Literal["online", "offline"]
    last_online: datetime | None
    threat: str
    tags: list[str]
    urlhaus_link: str
    reporter: str

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v: str) -> list[str]:
        if not v or v == "None":
            return []
        return [tag.strip() for tag in v.split(",") if tag.strip() and tag.strip() != "None"]

    @field_validator("last_online", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str) -> str | None:
        return None if v == "" else v


class AlienVaultRecord(BaseModel):
    address: str
    reliability: int
    risk: int
    threat_type: str
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None

    @model_validator(mode="before")
    @classmethod
    def parse_coords(cls, data: dict) -> dict:
        coords: str = data.get("coords", "")
        if coords:
            parts = coords.split(",")
            if len(parts) == 2:
                data["latitude"]  = float(parts[0])
                data["longitude"] = float(parts[1])
        data.setdefault("latitude",  None)
        data.setdefault("longitude", None)
        return data

    @field_validator("country", "city", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str) -> str | None:
        return None if v == "" else v


class OpenPhishRecord(BaseModel):
    url: str = Field(min_length=1)
