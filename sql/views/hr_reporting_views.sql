-- ==============================================================================================================
-- HR Analytics — Layered SQL Reporting Views
-- ==============================================================================================================
-- Author  : Ashay Vairat
-- Purpose : Implements a staging → reporting mart view architecture on top of the HR_Employee table.
--           This pattern mirrors dbt-style data modeling: raw table data is never queried directly
--           by consumers — instead, all downstream reports and dashboards read from typed,
--           validated, business-logic-applied views.
--
-- View Hierarchy:
--   [1] v_stg_employees     — Staging layer: clean types, derived fields, active/terminated flags
--   [2] v_rpt_attrition     — Reporting mart: attrition rates, exit reasons, dept-level retention metrics
--   [3] v_rpt_compensation  — Reporting mart: salary benchmarks, gender equity gap, outlier flags
--
-- Usage:
--   Power BI, downstream reports, and ad-hoc queries should target mart views, not the base table.
--   Mart views depend on v_stg_employees — always create/replace in order: stg → mart.
--
-- When to refresh: After every ETL load into HR_Employee (reconciliation checks must pass first).
-- ==============================================================================================================

USE HR_Employee_DB;


-- ==============================================================================================================
-- VIEW 1: v_stg_employees  (Staging Layer)
-- ==============================================================================================================
-- The canonical staging view. Adds derived fields, standardizes types, and applies business-logic
-- labels that all downstream mart views consume. No filtering of records — full employee population.
-- ==============================================================================================================

CREATE OR REPLACE VIEW v_stg_employees AS
SELECT
    -- Core identity
    EmpID,
    TRIM(Employee_Name)                                                 AS employee_name,
    TRIM(Sex)                                                           AS gender,
    MaritalDesc                                                         AS marital_status,
    TRIM(Department)                                                    AS department,
    TRIM(Position)                                                      AS job_title,

    -- Compensation
    Salary                                                              AS annual_salary,
    ROUND(Salary / 12, 2)                                              AS monthly_salary,
    ROUND(Salary / 260, 2)                                             AS daily_rate,       -- based on 260 working days/yr

    -- Employment timeline
    DateofHire                                                          AS hire_date,
    DateofTermination                                                   AS termination_date,
    DATEDIFF(COALESCE(DateofTermination, CURDATE()), DateofHire) / 365 AS tenure_years,
    YEAR(DateofHire)                                                    AS hire_year,

    -- Employment status labels
    EmploymentStatus                                                    AS employment_status,
    CASE
        WHEN EmploymentStatus = 'Active' THEN 'Active'
        ELSE 'Terminated'
    END                                                                 AS status_simplified,
    CASE
        WHEN EmploymentStatus = 'Active' THEN 0
        ELSE 1
    END                                                                 AS is_terminated,   -- binary flag for aggregations

    -- Termination context
    TermReason                                                          AS termination_reason,
    CASE
        WHEN TermReason IN ('Another position', 'more money', 'career change', 'hours',
                            'return to school', 'relocation out of area', 'unhappy')
            THEN 'Voluntary — Potentially Preventable'
        WHEN TermReason IN ('no-call, no-show', 'attendance', 'performance')
            THEN 'Involuntary — Performance/Conduct'
        WHEN TermReason = 'N/A-StillEmployed'
            THEN 'N/A — Active'
        ELSE 'Other'
    END                                                                 AS termination_category,

    -- Performance & engagement
    PerformanceScore                                                    AS performance_score,
    CASE
        WHEN PerformanceScore = 'Exceeds'           THEN 4
        WHEN PerformanceScore = 'Fully Meets'       THEN 3
        WHEN PerformanceScore = 'Needs Improvement' THEN 2
        WHEN PerformanceScore = 'PIP'               THEN 1
        ELSE NULL
    END                                                                 AS performance_rank,
    EngagementSurvey                                                    AS engagement_score,
    EmpSatisfaction                                                     AS satisfaction_score,

    -- Recruitment
    RecruitmentSource                                                   AS recruitment_source,
    CASE WHEN FromDiversityJobFairID = 1 THEN 'Yes' ELSE 'No' END      AS diversity_hire,

    -- Attendance (payroll-adjacent)
    Absences                                                            AS total_absences,
    DaysLateLast30                                                      AS days_late_last_30,
    ROUND(Absences * (Salary / 260), 2)                                AS absence_cost_usd, -- estimated pay impact of absences

    -- Management
    ManagerName                                                         AS manager_name,
    ManagerID                                                           AS manager_emp_id,

    -- Special projects
    SpecialProjectsCount                                                AS special_projects_count,
    LastPerformanceReview_Date                                          AS last_review_date

FROM HR_Employee;


-- ==============================================================================================================
-- VIEW 2: v_rpt_attrition  (Reporting Mart — Attrition & Retention)
-- ==============================================================================================================
-- Department-level attrition report. Provides the metrics needed to monitor workforce stability,
-- identify high-risk departments, and support retention planning for HR Operations.
-- Consumed by: Power BI Attrition Page, findings_summary.md, HR Operations reporting.
-- ==============================================================================================================

CREATE OR REPLACE VIEW v_rpt_attrition AS
SELECT
    department,

    -- Headcount
    COUNT(EmpID)                                                        AS total_headcount,
    SUM(CASE WHEN status_simplified = 'Active' THEN 1 ELSE 0 END)      AS active_headcount,
    SUM(is_terminated)                                                  AS total_terminations,

    -- Attrition metrics
    ROUND(
        SUM(is_terminated) * 100.0 / COUNT(EmpID), 1
    )                                                                   AS attrition_rate_pct,

    -- Voluntary vs involuntary breakdown
    SUM(CASE WHEN termination_category = 'Voluntary — Potentially Preventable'
             THEN 1 ELSE 0 END)                                         AS voluntary_terminations,
    SUM(CASE WHEN termination_category = 'Involuntary — Performance/Conduct'
             THEN 1 ELSE 0 END)                                         AS involuntary_terminations,

    -- Preventable attrition rate (key metric for retention strategy)
    ROUND(
        SUM(CASE WHEN termination_category = 'Voluntary — Potentially Preventable'
                 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(EmpID), 0), 1
    )                                                                   AS preventable_attrition_rate_pct,

    -- Tenure context
    ROUND(AVG(tenure_years), 1)                                         AS avg_tenure_years,
    ROUND(AVG(CASE WHEN is_terminated = 1 THEN tenure_years END), 1)   AS avg_tenure_at_exit_years,

    -- Engagement snapshot (active employees only)
    ROUND(AVG(CASE WHEN status_simplified = 'Active'
                   THEN engagement_score END), 2)                       AS avg_engagement_active,
    ROUND(AVG(CASE WHEN status_simplified = 'Active'
                   THEN satisfaction_score END), 2)                     AS avg_satisfaction_active,

    -- Payroll impact of absences
    SUM(absence_cost_usd)                                               AS total_absence_cost_usd,
    ROUND(AVG(total_absences), 1)                                       AS avg_absences_per_employee

FROM v_stg_employees
GROUP BY department
ORDER BY attrition_rate_pct DESC;


-- ==============================================================================================================
-- VIEW 3: v_rpt_compensation  (Reporting Mart — Compensation & Pay Equity)
-- ==============================================================================================================
-- Department × gender-level compensation benchmarking report. Surfaces salary distributions,
-- gender pay gaps, and outlier flags for compensation equity and Finance reporting.
-- Consumed by: Power BI Compensation Page, findings_summary.md, Finance / Comp team reporting.
-- ==============================================================================================================

CREATE OR REPLACE VIEW v_rpt_compensation AS
WITH dept_stats AS (
    -- Pre-compute department-level salary statistics for outlier detection
    SELECT
        department,
        AVG(annual_salary)    AS dept_avg_salary,
        STDDEV(annual_salary) AS dept_std_salary
    FROM v_stg_employees
    GROUP BY department
)
SELECT
    s.department,
    s.gender,
    s.job_title,
    s.employment_status,

    -- Headcount
    COUNT(s.EmpID)                                                      AS headcount,

    -- Salary metrics
    ROUND(AVG(s.annual_salary), 0)                                      AS avg_annual_salary,
    ROUND(MIN(s.annual_salary), 0)                                      AS min_salary,
    ROUND(MAX(s.annual_salary), 0)                                      AS max_salary,
    ROUND(STDDEV(s.annual_salary), 0)                                   AS salary_std_dev,

    -- Monthly payroll exposure (useful for Finance budget reporting)
    ROUND(SUM(s.monthly_salary), 0)                                     AS total_monthly_payroll,
    ROUND(SUM(s.annual_salary), 0)                                      AS total_annual_payroll,

    -- Absence-adjusted payroll cost
    ROUND(SUM(s.absence_cost_usd), 0)                                   AS total_absence_cost_usd,
    ROUND(SUM(s.annual_salary) + SUM(s.absence_cost_usd), 0)            AS total_adjusted_payroll_cost,

    -- Outlier flag: salary more than 2 std deviations from dept mean (for equity review)
    SUM(CASE
            WHEN ABS(s.annual_salary - d.dept_avg_salary) > 2 * d.dept_std_salary
            THEN 1 ELSE 0
        END)                                                            AS outlier_salary_count,

    -- Performance context
    ROUND(AVG(s.performance_rank), 2)                                   AS avg_performance_rank,
    SUM(CASE WHEN s.performance_score = 'Exceeds' THEN 1 ELSE 0 END)   AS exceeds_count

FROM v_stg_employees s
JOIN dept_stats d ON s.department = d.department
GROUP BY
    s.department,
    s.gender,
    s.job_title,
    s.employment_status
ORDER BY
    s.department,
    avg_annual_salary DESC;


-- ==============================================================================================================
-- VERIFICATION: Confirm all views are created and accessible
-- ==============================================================================================================

SHOW FULL TABLES IN HR_Employee_DB WHERE TABLE_TYPE = 'VIEW';

-- Quick sanity check — row counts from each view
SELECT 'v_stg_employees'  AS view_name, COUNT(*) AS row_count FROM v_stg_employees
UNION ALL
SELECT 'v_rpt_attrition'  AS view_name, COUNT(*) AS row_count FROM v_rpt_attrition
UNION ALL
SELECT 'v_rpt_compensation' AS view_name, COUNT(*) AS row_count FROM v_rpt_compensation;
