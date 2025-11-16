"""Utility functions for SmartThings."""

from typing import Any, cast

from pysmartthings import Attribute, Capability, ComponentStatus

from .const import MAIN
from .models import Program, SupportedOption

PROGRAM_COURSE = "Course"


def translate_program_course(program_course: str | None, set_course: bool = True) -> str:
    """Convert a program key to a translation key format (e.g. course_xx)."""

    if program_course is None:
        return ""
    course: str = program_course.upper()
    part: list[str] = course.split("_")
    if (ln := len(part)) == 0:
        return course
    if set_course:
        return f"{PROGRAM_COURSE}_{part[ln - 1]}"
    return part[ln - 1]


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

    return options_dict.options


def get_program_table_id(status: dict[str, ComponentStatus]) -> str:
    """Retrieve the value of the reference table ID from the status."""
    if (main_component := status.get(MAIN)) is not None and (
        main_component.get(Capability.CUSTOM_SUPPORTED_OPTIONS)
    ) is not None:
        if (capability_status:= main_component.get(Capability.CUSTOM_SUPPORTED_OPTIONS)) is not None:
            attribute_status = cast(
            dict[str, Any], capability_status[Attribute.REFERENCE_TABLE].value)
            value = str(attribute_status.get("id"))
            return value.lower()
    return ""
