"""Utility functions for SmartThings."""

import re

from pysmartthings import Attribute, Capability, ComponentStatus

from .const import DISHWASHER_COURSE_TO_HA, MAIN
from .models import Program, SupportedOption

PROGRAM_COURSE = "Course"
HA_TO_DISHWASHER_COURSE = {value: key for key, value in DISHWASHER_COURSE_TO_HA.items()}


def translate_program_course(program_course: str | None) -> str:
    """Convert a program key to a translation key format (e.g. course_xx)."""

    if not program_course:
        return ""

    if program_course in DISHWASHER_COURSE_TO_HA:
        return DISHWASHER_COURSE_TO_HA[program_course]

    if "_" not in program_course and len(program_course) > 2:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', program_course).lower()

    last_part = program_course.split("_")[-1].lower()
    return f"{PROGRAM_COURSE}_{last_part}".lower()


def command_program_course(program_course: str) -> str:
    """Convert a translation key back to a SmartThings program ID."""
    if not program_course:
        return ""

    if program_course in HA_TO_DISHWASHER_COURSE:
        return HA_TO_DISHWASHER_COURSE[program_course]

    prefix = f"{PROGRAM_COURSE}_".lower()
    if program_course.startswith(prefix):
        last_part = program_course[len(prefix):].upper()
        return f"{PROGRAM_COURSE}_{last_part}"

    if "_" in program_course:
        words = program_course.split("_")
        return words[0] + "".join(word.capitalize() for word in words[1:])

    return program_course


def get_program_options(
    programs: dict[str, Program], program_id: str, supported_option: SupportedOption
) -> list[str] | None:
    """Retrieve the options value from the Program dictionary based on program_id and supported_option."""
    program = programs.get(program_id)
    if not program:
        return None

    options_dict = program.supportedoptions.get(supported_option)
    if not options_dict:
        return None

    return [str(opt) for opt in options_dict.options]


def get_program_table_id(status: dict[str, ComponentStatus]) -> str:
    """Retrieve the value of the reference table ID from the status."""
    main_component = status.get(MAIN)
    if not main_component:
        return ""

    capability_status = main_component.get(Capability.CUSTOM_SUPPORTED_OPTIONS)
    if not capability_status:
        return ""

    attribute_status = capability_status.get(Attribute.REFERENCE_TABLE)
    if not attribute_status or not attribute_status.value:
        return ""

    if isinstance(attribute_status.value, dict):
        table_id = str(attribute_status.value.get("id", ""))
        return table_id.lower()

    return ""
