"""Models for SmartThings API."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


class STType(StrEnum):
    """Data point types."""

    BOOLEAN = "Boolean"
    ENUM = "Enum"
    FLOAT = "Float"
    INTEGER = "Integer"
    JSON = "Json"
    RAW = "Raw"
    STRING = "String"


class SupportedOption(StrEnum):
    """SupportedCycle model."""

    BUBBLE_SOAK = "bubbleSoak"
    DRYING_LEVEL = "dryingLevel"
    DRYING_TEMPERATURE = "dryingTemperature"
    KEEP_FRESH = "keepFresh"
    RINSE_CYCLE = "rinseCycle"
    SANITIZE = "sanitize"
    SOIL_LEVEL = "soilLevel"
    SPIN_LEVEL = "spinLevel"
    WATER_TEMPERATURE = "waterTemperature"
    SELECTED_ZONE = "selectedZone"
    SPEED_BOOSTER = "speedBooster"
    ZONE_BOOSTER = "zoneBooster"
    ADD_RINSE = "addRinse"
    DRY_PLUS = "dryPlus"
    HEATED_DRY = "heatedDry"
    HIGH_TEMP_WASH = "highTempWash"
    HOT_AIR_DRY = "hotAirDry"
    MULTI_TAB = "multiTab"
    RINSE_PLUS = "rinsePlus"
    SANITIZING_WASH = "sanitizingWash"
    STEAM_SOAK = "steamSoak"
    STORM_WASH = "stormWash"
    TEMPERATURE = "temperature"
    OPERATION_TIME = "operationTime"


@dataclass
class Program(DataClassORJSONMixin):
    """Program model."""

    program_id: str = field(metadata=field_options(alias="cycle"))
    program_type: str = field(metadata=field_options(alias="cycleType"))
    supportedoptions: dict[SupportedOption | str, ProgramOptions]
    supports_start: bool = field(default=False)


@dataclass
class ProgramOptions(DataClassORJSONMixin):
    """Program option model."""

    supportedoption: SupportedOption | str
    raw: str = field(default="", metadata=field_options(alias="raw"))
    default: int | str = field(default="", metadata=field_options(alias="default"))
    options: list[str] = field(default_factory=list, metadata=field_options(alias="options"))
    selected_value: Any | None = field(default=None)
    min_value: float | None = field(default=None)
    max_value: float | None = field(default=None)
    step_value: float | None = field(default=None)
    unit: str | None = field(default=None)
