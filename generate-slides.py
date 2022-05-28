import argparse
import csv
import glob
import re

from dotenv import load_dotenv
from os import system, getenv
from os.path import exists

load_dotenv()

DATA_DIRECTORY = getenv("DATA_DIRECTORY", "sample-data")
STUDENT_LIST_FILENAME = f"{DATA_DIRECTORY}/" + getenv(
    "STUDENT_LIST_FILENAME", "student_list.csv"
)
MARKDOWN_OUTPUT_FILENAME = getenv("MARKDOWN_OUTPUT_FILENAME", "slides.md")

DIVISION_DIRECTORY = f"{DATA_DIRECTORY}/" + getenv("DIVISION_DIRECTORY", "divisions")
BABY_PHOTO_DIRECTORY = f"{DATA_DIRECTORY}/" + getenv(
    "BABY_PHOTO_DIRECTORY", "baby-photos"
)
SCHOOL_PHOTO_DIRECTORY = f"{DATA_DIRECTORY}/" + getenv(
    "SCHOOL_PHOTO_DIRECTORY", "school-photos"
)

SLIDESHOW_TITLE = getenv("SLIDESHOW_TITLE", "My Slideshow")
SLIDESHOW_SUBTITLE = getenv("SLIDESHOW_SUBTITLE", "My slideshow subtitle")


def get_student_info():
    """
    :return: A dictionary of student information, keyed by the student's full name. Note that this assumes
    that all students have unique full names.
    """
    info = {}
    with open(STUDENT_LIST_FILENAME) as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for last_name, first_name, photo in reader:
            key = f"{first_name} {last_name}"
            info[key] = {
                "first_name": first_name,
                "last_name": last_name,
                "photo": photo,
            }
    return info


def get_divisions():
    """
    :return: A dictionary with keys being division names and values being lists of student names.
    """
    filenames = glob.glob(f"{DIVISION_DIRECTORY}/*.csv")
    divisions = {}
    for filename in filenames:
        match = re.search(f"{DIVISION_DIRECTORY}/(.+).csv", filename)
        name = match.group(1)
        divisions[name] = []

        with open(filename) as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True)
            for last_name, first_name in reader:
                divisions[name].append(f"{first_name} {last_name}")

    return divisions


def generate_markdown_file():
    student_info = get_student_info()
    divisions = get_divisions()

    title_slide = f"""
---
# {SLIDESHOW_TITLE}
## {SLIDESHOW_SUBTITLE}
"""

    with open(MARKDOWN_OUTPUT_FILENAME, "w") as f:
        f.write(title_slide)
        for division_name, students in divisions.items():
            division_title_slide = f"""
---
# Division {division_name}
"""
            f.write(division_title_slide)

            for student in students:
                # See if the student has a baby picture.
                photo = student_info[student]["photo"]
                has_baby_photo = exists(f"{BABY_PHOTO_DIRECTORY}/{photo}")
                if has_baby_photo:
                    slide = f"""
---
# {student}

![]({BABY_PHOTO_DIRECTORY}/{photo})

{{.column}}

![]({SCHOOL_PHOTO_DIRECTORY}/{photo})
"""
                else:
                    slide = f"""
---
# {student}
## - 
![]({SCHOOL_PHOTO_DIRECTORY}/{photo})
"""
                f.write(slide)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id")
    parsed_args = parser.parse_args()
    slide_id = parsed_args.id

    generate_markdown_file()

    # See https://github.com/googleworkspace/md2googleslides#installation-and-usage
    # for more information about the `md2gslides` tool.
    extra_args = f"--append {slide_id} --erase" if slide_id else ""
    system(
        f"md2gslides slides.md --title '{SLIDESHOW_TITLE} - {SLIDESHOW_SUBTITLE}' --use-fileio {extra_args}"
    )
