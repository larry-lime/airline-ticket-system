def error_check_search(leaving_from_airport, going_to_airport, departure_date):
    error = None
    if leaving_from_airport is None:
        error = "Leaving from airport is required."
    elif going_to_airport is None:
        error = "Going to airport is required."
    elif departure_date is None:
        error = "Departure date is required."
    return error

def error_check_update_graph(start_date, end_date):
    error = None
    if start_date == "":
        error = "Start date is required."
    elif end_date == "":
        error = "End date is required."
    return error
