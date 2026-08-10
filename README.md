# Vaccination-Pilot-Program

Data cleaning, feature engineering, and statistical analysis code for a nurse-led childhood
vaccination program in a conflict-affected ethnic state of Myanmar.

This work contributed to the research paper
**"[Struggling to resume childhood vaccination during war in Myanmar: evaluation of a pilot program](https://link.springer.com/article/10.1186/s12939-024-02165-9)"**
(Poe A, Emily, Aurora, Aung HT, Reh ASE, **Grissom B**, Tinoo C, Fishbein DB.
*International Journal for Equity in Health*, 2024;23. DOI: 10.1186/s12939-024-02165-9. PMID 38872203, PMCID PMC11177543).

<img width="1006" height="688" alt="Screenshot 2026-08-10 at 4 01 55 PM" src="https://github.com/user-attachments/assets/98fd9b26-bcdb-40d0-b699-82c52befd675" />


## Background

After the February 2021 military coup, Myanmar's health system disintegrated and vaccine shipments
into ethnic states were blocked. After two years without childhood vaccines, a nurse-led civil
society organization built its own vaccination program, purchasing and smuggling in five vaccines
(BCG, Penta, OPV, MMR, and JE) and delivering them at monthly outreach sessions to village children
and internally displaced persons (IDPs).

The published paper is a retrospective cohort study and participatory evaluation of the **pilot**:
184 children across five monthly sessions, of whom 145 (79%) were previously unvaccinated
("zero-dose") and 71 (41%) were internally displaced. Because the program's success led to a
donor-funded expansion to ~2,000 children across many sites, this repository contains code for
**two generations of the analysis**: the original pilot notebook behind the published paper, and the
scripts used on the larger multi-site dataset from the expanded program.

## Files

### `vaccine-analysis2.ipynb` — pilot analysis (the published paper)

The end-to-end Jupyter notebook for the 184-child pilot cohort, structured in two halves:

**Cleaning & feature engineering**
- Parses the five monthly attendance columns (`Att1`–`Att5`) and dates of birth into datetimes, and
  flags census-listed children who never attended (`NO SHOW`).
- Derives the date and month of each child's first attended session, and back-calculates the child's
  age at each monthly session (`AGE_MAY15`, `AGE_JUNE15`, …) from age at enrollment.
- Builds the **previously vaccinated** flag (`PreV`) — any vaccine entry coded `P` means the child
  had received at least one dose before the program; children with none are the zero-dose group.
- Builds the **up-to-date (UTD)** flag from the Penta and Polio third-dose columns.
- Marks sessions a child did not attend with `-` so that missing attendance is never confused with a
  missed dose.

**Analysis**
- Flowchart counts reconciling the census, new attendees, attendees, and never-attendees.
- Descriptive statistics: residence/camp breakdowns (new attendees vs. census attendees vs. census
  nonattendees), age distribution (median and IQR), and sex distribution.
- **Survival analysis of vaccine uptake among previously unvaccinated children.** For each of Penta3,
  OPV3, MMR2 (`M2`), and BCG, the notebook builds an event-status array and a time-to-event array in
  months since first attendance, censoring children lost to follow-up, and restricting each analysis
  to age-eligible children (e.g. ≥2 months for Penta3/OPV3, ≥9 months for MMR2, ≤12 months for BCG).
  Kaplan–Meier estimates come from `sksurv.nonparametric.kaplan_meier_estimator`; the notebook plots
  the **inverse survival** curve `1 − S(t)`, i.e. the cumulative probability of becoming fully
  vaccinated. These are the 92% MMR / 87% Penta / 76% BCG / 68% OPV probabilities reported in the
  paper.
- Hand-implemented `calculate_probabilities` and `calculate_CI` helpers that reproduce the
  step-function estimates and normal-approximation 95% confidence intervals used in the figures.
- Percentage previously unvaccinated by two-month age band, with binomial standard errors and a
  `sklearn` linear trendline — showing that the youngest children were essentially 100% zero-dose.
- Distribution of the number of sessions attended per child, overall and by subgroup.
- Coverage by age band for BCG, full Penta, and full OPV.

### `creating_new_variables.py` — feature engineering for the expanded program

Reads the multi-site master register (`data/Master 1.10L.xlsx`, sheet `raw`), where each vaccine has
a dose-date column (`BCGD`, `Pe1D`, …, `JaED`) and a status code column (`BC_C`, `PE1C`, …, `JaEC`).
Code `1` marks a dose given *before* the program, so those dates are excluded when reconstructing
program contact. It writes `data/vaccine_master_april_final.xlsx` with:

- `date_of_first_visit`, `date_of_last_visit`, `time_enrolled` — from the sorted set of in-program
  dose dates.
- `num_visits` — distinct in-program session dates per child.
- `time_in_program` / `time_in_program_days` — first visit through the site's last session date, so
  follow-up time is measured against how long the child *could* have been observed.
- `num_potential_visits` — sessions the child's site actually held.
- `zero_dose` — no prior Penta1.
- `UTD` — up to date on Penta3, OPV3, MMR2, and JE.
- `PE3STATUS` — received Penta3 from any source.
- `age_at_first_visit` / `age_at_first_visit_days`.
- `Routine` — whether the site ran the routine or accelerated MMR schedule.
- `UTD_within_1_year` / `UTD_within_15_months` — the time-bounded outcomes, true only when the child
  is UTD *and* no qualifying dose date falls beyond 12 (or 15) months after enrollment.

It also removes six duplicate records and repairs known data-entry errors (a malformed first-visit
date, and BCG coded as refused for children too young for that to be plausible).

### `manuscript.py` — cohort tables and regression for the expanded program

Reads the engineered file above plus the per-site session calendar
(`Vaccination site dates (fixed).xlsx`) and produces the manuscript numbers:

- `num_potential_sessions_after_enrollment` — sessions held at the child's site *after* they
  enrolled, the exposure denominator for follow-up.
- Corrections to first-visit dates at one site where recorded dates were off by a few days from the
  actual session dates.
- Twelve analysis populations, stratified by follow-up (<1 year vs. ≥1 year), prior vaccination
  status (zero-dose vs. previously vaccinated), and UTD-within-1-year status, with the totals for
  each table.
- For every population: counts, sex distribution, median/IQR age at enrollment and the split above
  and below one year of age, IDP vs. village residence, median/IQR sessions attended, median/IQR
  sessions available after enrollment, and accelerated vs. routine schedule.
- Multivariable **logistic regression** (`statsmodels.Logit`) of `UTD_within_1_year`, fit separately
  for zero-dose and previously vaccinated children followed ≥15 months, with standardized predictors
  (age at enrollment, sessions attended, sessions available after enrollment) so coefficients are
  adjusted odds ratios per standard deviation.

## Data and dependencies

The register data are not in this repository — the records are identifiable child-level health data
from an active conflict zone, and both the Excel workbooks and the `site_variables.py` module that
holds site names, per-site session counts, and last session dates are kept out of version control.
The scripts therefore document the analysis rather than run standalone.

The code uses `pandas`, `numpy`, `matplotlib`, `statsmodels`, `scikit-learn`, and `scikit-survival`
(`sksurv`), and reads Excel via `openpyxl`.

