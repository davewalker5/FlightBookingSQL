import os
import setuptools


def find_package_files(directory, remove_root):
    """
    Walk the filesystem from the specifed directory to get a recursive list of files. Remove the start of each
    if it matches the specified removal string to leave paths relative to their containing package

    :param directory: Path to the folder to walk
    :param remove_root: Remove this if it appears at the start of a file path
    :return: A list of file paths relative to a package folder
    """
    file_paths = []
    for (path, directories, filenames) in os.walk(directory):
        # Remove the start of the path to leave the path relative to the package folder
        if path.startswith(remove_root):
            path = path[len(remove_root):]

        for filename in filenames:
            file_paths.append(os.path.join(path, filename))

    return file_paths


# The package data for the booking_web package includes the whole directory tree for the static files plus
# the Flask view templates
booking_web_package_data = find_package_files("src/booking_web/static", "src/booking_web/")
booking_web_package_data.append("templates/*.html")


setuptools.setup(
    name="flight_booking_sql",
    version="1.0.1",
    description="Simple aircraft flight booking system",
    packages=setuptools.find_packages("src"),
    include_package_data=True,
    package_dir={"": "src"},
    package_data={
        "booking_web": booking_web_package_data,
        "booking_web.airlines": ["templates/airlines/*.html"],
        "booking_web.airports": ["templates/airports/*.html"],
        "booking_web.boarding_cards": ["templates/boarding_cards/*.html"],
        "booking_web.flights": ["templates/flights/*.html"],
        "booking_web.layouts": ["templates/layouts/*.html"],
        "booking_web.passengers": ["templates/passengers/*.html"]
    }
)
