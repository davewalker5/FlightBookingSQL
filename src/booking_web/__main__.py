import os
from booking_web.booking import app

try:
    if os.environ["FLASK_ENV"] == "development":
        app.run(debug=True, use_reloader=True)
    else:
        app.run(host="0.0.0.0")
except KeyError:
    app.run(host="0.0.0.0")
