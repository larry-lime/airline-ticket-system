def error_check_homepage(leaving_from_airport, going_to_airport, departure_date):
    error = None
    if leaving_from_airport is None:
        error = "Leaving from airport is required."
    elif going_to_airport is None:
        error = "Going to airport is required."
    elif departure_date is None:
        error = "Departure date is required."
    return error
