import pandas as pd
import numpy as np
from site_variables import session_count, last_date_by_site, routine_sites


df = pd.read_excel('data/Master 1.10L.xlsx', sheet_name='raw')

# date of first visit variable
date_cols = ['BCGD', 'Pe1D', 'Pe2D', 'Pe3D', 'OP1D', 'OP2D', 'OP3D', 'Ro1D', 'Ro2D', 'MM1D', 'MM2D', 'JaED']
code_cols = ['BC_C', 'PE1C', 'PE2C', 'PE3C', 'OP1C', 'OP2C', 'OP3C', 'Ro1C', 'Ro2C', 'MM1C', 'MM2C', 'JaEC']

df['DOB_'] = pd.to_datetime(df['DOB_'], errors='coerce')

for idx in df.index:
    statuses = df.loc[idx, code_cols].values
    se_da = df.loc[idx, 'SeDa']
    # statuses = np.append(statuses, 2)  # add something not equal to 1 for the "SeDa"
    visit_dates = df.loc[idx, date_cols].values
    # visit_dates = np.append(visit_dates, se_da)
    result = list(zip(statuses, visit_dates))
    timestamps = list()
    for pair in result:
        if pair[0] != 1:  # only look at dates for when the child came to the clinic, not previous vaccines
            if pd.isna(pair[1]):
                continue
            timestamps.append(pair[1])
    sorted_timestamps = sorted(timestamps)
    if len(sorted_timestamps) != 0:
        df.loc[idx, 'date_of_first_visit'] = sorted_timestamps[0]
        df.loc[idx, 'date_of_last_visit'] = sorted_timestamps[-1]
        df.loc[idx, 'time_enrolled'] = (sorted_timestamps[-1] - sorted_timestamps[0]).days / 30
    if len(sorted_timestamps) == 0:
        df.loc[idx, 'date_of_first_visit'] = 'Unknown'
        df.loc[idx, 'date_of_last_visit'] = 'Unknown'

# Number of visits variable
for idx in df.index:
    statuses = df.loc[idx, code_cols].values
    visit_dates = df.loc[idx, date_cols].values
    result = list(zip(statuses, visit_dates))
    timestamps = set()
    for pair in result:
        if pair[0] != 1:  # only look at dates for when the child came to the clinic, not previous vaccines
            if pd.isna(pair[1]):
                continue
            timestamps.add(pair[1])
    if len(timestamps) != 0:
        df.loc[idx, 'num_visits'] = len(timestamps)
    if len(timestamps) == 0:
        df.loc[idx, 'num_visits'] = 1


for site, last_date in last_date_by_site.items():
    last_date_by_site[site] = pd.to_datetime(last_date)

# Time in program variable (in months) up to July 31st and the last date of the clinic
for idx in df.index:
    statuses = df.loc[idx, code_cols].values
    site = df.loc[idx, 'Site']
    if pd.isna(site):
        df.loc[idx, 'time_in_program2'] = 'Unknown'
        continue
    visit_dates = df.loc[idx, date_cols].values
    result = list(zip(statuses, visit_dates))
    dates = list()
    for pair in result:
        if pair[0] != 1:  # Don't include previous vaccinations
            if pd.isna(pair[1]):
                continue
            dates.append(pair[1])
    sorted_dates = sorted(dates)
    if len(sorted_dates) != 0:  # sorted_dates[0] is the date of first visit
        time2 = (last_date_by_site[site] - sorted_dates[0]).days / 30
        time2_days = (last_date_by_site[site] - sorted_dates[0]).days
        df.loc[idx, 'time_in_program'] = time2
        df.loc[idx, 'time_in_program_days'] = time2_days
    if len(sorted_dates) == 0:
        df.loc[idx, 'time_in_program'] = 'Unknown'
        df.loc[idx, 'time_in_program_days'] = 'Unknown'


# Zero dose feature
def zero_dose(row):
    ZD = True
    codes = [row['PE1C']]
    if 1 in codes:
        ZD = False
    return ZD


df['zero_dose'] = df.apply(zero_dose, axis=1)

# UTD
for idx in df.index:
    statuses = df.loc[idx, ['PE3C', 'OP3C', 'MM2C', 'JaEC']].values
    if (0 in statuses) or (3 in statuses) or (4 in statuses) or (6 in statuses):
        df.loc[idx, 'UTD'] = 0
    else:
        df.loc[idx, 'UTD'] = 1

# Penta3 status
for idx in df.index:
    pe3 = df.loc[idx, 'PE3C']
    if (pe3 == 1) or (pe3 == 2) or (pe3 == 5):
        df.loc[idx, 'PE3STATUS'] = 1
    else:
        df.loc[idx, 'PE3STATUS'] = 0


# APRIL 2025 session count

for idx in df.index:
    site = df.loc[idx, 'Site']
    if pd.isna(site):
        df.loc[idx, 'num_potential_visits'] = 'Unknown'
    else:
        df.loc[idx, 'num_potential_visits'] = session_count[site]
deleted_ids = [74444, 75012, 75013, 75046, 75047, 75048]  # these records are duplicates
df = df.loc[df['ID'].isin(deleted_ids) == False]
df.loc[2550, 'time_in_program_days'] = 90
df.loc[2550, 'date_of_first_visit'] = pd.to_datetime('2024-06-06 00:00:00')
# df = df.loc[df['date_of_first_visit'] != 'Unknown', :]
df['num_potential_visits'] = df['num_potential_visits'].astype(float)
df['date_of_first_visit'] = pd.to_datetime(df['date_of_first_visit'])
df['age_at_first_visit'] = (df['date_of_first_visit'] - df['DOB_']).dt.days / 30
df['age_at_first_visit_days'] = (df['date_of_first_visit'] - df['DOB_']).dt.days
df['time_in_program_days'] = df['time_in_program_days'].astype(int)

for idx in df.index:
    bcg_code = df.loc[idx, 'BC_C']
    age = df.loc[idx, 'age_at_first_visit']
    if (bcg_code == 3) and (age < 12):
        df.loc[idx, 'BC_C'] = 0


for idx in df.index:
    site = df.loc[idx, 'Site']
    if site in routine_sites:
        df.loc[idx, 'Routine'] = True
    else:
        df.loc[idx, 'Routine'] = False



date_cols = ['Pe1D', 'Pe3D', 'Pe2D', 'OP3D', 'MM2D', 'JaED', 'OP1D', 'OP2D', 'MM1D']
# checking to see if they got UTD within 1 year of first visit
for idx in df.index:
    if df.loc[idx, 'UTD'] == 0:
        df.loc[idx, 'UTD_within_1_year'] = 0
        df.loc[idx, 'UTD_within_15_months'] = 0
        continue
    date_of_first_visit = df.loc[idx, 'date_of_first_visit']
    one_yr_later = date_of_first_visit + pd.DateOffset(months=12)
    fifteen_months_later = date_of_first_visit + pd.DateOffset(months=15)
    vaccine_dates = df.loc[idx, date_cols]
    utd_within_1_year = 1
    utd_within_15_months = 1
    for date in vaccine_dates.dropna():
        if date > one_yr_later:
            utd_within_1_year = 0
            break
    for date in vaccine_dates.dropna():
        if date > fifteen_months_later:
            utd_within_15_months = 0
            break
    df.loc[idx, 'UTD_within_1_year'] = utd_within_1_year
    df.loc[idx, 'UTD_within_15_months'] = utd_within_15_months

df.to_excel('data/vaccine_master_april_final.xlsx')

