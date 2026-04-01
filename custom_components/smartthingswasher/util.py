"""Utility functions for SmartThings."""

import re

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
    ln = len(part)
    if (ln  == 0):
        return course
    if (ln == 1 and len(course) > 2):
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', program_course).lower()
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
