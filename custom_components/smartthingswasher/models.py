"""Models for SmartThings API."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


class STType(StrEnum):
    """Data point types."""

    BOOLEAN = "Boolean"
    ENUM = "Enum"
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


@dataclass
class Program(DataClassORJSONMixin):
    """Program model."""

    program_id: str = field(metadata=field_options(alias="cycle"))
    program_type: str = field(metadata=field_options(alias="cycleType"))
    supportedoptions: dict[SupportedOption | str, dict[ProgramOptions]]
    bubblesoak: bool


@dataclass
class ProgramOptions(DataClassORJSONMixin):
    """Program option model."""

    supportedoption: SupportedOption | str
    raw: str = field(metadata=field_options(alias="raw"))
    default: str = field(metadata=field_options(alias="default"))
    options: list[str] = field(metadata=field_options(alias="options"))
