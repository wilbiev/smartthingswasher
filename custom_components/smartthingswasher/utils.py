"""Utility functions for SmartThings."""

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
