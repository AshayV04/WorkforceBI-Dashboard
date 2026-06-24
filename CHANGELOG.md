# Changelog

All notable changes to this project are documented here.
This project follows an iterative, sprint-based delivery model.

---

## [Sprint 3] — Stakeholder Reporting & Documentation
*Focus: Communication, lineage, and audit-readiness*

### Added
- `findings_summary.md` — Stakeholder-facing report with 5 key workforce insights, data quality results, and a prioritised recommendations table. All figures sourced directly from the cleaned dataset (311 records).
- `data_dictionary.md` — Full schema reference for the `HR_Employee` table (29 columns), data lineage diagram (source → ETL → MySQL → Views → Power BI), ETL transformation log, and data quality rules reference.
- `CHANGELOG.md` — This file. Documents iterative delivery across three sprints.
- `requirements.txt` — Pinned Python dependency versions for environment reproducibility.
- `.gitignore` — Excludes environment files, checkpoints, OS artifacts, and build outputs.

### Changed
- `README.md` — Vocabulary realigned to JD-matching language: downstream reporting, self-serve BI, stakeholder-ready, ETL pipeline, data reconciliation. Added cloud migration path section and updated project files table to include new assets.

---

## [Sprint 2] — Data Modeling & Reconciliation Framework
*Focus: SQL modeling, data quality, and payroll-adjacent reporting*

### Added
- `sql/views/hr_reporting_views.sql` — Three layered SQL reporting views implementing a staging → reporting mart architecture:
  - `v_stg_employees`: Canonical staging view with derived fields (tenure, daily rate, absence cost, termination category, performance rank)
  - `v_rpt_attrition`: Department-level attrition mart (attrition rate, preventable attrition %, avg tenure at exit, absence cost)
  - `v_rpt_compensation`: Compensation mart (salary benchmarks by dept/gender, pay equity gap, payroll exposure, outlier flags)
- **Data Quality & Reconciliation Framework** (appended to `HR_Analytics.sql`) — 9 automated checks:
  1. Source-to-target row count verification (311 == 311)
  2. Primary key uniqueness (no duplicate EmpIDs)
  3. Null audit on 9 critical reporting fields
  4. Business logic: termination date after hire date
  5. Business logic: no future hire dates
  6. Salary outlier detection (> 3σ from mean)
  7. Referential integrity: ManagerID maps to valid EmpID
  8. Employment status consistency (Active ↔ termination date alignment)
  9. Reconciliation summary dashboard (single-query health check)
- **Payroll-Adjacent Reporting Queries** (appended to `HR_Analytics.sql`) — 5 payroll-framed reports:
  1. Gross pay summary by department (payroll register equivalent)
  2. Absence-adjusted cost by department (absence cost as % of payroll)
  3. Termination offboarding flag with final pay liability estimate
  4. At-risk employees (PIP / Needs Improvement) — offboarding cost forecast
  5. Gender pay equity summary (dept × gender compensation benchmarking)

---

## [Sprint 1] — Data Ingestion, ETL & Initial Analysis
*Focus: Pipeline foundation, cleaning, and exploratory reporting*

### Added
- `HRDataset_v14.csv` — Raw HR source dataset (311 employee records, 29 fields)
- `HR_Data_Cleaning.ipynb` — ETL pipeline: null imputation (ManagerID), date format standardisation, column reordering, redundant field removal. Output: `HR_Employee_Cleaned_Data.csv`
- `HR_Employee_Cleaned_Data.csv` — Canonical transformed dataset; input to all downstream systems
- `HR_Analytics.sql` — MySQL database creation (`HR_Employee_DB`), table schema definition, `LOAD DATA INFILE` import with date conversion, and initial analytical queries (salary by dept, performance distribution, turnover reasons, top earners via window function)
- `HR_Analytics_EDA.ipynb` — Exploratory Data Analysis: descriptive statistics, salary distributions, attrition trends, performance vs satisfaction correlations, recruitment source effectiveness. Visualised with Seaborn and Matplotlib
- `HR Dashboard.pbix` — Interactive Power BI dashboard connected to MySQL live data source. Multi-page with KPI cards, bar charts, pie charts, line graphs
- `HR Dashboard.pdf` — Static PDF export for offline stakeholder distribution
- `README.md` — Project documentation covering overview, workflow, problem statements, technologies, and setup instructions
