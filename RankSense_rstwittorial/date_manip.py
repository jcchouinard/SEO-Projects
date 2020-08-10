import re 
import datetime
from dateutil import relativedelta
import pandas as pd


### DATE CONVERSION FUNCTIONS ###
# Convert date to a string with format YYYY-MM-DD
def date_to_str(date):
    if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
        date = datetime.datetime.strftime(date,'%Y-%m-%d')
    return date

# Convert date to a string with format YYYY-MM-DD
def str_to_date(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date,'%Y-%m-%d')
    return date

# Convert Date to YYYY-MM
def date_to_YM(date):
    dt = str_to_date(date)
    return datetime.datetime.strftime(dt,'%Y-%m')

# Convert YYYYWW to Start and End Date
def iso_to_dates(pos): # 1 for start_date, 0 for end_date
    return lambda x:datetime.datetime.strptime(str(x)+'-'+str(pos), "%G%V-%w").date()


### FUNCTIONS TO LIST DATES ###
# List dates between two dates
def list_dates(startDate,endDate):
    start_date = str_to_date(startDate)
    end_date = str_to_date(endDate)
    delta = end_date - start_date
    days = []
    for i in range(delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        days.append(date_to_str(day))
    return days

# Compare two lists to find missing dates.
def get_missing_dates(previous_dt,new_dt):
    if not previous_dt:
        dates = new_dt
    elif not new_dt:
        dates = print('No new dates to extract')
    else:
        previous_dt = set(previous_dt)
        new_dt = set(new_dt)
        ms_new_dates = list(sorted(new_dt - previous_dt))
        ms_old_date = list(sorted(previous_dt - new_dt))
        dates = list(sorted(set(ms_new_dates + ms_old_date)))
    return ms_new_dates, ms_old_date, dates

# Get last day of a specified month
def last_day_of_month(date):
    next_month = str_to_date(date).replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return date_to_str(next_month - datetime.timedelta(days=next_month.day))

# Get first and last day of a specified month
def month_start_end_dates(month,year=datetime.date.today().year):
    month = month_to_int(month)
    startDate = f'{year}-{month}-01'
    last_day = last_day_of_month(startDate)
    endDate = f'{last_day}'
    return startDate, endDate

# Get days since the beginning of the month
# If dt is not defined, use current month, else use month of the specified date.
def get_dates(chosen_date):
    print(f'Fetching start and end dates from {chosen_date}')
    today = datetime.date.today()
    days = relativedelta.relativedelta(days=3) # GSC does not permit date earlier than 3 days
    end_date = today - days  
    if chosen_date is '': 
        delta = end_date - today.replace(day=1) # Get first day of the month
        start_date = end_date - delta # count difference between end date and first day of the month
    else:
        delta = end_date - datetime.datetime.strptime(chosen_date,'%Y-%m-%d').date() # Get first day of the month
        start_date = end_date - delta # count difference between end date and first day of the month
    YM_date = date_to_YM(start_date)
    print(f'start_date: {start_date}, end_date: {end_date}')
    return YM_date, start_date, end_date

### OTHER FUNCTIONS ###
# Convert Month to a two digits str
def month_to_int(month):
    month = str(month)
    if re.search('Jan(urary)?|(0)?1', month, re.IGNORECASE):
        month = '01'
    elif re.search('Feb(urary)?|(0)?2', month, re.IGNORECASE):
        month = '02'
    elif re.search('Mar(ch)?|(0)?3', month, re.IGNORECASE):
        month = '03'
    elif re.search('Apr(il)?|(0)?4', month, re.IGNORECASE):
        month = '04'
    elif re.search('M(ay)?|(0)?5', month, re.IGNORECASE):
        month = '05'
    elif re.search('Jun(e)?|(0)?6', month, re.IGNORECASE):
        month = '06'
    elif re.search('Jul(y)?|(0)?7', month, re.IGNORECASE):
        month = '07'
    elif re.search('Aug(ust)?|(0)?8', month, re.IGNORECASE):
        month = '08'
    elif re.search('Sep(tember)?|(0)?9', month, re.IGNORECASE):
        month = '09'
    elif re.search('Oct(ober)?|10', month, re.IGNORECASE):
        month = '10'
    elif re.search('Nov(ember)?|11', month, re.IGNORECASE):
        month = '11'
    elif re.search('Dec(ember)?|12', month, re.IGNORECASE):
        month = '12'
    else: 
        return print('Not a valid Month')
    return month
