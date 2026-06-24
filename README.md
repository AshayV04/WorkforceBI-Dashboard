# 📊 HR Analytics Project

> **An end-to-end downstream reporting and analytics pipeline — transforming raw workforce data into self-serve BI dashboards and stakeholder-ready insights.**

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

</div>

---

<div align="center">
  <img src="https://github.com/RafiQamar/HR-Analytics-Project/blob/main/HR%20Analytics%20Dashboard.gif?raw=true" height="340" alt="HR Analytics Dashboard Preview" />
  <br/>
  <em>Self-Serve HR Analytics Dashboard — Live Preview</em>
</div>

---

## 🗂️ Table of Contents

- [Overview](#-overview)
- [Problem Statements](#-problem-statements)
- [Data Quality & Reconciliation](#-data-quality--reconciliation)
- [Project Workflow](#-project-workflow)
- [Key Insights](#-key-insights)
- [Project Files](#-project-files)
- [Technologies Used](#-technologies-used)
- [How to Run](#-how-to-run)
- [Cloud Migration Path](#️-cloud-migration-path)
- [Conclusion](#-conclusion)
- [Author](#-author)

---

## 🔍 Overview

This project implements a complete **HR analytics and downstream reporting pipeline** — covering data ingestion, transformation, quality validation, relational database integration, and self-serve BI dashboard delivery. It mirrors the structure of real-world reporting workflows used by HR Tech and People Analytics teams to surface workforce insights for Finance, HR Operations, and executive stakeholders.

| Stage | Activity | Tool |
|-------|----------|------|
| 1 | ETL — Data Cleaning & Preprocessing | Python (Pandas) |
| 2 | Relational Data Warehouse Integration | MySQL |
| 3 | Exploratory Data Analysis & Reporting | Python (Seaborn, Matplotlib) |
| 4 | Self-Serve BI Dashboard Delivery | Power BI |

---

## 🎯 Problem Statements

### 1. ETL Pipeline & Data Cleaning — `HR_Data_Cleaning.ipynb`

**Challenge:** The raw HR source dataset contained inconsistencies, missing values, and redundant columns — making it unsuitable for downstream reporting consumption.

**Solution:**
- Built a repeatable **ETL preprocessing pipeline** using Python and Pandas
- Resolved missing Manager IDs through logical hierarchical imputation
- Standardized column formats — dates converted to `datetime`, name fields normalized for consistency
- Removed redundant columns and restructured the schema to match downstream reporting requirements
- Exported the transformed dataset as `HR_Employee_Cleaned_Data.csv` — the canonical input for all downstream consumers

---

### 2. Downstream Reporting & EDA — `HR_Analytics_EDA.ipynb`

**Challenge:** Translating raw HR data into structured analytical findings that support decision-making across HR Operations, Finance, and executive stakeholders.

**Solution:**
- Developed descriptive reporting across salary, tenure, performance, and employee satisfaction dimensions
- Built visualizations using Seaborn and Matplotlib to surface trends and distributions for non-technical stakeholders
- Identified correlations between engagement, satisfaction, and turnover — translating findings into actionable narrative insights
- Structured analysis to be reusable and self-documenting — reducing manual reporting burden for downstream consumers

---

### 3. Relational Database & SQL Reporting Layer — `HR_Analytics.sql`

**Challenge:** Establishing a scalable, queryable data store to support live dashboard connectivity and on-demand operational reporting.

**Solution:**
- Designed and provisioned a structured **MySQL relational database** (`HR_Employee_DB`) with a schema optimized for reporting queries
- Authored SQL queries targeting key operational metrics: headcount by department, average salary, attrition rates, and tenure distributions
- Connected the database as a **live data source** for Power BI — enabling near real-time report refresh without manual data exports
- Applied filtering, aggregation, and join logic consistent with **data warehouse reporting patterns**

---

### 4. Self-Serve BI Dashboard — `HR Dashboard.pbix`

**Challenge:** Delivering a production-ready, interactive dashboard that enables HR Operations and Finance to self-serve workforce insights without relying on ad-hoc data requests.

**Solution:**
- Established a live **MySQL → Power BI** connection for automated data refresh
- Built a multi-page self-serve dashboard with custom DAX measures, calculated columns, and KPI cards
- Designed role-relevant views covering headcount, turnover, salary trends, and performance distributions
- Published the dashboard for web-based access — enabling stakeholder consumption without Power BI Desktop
- Dashboard is structured for **operational handoff**: clearly labeled visuals, consistent formatting, and reusable report components

---

## 🔎 Data Quality & Reconciliation

A key aspect of trustworthy downstream reporting is ensuring the data pipeline produces accurate, consistent outputs. The following data quality checks were implemented across the pipeline:

| Check | Stage | Method |
|-------|-------|--------|
| **Missing value detection & resolution** | ETL (Cleaning) | Null counts, conditional fill logic (Manager ID imputation) |
| **Duplicate record detection** | ETL (Cleaning) | `pandas.DataFrame.duplicated()` — flagged and removed duplicate rows |
| **Schema validation** | ETL → Database | Column types enforced on MySQL ingestion (dates, strings, integers) |
| **Referential integrity** | Database | Foreign key relationships between employee and manager records validated |
| **Range & outlier checks** | EDA | Salary and tenure distributions reviewed for anomalous values |
| **Source-to-target reconciliation** | ETL → Database | Row counts between source CSV and MySQL table verified to match post-import |

> These checks mirror the kind of **data reconciliation and quality validation** frameworks used in production payroll and HR reporting systems to catch discrepancies before they reach downstream consumers.

---

## 🔄 Project Workflow

```
Source System: Raw HR Dataset (HRDataset_v14.csv)
         │
         ▼
  [1] ETL: Python Data Pipeline (HR_Data_Cleaning.ipynb)
         │  ─ Null handling & imputation
         │  ─ Schema normalization
         │  ─ Duplicate removal
         │  ─ Source-to-output row reconciliation
         │  ─ Export: HR_Employee_Cleaned_Data.csv
         │
         ▼
  [2] Data Warehouse Layer: MySQL (HR_Analytics.sql)
         │  ─ Database: HR_Employee_DB
         │  ─ Schema definition & table creation
         │  ─ Bulk data import & row count validation
         │  ─ SQL reporting queries (aggregations, filters, joins)
         │
         ▼
  [3] Analytical Reporting: EDA (HR_Analytics_EDA.ipynb)
         │  ─ Descriptive statistics & trend analysis
         │  ─ Correlation analysis (satisfaction ↔ performance)
         │  ─ Stakeholder-ready visual outputs
         │
         ▼
  [4] Self-Serve BI: Power BI Dashboard (HR Dashboard.pbix)
         ─ Live MySQL connection (auto-refresh capable)
         ─ DAX measures & calculated KPIs
         ─ Multi-page stakeholder dashboard
         ─ Published for web-based self-serve access
```

---

## 💡 Key Insights

- 🔁 **Attrition by Department** — Identified departments with disproportionately high turnover rates; findings surface actionable targets for retention strategy
- 😊 **Satisfaction ↔ Performance Correlation** — Quantified the positive relationship between employee satisfaction scores and performance ratings across departments
- 💰 **Salary Benchmarking** — Surfaced salary disparities across gender and department segments for compensation equity reporting
- 🎯 **Recruitment Source Effectiveness** — Evaluated which hiring channels produce the highest-performing, longest-tenured employees — directly supporting workforce planning decisions
- 📅 **Tenure & Output** — Analyzed how years of service correlate with performance and engagement — informing HR Operations retention planning

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `HRDataset_v14.csv` | Source HR dataset — raw input to the ETL pipeline |
| `HR_Data_Cleaning.ipynb` | ETL pipeline: data cleaning, quality checks, and preprocessing |
| `HR_Employee_Cleaned_Data.csv` | Transformed dataset — canonical downstream reporting input |
| `HR_Analytics.sql` | SQL reporting layer: schema, import, 9-check reconciliation framework, and payroll-adjacent queries |
| `sql/views/hr_reporting_views.sql` | Layered SQL reporting views: staging → attrition mart → compensation mart |
| `HR_Analytics_EDA.ipynb` | Analytical reporting: EDA, trend analysis, and stakeholder visualizations |
| `HR Dashboard.pbix` | Self-serve Power BI dashboard connected to the MySQL reporting layer |
| `HR Dashboard.pdf` | Static PDF export for stakeholder distribution and offline reference |
| `findings_summary.md` | Stakeholder-facing report: data quality results, 5 key insights, and recommendations |
| `data_dictionary.md` | Schema reference, data lineage diagram, ETL transformation log, and data quality rules |
| `CHANGELOG.md` | Sprint-based delivery log documenting iterative project development |
| `requirements.txt` | Pinned Python dependency versions for environment reproducibility |

---

## 🛠️ Technologies Used

| Category | Tools & Libraries |
|----------|--------------------|
| **Language** | Python 3.x |
| **ETL & Data Manipulation** | Pandas, NumPy |
| **Data Visualization** | Matplotlib, Seaborn |
| **Relational Database** | MySQL, PyMySQL |
| **Self-Serve BI & Dashboarding** | Microsoft Power BI (DAX, live MySQL connector) |
| **Notebooks** | Jupyter |

---

## ▶️ How to Run

### Prerequisites
- Python 3.8+
- MySQL Server
- Power BI Desktop
- Jupyter Notebook

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/AshayV04/HR-Analytics-Project.git
cd HR-Analytics-Project
```

**2. Install Python dependencies**
```bash
pip install pandas matplotlib seaborn pymysql jupyter
```

**3. Run the ETL Pipeline**
- Open and run `HR_Data_Cleaning.ipynb` in Jupyter
- Output: `HR_Employee_Cleaned_Data.csv`

**4. Provision the Reporting Database**
- Execute `HR_Analytics.sql` in your MySQL client
- This creates `HR_Employee_DB`, defines the schema, and imports the cleaned dataset
- Verify: row count in MySQL should match the source CSV

**5. Run Analytical Reporting**
- Open and run `HR_Analytics_EDA.ipynb` to reproduce all trend and correlation analyses

**6. Access the Self-Serve Dashboard**
- Open `HR Dashboard.pbix` in Power BI Desktop and update MySQL credentials
- Or access the **live published dashboard** directly:

  > 🔗 [**View Live Dashboard →**](https://app.powerbi.com/view?r=eyJrIjoiNzZlNDRiY2UtNmVlOC00MzhjLTgzNzMtOGU0NTE1YmYxMjAzIiwidCI6IjZjZTcwOTA0LTUwOWMtNGI0Zi1iNjc2LTJiMGRlZjA3M2U2YyJ9)

---

## ☁️ Cloud Migration Path

This pipeline was built on a local MySQL stack. The table below maps each component to its cloud-native equivalent — showing how this architecture would scale to a cloud data platform like **Google Cloud / BigQuery**, **Azure Synapse**, or **Snowflake**.

| Current (Local) | Cloud Equivalent | Platform |
|-----------------|-----------------|----------|
| `HRDataset_v14.csv` (raw file) | Cloud Storage bucket / Azure Blob Storage | GCP / Azure |
| `HR_Data_Cleaning.ipynb` (ETL) | Cloud Dataflow / Azure Data Factory / dbt Cloud | GCP / Azure / dbt |
| `HR_Employee_Cleaned_Data.csv` | Staging table in BigQuery / Snowflake | GCP / Snowflake |
| MySQL `HR_Employee_DB` | BigQuery dataset / Azure Synapse Analytics / Snowflake schema | GCP / Azure / Snowflake |
| `sql/views/hr_reporting_views.sql` (SQL views) | dbt models (staging + mart layers) | dbt + any warehouse |
| `HR_Analytics.sql` (reconciliation) | dbt tests (`not_null`, `unique`, `accepted_values`) + Great Expectations | dbt |
| Power BI (live MySQL connection) | Looker / Connected Sheets / Power BI with Direct Lake | GCP / Azure |

**Migration would involve:**
1. Replace `LOAD DATA INFILE` with a Cloud Storage → BigQuery transfer (or dbt `source` + `seed`)
2. Convert SQL views to dbt models with `schema.yml` tests replacing manual reconciliation queries
3. Connect Power BI or Looker to the BigQuery dataset via a service account

---

## ✅ Conclusion

This project demonstrates an end-to-end **downstream HR reporting pipeline** — from raw source data ingestion through ETL transformation, relational database integration, data quality reconciliation, and final self-serve BI dashboard delivery. The workflow and tooling reflect the patterns used by real-world HR Tech and People Analytics teams to deliver accurate, scalable, and stakeholder-ready reporting.

---

## 👤 Author

**Ashay Vairat**

[![GitHub](https://img.shields.io/badge/GitHub-AshayV04-181717?style=flat-square&logo=github)](https://github.com/AshayV04)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/ashayvairat)
