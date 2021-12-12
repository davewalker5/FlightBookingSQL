FROM python:3.10-slim-bullseye AS runtime

COPY flightbooking-1.0.0.0 /opt/flightbooking-1.0.0.0

WORKDIR /opt/flightbooking-1.0.0.0

RUN apt-get update -y
RUN apt-get install -y wkhtmltopdf
RUN pip install -r requirements.txt
RUN pip install flight_booking_pdf_generator-1.0.0-py3-none-any.whl 
RUN pip install flight_booking_sql-1.0.0-py3-none-any.whl

ENV FLIGHT_BOOKING_DATA_FOLDER=/var/opt/flightbooking-1.0.0.0/
ENV FLIGHT_BOOKING_DB=/var/opt/flightbooking-1.0.0.0/flight_booking.db

ENTRYPOINT [ "python" ]
CMD [ "-m", "booking_web" ]
