from dateutil import parser


def parse_date(date_str, current_time, parsed_cache: dict, day_first=True):
    if date_str in parsed_cache.keys():  # Return cached result if available
        return parsed_cache[date_str]
    try:
        # Parse the date with dayfirst option
        parsed_date = parser.parse(date_str, dayfirst=day_first)
        date_factor = current_time - parsed_date
        days_diff = abs(date_factor.days)
        date_factor = 1 / (
                1 + days_diff / 30)  # Adding 1 to avoid division by zero and ensure recent docs have higher factor
        parsed_cache[date_str] = date_factor  # Cache the result
        return date_factor
    except ValueError:
        print(f"Could not parse date: {date_str}")
        return None
