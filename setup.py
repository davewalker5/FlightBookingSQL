import setuptools

setuptools.setup(
    name="flight_booking_sql",
    version="1.0.0",
    description="Simple aircraft flight booking system",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"}
)
