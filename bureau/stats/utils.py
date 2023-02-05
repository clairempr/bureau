import statistics


def get_ages_at_death(employees):
    """
    Calculate approximate age at death for employees
    Assumes that they have a birth year and death year filled
    """
    return list(map(lambda x: x.age_at_death(), employees))


def get_ages_in_year(employees, year):
    """
    Calculate approximate ages for employees in the given year
    Assumes that they have a birth year filled
    """
    return list(map(lambda x: x.calculate_age(year), employees))


def get_mean(data):
    """
    Return the mean of the data, or 0 if there is no data
    """
    return statistics.mean(data) if data else 0


def get_median(data):
    """
    Return the median of the data, or 0 if there is no data
    """
    return statistics.median(data) if data else 0


def get_percent(part, total):
    """
    Return the percentage that part is of total and multiply by 100
    If total is 0, return 0
    """
    return (part / total) * 100 if part and total else 0
