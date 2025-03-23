"""Utility functions for SmartThings."""

from .models import Program, SupportedOption

PROGRAM_COURSE = "Course"


def translate_program_course(program_course: str, set_course: bool = True) -> str:
    """Convert a program key to a translation key format (e.g. course_xx)."""

    course: str = program_course.upper()
    part: list[str] = course.split("_")
    if (ln := len(part)) == 0:
        return program_course
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
