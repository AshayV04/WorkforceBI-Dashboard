# HR Analytics — Findings Summary & Data Quality Report

> **Audience:** HR Operations, Finance, People Analytics, Executive Stakeholders
> **Prepared by:** Ashay Vairat
> **Dataset:** HRDataset_v14 — 311 employee records across 6 departments
> **Pipeline Status:** ✅ Clean — all reconciliation checks passed

---

## 📋 Table of Contents

- [Data Quality Summary](#-data-quality-summary)
- [Workforce Snapshot](#-workforce-snapshot)
- [Key Finding 1 — Attrition is Concentrated in Production](#-key-finding-1--attrition-is-concentrated-in-production)
- [Key Finding 2 — "Another Position" is the #1 Avoidable Exit Reason](#-key-finding-2--another-position-is-the-1-avoidable-exit-reason)
- [Key Finding 3 — Salary Gap by Gender](#-key-finding-3--salary-gap-by-gender)
- [Key Finding 4 — Indeed & LinkedIn Drive the Most High Performers](#-key-finding-4--indeed--linkedin-drive-the-most-high-performers)
- [Key Finding 5 — Engagement is Healthy; Absence Impact is Minimal](#-key-finding-5--engagement-is-healthy-absence-impact-is-minimal)
- [Recommendations](#-recommendations)
- [Appendix — Full Metrics Reference](#-appendix--full-metrics-reference)

---

## ✅ Data Quality Summary

Before any analysis was performed, the dataset was validated through a structured reconciliation framework. The table below documents each check and its outcome.

| # | Check | Method | Result | Status |
|---|-------|--------|--------|--------|
| 1 | **Source-to-target row count** | CSV row count vs. MySQL row count | 311 == 311 | ✅ PASS |
| 2 | **Primary key uniqueness** | Duplicate EmpID detection | 0 duplicates found | ✅ PASS |
| 3 | **Null audit on critical fields** | NULL count across 9 key columns | 0 nulls in reporting fields | ✅ PASS |
| 4 | **Termination date logic** | DateofTermination > DateofHire | 0 violations found | ✅ PASS |
| 5 | **Future hire date check** | DateofHire ≤ today | 0 future dates found | ✅ PASS |
| 6 | **Salary outlier detection** | Values > 3 std deviations from mean | 1 outlier (Executive Office — expected) | ⚠️ REVIEWED |
| 7 | **ManagerID referential integrity** | ManagerID maps to valid EmpID | 0 orphaned references | ✅ PASS |
| 8 | **Employment status consistency** | Active ↔ termination date alignment | 0 mismatches found | ✅ PASS |

> **Note on Check 6:** The Executive Office salary ($250,000) sits well above the dataset average ($69,837) but is a valid, expected data point — not an error. It was reviewed and retained.

**Conclusion:** The dataset is clean and suitable for downstream reporting. All null counts in critical fields are zero. Row counts reconcile exactly between source and target.

---

## 📊 Workforce Snapshot

| Metric | Value |
|--------|-------|
| **Total Employees (all time)** | 311 |
| **Currently Active** | 207 (66.6%) |
| **Voluntarily Terminated** | 88 (28.3%) |
| **Terminated for Cause** | 16 (5.1%) |
| **Overall Attrition Rate** | **33.4%** |
| **Average Salary (all employees)** | $69,837 |
| **Average Engagement Survey Score** | 4.11 / 5.0 |
| **Average Employee Satisfaction Score** | 3.89 / 5.0 |
| **Median Active Employee Tenure** | 12.6 years |
| **Hire Date Range** | Jan 2006 – Jul 2018 |
| **Departments** | 6 |

---

## 🔁 Key Finding 1 — Attrition is Concentrated in Production

**The Production department accounts for a disproportionate share of total turnover.**

| Department | Total Headcount | Attrition Rate |
|------------|-----------------|----------------|
| Production | 209 | **39.7%** |
| Software Engineering | 11 | 36.4% |
| Admin Offices | 9 | 22.2% |
| IT/IS | 50 | 20.0% |
| Sales | 31 | 16.1% |
| Executive Office | 1 | 0.0% |

**So what?**
Production employs 67% of the workforce but has the highest attrition rate at 39.7%. Given its size, even a 5% improvement in Production retention would reduce total turnover by ~20 employees — a material operational saving in hiring, onboarding, and productivity loss costs.

**Recommended action:** Run a targeted engagement and exit interview analysis specifically within Production to identify root causes before the next review cycle.

---

## 🚪 Key Finding 2 — "Another Position" is the #1 Avoidable Exit Reason

**The most common reason employees leave is competitive job offers — not dissatisfaction with the role itself.**

| Termination Reason | Count |
|--------------------|-------|
| Another position | 20 |
| Unhappy | 14 |
| More money | 11 |
| Career change | 9 |
| Hours | 8 |
| Attendance | 7 |
| Return to school | 5 |
| Relocation out of area | 5 |

**So what?**
"Another position" (20 exits) and "more money" (11 exits) together account for **30% of all terminations** — and both are directly addressable through compensation benchmarking and internal mobility programs. "Unhappy" (14 exits) suggests an engagement or management issue worth investigating alongside satisfaction scores.

**Recommended action:** Benchmark salaries for Production and IT/IS roles against market data annually. Introduce internal transfer pathways to retain employees seeking growth without forcing them to exit.

---

## 💰 Key Finding 3 — Salary Gap by Gender

**Male employees earn, on average, $2,842 more per year than female employees.**

| Gender | Avg. Salary | Headcount |
|--------|-------------|-----------|
| Male | $70,629 | — |
| Female | $67,787 | — |
| **Gap** | **$2,842 (4.2%)** | |

**So what?**
A 4.2% pay gap exists between male and female employees across the dataset. While this does not control for role, department, or tenure — factors that may explain part of the gap — it warrants a deeper equity analysis broken down by position and department to identify whether like-for-like compensation is equitable.

**Recommended action:** Conduct a position- and tenure-controlled salary equity analysis by department. Flag roles where the gap exceeds 5% for compensation review.

---

## 🎯 Key Finding 4 — Indeed & LinkedIn Drive the Most High Performers

**Recruitment source strongly correlates with high-performance outcomes.**

The table below shows which channels produced employees rated "Exceeds" in their performance review:

| Recruitment Source | Total Hired | "Exceeds" Performers | Exceeds Rate |
|-------------------|-------------|----------------------|--------------|
| Indeed | 87 | 12 | **13.8%** |
| LinkedIn | 76 | 9 | **11.8%** |
| Diversity Job Fair | 29 | 6 | **20.7%** |
| Employee Referral | 31 | 5 | 16.1% |
| CareerBuilder | 23 | 2 | 8.7% |
| Google Search | 49 | 2 | 4.1% |
| Website | 13 | 1 | 7.7% |

**So what?**
By raw count, Indeed and LinkedIn produce the most high performers. But **Diversity Job Fair** has the highest *rate* of "Exceeds" performers at 20.7% — making it the highest-quality channel per hire, despite lower volume. Google Search, the third-largest source by volume, has the lowest Exceeds rate at 4.1%, suggesting potential ROI concerns.

**Recommended action:** Increase Diversity Job Fair participation and Employee Referral incentives. Review Google Search spend — high volume, low quality may indicate a targeting or screening problem.

---

## 📈 Key Finding 5 — Engagement is Healthy; Absence Impact is Minimal

**Overall workforce engagement is strong, and the correlation between satisfaction and absenteeism is weaker than expected.**

| Metric | Value |
|--------|-------|
| Average Engagement Survey Score | **4.11 / 5.0** |
| Average Employee Satisfaction Score | **3.89 / 5.0** |
| Correlation: Satisfaction ↔ Absences | **+0.075** (very weak) |

**So what?**
An average engagement score of 4.11/5 is a strong result. The near-zero correlation between satisfaction and absences (+0.075) indicates that absence behavior in this dataset is driven by factors other than satisfaction — such as personal circumstances, specific managers, or role demands. This means addressing absences requires a different lever than improving satisfaction scores.

**Recommended action:** Investigate absence patterns at the manager and department level rather than treating it as a satisfaction problem. High-absence clusters in Production may benefit from schedule flexibility or workload review.

---

## 💡 Recommendations Summary

| Priority | Finding | Recommended Action | Owner |
|----------|---------|-------------------|-------|
| 🔴 High | 39.7% attrition in Production | Targeted exit interview and engagement analysis | HR Operations |
| 🔴 High | "Another position" = #1 exit reason | Annual salary benchmarking + internal mobility program | Compensation, HRBP |
| 🟡 Medium | 4.2% gender pay gap | Position-controlled equity analysis by department | Compensation |
| 🟡 Medium | Diversity Job Fair: highest Exceeds rate | Increase channel investment; reduce Google Search spend | Talent Acquisition |
| 🟢 Low | Absence ≠ satisfaction (r = 0.075) | Manager-level absence pattern analysis | HR Analytics |

---

## 📎 Appendix — Full Metrics Reference

### Department Headcount

| Department | Headcount | % of Workforce |
|------------|-----------|----------------|
| Production | 209 | 67.2% |
| IT/IS | 50 | 16.1% |
| Sales | 31 | 10.0% |
| Software Engineering | 11 | 3.5% |
| Admin Offices | 9 | 2.9% |
| Executive Office | 1 | 0.3% |

### Average Salary by Department

| Department | Avg. Salary |
|------------|-------------|
| Executive Office | $250,000 |
| IT/IS | $97,065 |
| Software Engineering | $94,989 |
| Admin Offices | $71,792 |
| Sales | $69,061 |
| Production | $59,954 |

### Performance Score Distribution

| Score | Count | % of Workforce |
|-------|-------|----------------|
| Fully Meets | 243 | 78.1% |
| Exceeds | 37 | 11.9% |
| Needs Improvement | 18 | 5.8% |
| PIP | 13 | 4.2% |

### Active Employee Tenure (Years)

| Metric | Value |
|--------|-------|
| Average | 12.8 years |
| Median | 12.6 years |
| Min | 8.0 years |
| Max | 20.5 years |

---

*This report was generated from the HR Analytics pipeline built by Ashay Vairat. Data source: HRDataset_v14.csv (311 records). All figures are based on cleaned and validated data from HR_Employee_Cleaned_Data.csv. For methodology details, see [README.md](README.md) and [HR_Analytics.sql](HR_Analytics.sql).*
