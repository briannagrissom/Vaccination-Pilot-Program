import numpy as np
import pandas as pd
import datetime
import statsmodels.api as sm
from site_variables import site_fix


sd = pd.read_excel('Vaccination site dates (fixed).xlsx', sheet_name='Sheet2')
sd = sd.set_index('Site')
session_dates = dict()
for site in sd.index:
    session_dates[site] = []
    site_dates = sd.loc[site, sd.columns]
    for date in site_dates:
        if isinstance(date, (pd.Timestamp, datetime.datetime)):
            session_dates[site].append(date)

df = pd.read_excel('data/vaccine_master_april_final.xlsx')

# making sessions potential after enrollment variable
for idx in df.index:
    site = df.loc[idx, 'Site']
    dofv = df.loc[idx, 'date_of_first_visit']
    num_potential_sessions_after_enrollment = 0
    for date in session_dates[site]:
        if date > dofv:
            num_potential_sessions_after_enrollment = num_potential_sessions_after_enrollment + 1
    df.loc[idx, 'num_potential_sessions_after_enrollment'] = num_potential_sessions_after_enrollment

# Fixing date of first visits
site_fix_df = df[df['Site'] == site_fix]
for idx in site_fix_df.index:
    dofv = site_fix_df.loc[idx, 'date_of_first_visit']
    if dofv == pd.to_datetime('01/16/2024'):
        df.loc[idx, 'date_of_first_visit'] = pd.to_datetime('01/15/2024')
    if dofv == pd.to_datetime('05/05/2024'):
        df.loc[idx, 'date_of_first_visit'] = pd.to_datetime('05/06/2024')
    if dofv == pd.to_datetime('08/04/2024'):
        df.loc[idx, 'date_of_first_visit'] = pd.to_datetime('08/06/2024')
    if dofv == pd.to_datetime('10/13/2024'):
        df.loc[idx, 'date_of_first_visit'] = pd.to_datetime('10/06/2024')

# DEFINING POPULATIONS

df1 = df[df['time_in_program_days'] < 365]
# followed < 1 year
df2 = df[df['time_in_program_days'] >= 365]
# followed >= 1 year
total_table1 = df

df3 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == True)]
# zero-dose children followed for >= 1 year
df4 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == False)]
# previously vaccinated children followed for >= 1 year
total_table2 = df2

df5 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == True) & (df['UTD_within_1_year'] == True)]
# zero-dose children followed for >= 1 year who are UTD within 1 year
df6 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == True) & (df['UTD_within_1_year'] == False)]
# zero-dose children followed for >= 1 year who are NOT UTD within 1 year
total_table3 = df3

df7 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == False) & (df['UTD_within_1_year'] == True)]
# previously vaccinated children followed for >= 1 year who are UTD within 1 year
df8 = df[(df['time_in_program_days'] >= 365) & (df['zero_dose'] == False) & (df['UTD_within_1_year'] == False)]
# previously vaccinated children followed for >= 1 year who are NOT UTD within 1 year
total_table4 = df4

all_dfs = [df1, df2, total_table1, df3, df4, total_table2, df5, df6, total_table3, df7, df8, total_table4]
# all_dfs = [df_zd, df_p]
print('AMOUNT OF CHILDREN IN EACH POPULATION')
for idx, pop in enumerate(all_dfs):
    print(f'POPULATION {idx}: {len(pop)} children')

print('')
print('')
print('AMOUNT OF FEMALES AND MALES FOR EACH POPULATION')
print('')
for idx, pop in enumerate(all_dfs):
    num_females = len(pop[pop['Sex_'] == 'မ'])
    percentage_females = np.round(num_females / len(pop), 3) * 100
    percentage_males = 100 - percentage_females
    print(
        f'POPULATION {idx}: {num_females} ({percentage_females}%) females and {len(pop) - num_females} ({percentage_males}%) males')

print('')
print('')
print('AGE AT ENROLLMENT INFORMATION')
print('')
for idx, pop in enumerate(all_dfs):
    median = np.round(pop['age_at_first_visit'].median(), 0)
    IQR = np.quantile(pop['age_at_first_visit'], 0.75) - np.quantile(pop['age_at_first_visit'], 0.25)
    num_younger_than_1_yr = len(pop[pop['age_at_first_visit_days'] < 456])
    p_younger_than_1_yr = np.round(num_younger_than_1_yr / len(pop), 3) * 100
    num_older_than_1_yr = len(pop) - num_younger_than_1_yr
    p_older_than_1_yr = 100 - p_younger_than_1_yr
    print(f'MEDIAN AGE AT ENROLLMENT FOR POPULATION {idx}: {median} months (IQR {int(np.round(IQR, 0))})')
    print(f'AMOUNT < 1 YEAR AT ENROLLMENT FOR POPULATION {idx}: {num_younger_than_1_yr} ({p_younger_than_1_yr}%)')
    print(f'AMOUNT >= 1 YEAR AT ENROLLMENT FOR POPULATION {idx}: {num_older_than_1_yr} ({p_older_than_1_yr}%)')
print('')
print('')
print('RESIDENCE INFORMATION')
print('')
for idx, pop in enumerate(all_dfs):
    num_idps = len(pop[pop['IDP_'] == True])
    p_idps = np.round(num_idps / len(pop), 3) * 100

    num_villagers = len(pop) - num_idps
    p_villagers = 100 - p_idps

    print(f'NUMBER OF IDPS FOR POPULATION {idx}: {num_idps} ({p_idps}%)')
    print(f'NUMBER OF VILLAGERS FOR POPULATION {idx}: {num_villagers} ({p_villagers}%)')
print('')
print('')
print('SESSIONS ATTENDED AFTER ENROLLMENT INFORMATION')
print('')
for idx, pop in enumerate(all_dfs):
    median_sessions = int(np.round(pop['num_visits'].median(), 0))
    IQR = np.quantile(pop['num_visits'], 0.75) - np.quantile(pop['num_visits'], 0.25)
    print(f'MEDIAN AND IQR NUMBER OF SESSIONS ATTENDED FOR POPULATION {idx}: {median_sessions} (IQR {int(IQR)})')
print('')
print('')

print('SESSIONS POTENTIAL AFTER ENROLLMENT INFORMATION')
print('')
for idx, pop in enumerate(all_dfs):
    median_sessions_potential = int(np.round(pop['num_potential_sessions_after_enrollment'].median(), 0))
    IQR = np.quantile(pop['num_potential_sessions_after_enrollment'], 0.75) - np.quantile(
        pop['num_potential_sessions_after_enrollment'], 0.25)
    print(
        f'MEDIAN AND IQR SESSIONS POTENTIAL AFTER ENROLLMENT FOR POPULATION {idx}: {median_sessions_potential} (IQR {int(IQR)})')

print('')
print('')
print('ACCELERATED OR ROUTINE SCHEDULE INFORMATION')
print('')
for idx, pop in enumerate(all_dfs):
    num_routine = len(pop[pop['Routine'] == True])
    p_routine = np.round(a=num_routine / len(pop), decimals=3) * 100

    num_accelerated = len(pop) - num_routine
    p_accelerated = 100 - p_routine
    print(
        f'NUMBER ON ACCELERATED AND ROUTINE SCHEDULE FOR POPULATION {idx}: {num_accelerated} ACCELERATED ({p_accelerated}%) and {num_routine} ROUTINE ({p_routine}%)')




print('LOGISTIC REGRESSION')
print('')
# zero-dose children followed for >=1 year
df_15_zd = df[(df['time_in_program_days'] >= 456) & (df['zero_dose'] == True)]  # followed >= 15 months, ZD
df_15_p = df[(df['time_in_program_days'] >= 456) & (df['zero_dose'] == False)]  # followed >= 15 months, PV
zd_df = pd.get_dummies(df_15_zd, columns=['IDP_', 'Sex_', 'Routine'], drop_first=True)
prev_df = pd.get_dummies(df_15_p, columns=['IDP_', 'Sex_', 'Routine'], drop_first=True)
# X_zd = zd_df[['age_at_first_visit', 'num_visits', 'num_potential_sessions_after_enrollment', 'Routine_True']]
X_zd = zd_df[['age_at_first_visit', 'num_visits', 'num_potential_sessions_after_enrollment']]
X_zd['age_at_first_visit'] = (X_zd['age_at_first_visit'] - X_zd['age_at_first_visit'].mean()) / X_zd['age_at_first_visit'].std()
X_zd = (X_zd - X_zd.mean()) / X_zd.std()
X_zd['num_visits'] = (X_zd['num_visits'] - X_zd['num_visits'].mean()) / X_zd['num_visits'].std()
X_zd['num_potential_sessions_after_enrollment'] = (X_zd['num_potential_sessions_after_enrollment'] - X_zd['num_potential_sessions_after_enrollment'].mean()) / X_zd['num_potential_sessions_after_enrollment'].std()
X_zd = sm.add_constant(X_zd)

# X_prev = prev_df[['age_at_first_visit', 'num_visits', 'num_potential_sessions_after_enrollment', 'Routine_True']]
X_prev = prev_df[['age_at_first_visit', 'num_visits', 'num_potential_sessions_after_enrollment']]
X_prev = (X_prev - X_prev.mean()) / X_prev.std()
X_prev['age_at_first_visit'] = (X_prev['age_at_first_visit'] - X_prev['age_at_first_visit'].mean()) / X_prev['age_at_first_visit'].std()
X_prev['num_visits'] = (X_prev['num_visits'] - X_prev['num_visits'].mean()) / X_prev['num_visits'].std()
X_prev['num_potential_sessions_after_enrollment'] = (X_prev['num_potential_sessions_after_enrollment'] - X_prev['num_potential_sessions_after_enrollment'].mean()) / X_prev['num_potential_sessions_after_enrollment'].std()
X_prev = sm.add_constant(X_prev)

y_zd = zd_df['UTD_within_1_year']
y_prev = prev_df['UTD_within_1_year']

# THIS EXPLAINS ADJUSTED ODDS RATIO, WHICH IS WHAT WE'RE DOING: https://www.statology.org/adjusted-odds-ratio/
mdl_zd, mdl_prev = sm.Logit(np.asarray(y_zd), X_zd), sm.Logit(np.asarray(y_prev), X_prev)
result_zd, result_prev = mdl_zd.fit(), mdl_prev.fit()
summary_zd, summary_prev = result_zd.summary(), result_prev.summary()
print('LOGISTIC REGRESSION RESULTS FOR ZERO-DOSE CHILDREN FOLLOWED FOR >=15 MONTHS (STANDARDIZED PREDICTORS):')
print('')
# print(summary_zd)
print(f'AIC for ZD: {result_zd.aic}')
print('')
print('')
print('LOGISTIC REGRESSION RESULTS FOR PREVIOUSLY VACCINATED CHILDREN FOLLOWED FOR >=15 MONTHS (STANDARDIZED PREDICTORS):')
print('')
# print(summary_prev)
print(f'AIC for prev: {result_prev.aic}')
