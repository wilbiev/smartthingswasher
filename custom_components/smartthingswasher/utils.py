"""Utility functions for SmartThings."""

from pysmartthings import Attribute, Capability, ComponentStatus

from .const import MAIN
from .models import Program, SupportedOption

PROGRAM_COURSE = "Course"


def translate_program_course(program_course: str, set_course: bool = True) -> str:
    """Convert a program key to a translation key format (e.g. course_xx)."""

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
    if (main_component := status.get(MAIN)) is None or (
        main_component.get(Capability.CUSTOM_SUPPORTED_OPTIONS)
    ) is None:
        return ""
    return (
        status[MAIN][Capability.CUSTOM_SUPPORTED_OPTIONS][Attribute.REFERENCE_TABLE]
        .value["id"]
        .lower()
    )
