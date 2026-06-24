# Create a database to store the HR Employees Data
CREATE DATABASE HR_Employee_DB;

USE HR_Employee_DB;

-- to create a table for the HR Employee data
CREATE TABLE HR_Employee(
	EmpID INT PRIMARY KEY, 
    Employee_Name VARCHAR(255),
    Sex VARCHAR(5),
    MaritalDesc VARCHAR(255),
    DeptID INT,
    FromDiversityJobFairID INT, 
    Salary DECIMAL(10, 2), 
    Position VARCHAR(255), 
    State VARCHAR(255), 
    Zip VARCHAR(255), 
    DOB DATE,
	CitizenDesc VARCHAR(255), 
    HispanicLatino VARCHAR(255), 
    RaceDesc VARCHAR(255), 
    DateofHire DATE,
	DateofTermination DATE, 
    TermReason VARCHAR(255), 
    EmploymentStatus VARCHAR(255), 
    Department VARCHAR(255),
	ManagerName VARCHAR(255), 
    ManagerID INT, 
    RecruitmentSource VARCHAR(255), 
    PerformanceScore VARCHAR(255),
	EngagementSurvey FLOAT, 
    EmpSatisfaction INT, 
    SpecialProjectsCount INT,
    LastPerformanceReview_Date DATE, 
    DaysLateLast30 INT, 
    Absences INT
    );

-- SQL scripts to import the HR Employee data into the database.
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/HR_Employee_Cleaned_Data.csv'
INTO TABLE HR_Employee
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(EmpID, Employee_Name,Sex,MaritalDesc,DeptID,FromDiversityJobFairID, Salary, Position, State, Zip, 
@DOB,CitizenDesc, HispanicLatino, RaceDesc, @DateofHire,@DateofTermination, TermReason, EmploymentStatus, 
Department, ManagerName, ManagerID, RecruitmentSource, PerformanceScore,EngagementSurvey, EmpSatisfaction, 
SpecialProjectsCount,@LastPerformanceReview_Date, DaysLateLast30, Absences)
SET 
	DOB = str_to_date(@DOB, '%m/%d/%Y'),
    DateofHire = str_to_date(@DateofHire, '%m/%d/%Y'),
    DateofTermination = NULLIF(STR_TO_DATE(NULLIF(@DateofTermination, ''), '%m/%d/%Y'), NULL),
    LastPerformanceReview_Date = str_to_date(@LastPerformanceReview_Date, '%m/%d/%Y');

-- --------------------------------------------------------------------------------------------------------------

# Sql Queries to find insights from the HR employee data

-- the average salary by department
SELECT Department, AVG(salary) AS Average_Salary
FROM HR_Employee
GROUP BY Department
ORDER BY Average_Salary DESC;

-- number of employees came from a diversity recruitment event
SELECT count(EmpID)
FROM hr_employee
WHERE FromDiversityJobFairID = 1;

-- the average salary by department
SELECT Department, AVG(salary) AS Average_Salary
FROM HR_Employee
GROUP BY Department
ORDER BY Average_Salary DESC;

-- List employees who were hired in 2012
SELECT Employee_Name, DateofHire
FROM hr_employee
WHERE YEAR(DateofHire) = 2012;

--  the number of employees in each race/ethnicity category.
SELECT RaceDesc, COUNT(EmpID) number_of_employees
FROM hr_employee
GROUP BY 1;

-- the count of male and female employees.
SELECT Sex, COUNT(EmpID) AS number_of_employees
FROM hr_employee
GROUP BY sex;

-- the number of employees based on performance score.
SELECT PerformanceScore, COUNT(EmpID) AS number_of_employees
FROM hr_employee
GROUP BY PerformanceScore;

-- list of employees who have a performance score of "Needs Improvement" or "PIP"
SELECT empID, Employee_Name, PerformanceScore
FROM hr_employee
WHERE PerformanceScore IN ("Needs Improvement", "PIP");

-- top 5 employees with highest absences who have a performance score of "Needs Improvement" or "PIP"
SELECT empID, Employee_Name, Absences
FROM hr_employee
WHERE PerformanceScore IN ("Needs Improvement", "PIP") AND EmploymentStatus = 'Active'
ORDER BY Absences DESC
LIMIT 5;

--  top 3 highest-paid employees in each department
WITH RankEmp AS (
	SELECT Department, empID, Employee_Name, Sex, MaritalDesc,Position, Salary,
	DENSE_RANK() OVER(PARTITION BY Department ORDER BY Salary DESC) AS rnk
	FROM hr_employee
)
SELECT  Department, empID, Employee_Name, Sex, MaritalDesc,Position, Salary
FROM RankEmp
WHERE rnk <=3;

-- the count of employees based on their termination reason and employment status (active or terminated).
SELECT upper(TermReason), EmploymentStatus, COUNT(*) AS EmployeeCount
FROM HR_Employee
WHERE DateofTermination IS NOT NULL
GROUP BY TermReason, EmploymentStatus;

-- ==============================================================================================================
-- DATA QUALITY & RECONCILIATION FRAMEWORK
-- ==============================================================================================================
-- Purpose : Validate the integrity and accuracy of the HR_Employee table after data ingestion.
--           These checks mirror the reconciliation logic used in production reporting pipelines
--           to catch discrepancies between source and downstream systems before they reach
--           consumers (Finance, HR Operations, dashboards).
--
-- When to run : After every LOAD DATA INFILE import, and before publishing downstream reports.
-- Expected outcome : All checks should return 0 anomaly rows. Any non-zero result requires
--                    investigation and resolution before downstream consumers are refreshed.
-- ==============================================================================================================


-- -----------------------------------------------
-- CHECK 1: Source-to-Target Row Count Verification
-- -----------------------------------------------
-- Confirms the number of records loaded matches the expected source row count.
-- The source CSV (HR_Employee_Cleaned_Data.csv) contains 311 employee records (excluding header).
-- A mismatch indicates a failed or partial load and must be resolved before reporting.

SELECT
    COUNT(*)                              AS loaded_row_count,
    311                                   AS expected_row_count,
    COUNT(*) - 311                        AS row_discrepancy,
    CASE
        WHEN COUNT(*) = 311 THEN 'PASS — Row count matches source'
        ELSE 'FAIL — Row count mismatch. Investigate load.'
    END                                   AS reconciliation_status
FROM HR_Employee;


-- -----------------------------------------------
-- CHECK 2: Primary Key Integrity — Duplicate EmpIDs
-- -----------------------------------------------
-- EmpID is the primary key and must be unique across all records.
-- This query flags any IDs that appear more than once, which would indicate
-- a data ingestion error or upstream source issue.

SELECT
    EmpID,
    COUNT(*) AS occurrence_count
FROM HR_Employee
GROUP BY EmpID
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;
-- Expected result: 0 rows returned. Any rows returned = duplicate key violation.


-- -----------------------------------------------
-- CHECK 3: Null Audit on Critical Reporting Fields
-- -----------------------------------------------
-- Checks for NULL values in fields that are essential for downstream reporting accuracy.
-- NULL in any of these columns would cause silent errors or blank cells in dashboards
-- and operational reports (e.g. salary summaries, headcount by department).

SELECT
    SUM(CASE WHEN EmpID            IS NULL THEN 1 ELSE 0 END) AS null_EmpID,
    SUM(CASE WHEN Employee_Name    IS NULL THEN 1 ELSE 0 END) AS null_Employee_Name,
    SUM(CASE WHEN Department       IS NULL THEN 1 ELSE 0 END) AS null_Department,
    SUM(CASE WHEN Salary           IS NULL THEN 1 ELSE 0 END) AS null_Salary,
    SUM(CASE WHEN EmploymentStatus IS NULL THEN 1 ELSE 0 END) AS null_EmploymentStatus,
    SUM(CASE WHEN DateofHire       IS NULL THEN 1 ELSE 0 END) AS null_DateofHire,
    SUM(CASE WHEN PerformanceScore IS NULL THEN 1 ELSE 0 END) AS null_PerformanceScore,
    SUM(CASE WHEN ManagerID        IS NULL THEN 1 ELSE 0 END) AS null_ManagerID,
    SUM(CASE WHEN RecruitmentSource IS NULL THEN 1 ELSE 0 END) AS null_RecruitmentSource
FROM HR_Employee;
-- Expected result: All columns return 0. Any non-zero value = data gap requiring upstream fix.


-- -----------------------------------------------
-- CHECK 4: Business Logic Validation — Termination Date Before Hire Date
-- -----------------------------------------------
-- A terminated employee's DateofTermination must always be after their DateofHire.
-- Records where termination precedes hire indicate a data entry error or ETL bug
-- and would corrupt attrition trend reports and tenure calculations.

SELECT
    EmpID,
    Employee_Name,
    DateofHire,
    DateofTermination,
    DATEDIFF(DateofTermination, DateofHire) AS days_employed
FROM HR_Employee
WHERE DateofTermination IS NOT NULL
  AND DateofTermination < DateofHire
ORDER BY days_employed ASC;
-- Expected result: 0 rows returned. Any rows = invalid termination dates.


-- -----------------------------------------------
-- CHECK 5: Business Logic Validation — Future Hire Dates
-- -----------------------------------------------
-- DateofHire must not be in the future. A future hire date would incorrectly
-- inflate active headcount and skew tenure calculations in operational reports.

SELECT
    EmpID,
    Employee_Name,
    DateofHire
FROM HR_Employee
WHERE DateofHire > CURDATE()
ORDER BY DateofHire DESC;
-- Expected result: 0 rows returned.


-- -----------------------------------------------
-- CHECK 6: Salary Outlier Detection
-- -----------------------------------------------
-- Identifies salary values that fall outside 3 standard deviations from the mean.
-- Extreme outliers can distort department-level salary summaries and compensation
-- equity reports. Flagged records should be validated against the source system.

WITH SalaryStats AS (
    SELECT
        AVG(Salary)    AS avg_salary,
        STDDEV(Salary) AS std_salary
    FROM HR_Employee
    WHERE Salary IS NOT NULL
)
SELECT
    e.EmpID,
    e.Employee_Name,
    e.Department,
    e.Position,
    e.Salary,
    ROUND(s.avg_salary, 2)                                  AS dataset_avg_salary,
    ROUND(ABS(e.Salary - s.avg_salary) / s.std_salary, 2)  AS std_deviations_from_mean
FROM HR_Employee e
CROSS JOIN SalaryStats s
WHERE ABS(e.Salary - s.avg_salary) > 3 * s.std_salary
ORDER BY std_deviations_from_mean DESC;
-- Expected result: 0 rows for a clean dataset. Review any flagged records with source data.


-- -----------------------------------------------
-- CHECK 7: Referential Integrity — ManagerID Self-Reference
-- -----------------------------------------------
-- Every non-null ManagerID should correspond to an EmpID that exists in the table.
-- Orphaned ManagerIDs (pointing to non-existent employees) break manager-level
-- reporting and org-chart hierarchies in the dashboard.

SELECT
    e.EmpID,
    e.Employee_Name,
    e.ManagerID,
    e.ManagerName
FROM HR_Employee e
LEFT JOIN HR_Employee m ON e.ManagerID = m.EmpID
WHERE e.ManagerID IS NOT NULL
  AND m.EmpID IS NULL
ORDER BY e.ManagerID;
-- Expected result: 0 rows returned. Any rows = orphaned ManagerID references.


-- -----------------------------------------------
-- CHECK 8: EmploymentStatus Consistency
-- -----------------------------------------------
-- Active employees must not have a DateofTermination, and terminated employees
-- must have one. Inconsistency here would cause headcount and attrition figures
-- in downstream reports to be incorrect.

SELECT
    EmploymentStatus,
    CASE
        WHEN EmploymentStatus = 'Active'     AND DateofTermination IS NOT NULL THEN 'FAIL — Active employee has termination date'
        WHEN EmploymentStatus != 'Active'    AND DateofTermination IS NULL     THEN 'FAIL — Terminated employee missing termination date'
        ELSE 'PASS'
    END AS status_check,
    COUNT(*) AS record_count
FROM HR_Employee
GROUP BY
    EmploymentStatus,
    CASE
        WHEN EmploymentStatus = 'Active'  AND DateofTermination IS NOT NULL THEN 'FAIL — Active employee has termination date'
        WHEN EmploymentStatus != 'Active' AND DateofTermination IS NULL     THEN 'FAIL — Terminated employee missing termination date'
        ELSE 'PASS'
    END
ORDER BY status_check DESC;
-- Expected result: All rows show 'PASS'. Any 'FAIL' row requires data correction.


-- -----------------------------------------------
-- CHECK 9: Reconciliation Summary Dashboard
-- -----------------------------------------------
-- A single-query summary that provides a high-level health status of the ingested dataset.
-- Useful as a quick post-load validation step before triggering downstream report refreshes.

SELECT
    COUNT(*)                                                               AS total_records,
    SUM(CASE WHEN EmploymentStatus = 'Active' THEN 1 ELSE 0 END)         AS active_employees,
    SUM(CASE WHEN EmploymentStatus != 'Active' THEN 1 ELSE 0 END)        AS terminated_employees,
    SUM(CASE WHEN Salary IS NULL THEN 1 ELSE 0 END)                      AS records_missing_salary,
    SUM(CASE WHEN Department IS NULL THEN 1 ELSE 0 END)                  AS records_missing_department,
    SUM(CASE WHEN ManagerID IS NULL THEN 1 ELSE 0 END)                   AS records_missing_managerID,
    ROUND(AVG(Salary), 2)                                                 AS avg_salary,
    MIN(DateofHire)                                                       AS earliest_hire_date,
    MAX(DateofHire)                                                       AS latest_hire_date,
    COUNT(DISTINCT Department)                                            AS distinct_departments,
    COUNT(DISTINCT RecruitmentSource)                                     AS distinct_recruitment_sources
FROM HR_Employee;
-- Run this after every load. All null counts should be 0 for a clean pipeline state.


-- ==============================================================================================================
-- PAYROLL-ADJACENT REPORTING QUERIES
-- ==============================================================================================================
-- Purpose : Demonstrates how HR data fields map to downstream payroll reporting concepts.
--           These queries mirror the type of reporting produced by Payroll Tech and HR Finance
--           teams: gross pay exposure, absence cost impact, termination offboarding flags,
--           and pay equity summaries.
--
-- Context : The HR_Employee dataset contains Salary, Absences, DaysLateLast30, and EmploymentStatus —
--           fields that directly feed payroll cost analysis, workforce budget reporting, and
--           pay run validation workflows in production payroll systems.
-- ==============================================================================================================


-- -----------------------------------------------
-- PAYROLL REPORT 1: Gross Pay Summary by Department
-- -----------------------------------------------
-- Calculates the total annual and monthly payroll exposure per department.
-- Equivalent to a department-level payroll register summary — used by Finance
-- to reconcile headcount costs against departmental budgets.

SELECT
    TRIM(Department)                        AS department,
    COUNT(EmpID)                            AS active_headcount,
    SUM(Salary)                             AS total_annual_payroll_usd,
    ROUND(SUM(Salary) / 12, 2)             AS total_monthly_payroll_usd,
    ROUND(AVG(Salary), 2)                   AS avg_annual_salary,
    ROUND(MIN(Salary), 2)                   AS min_salary,
    ROUND(MAX(Salary), 2)                   AS max_salary
FROM HR_Employee
WHERE EmploymentStatus = 'Active'
GROUP BY TRIM(Department)
ORDER BY total_annual_payroll_usd DESC;


-- -----------------------------------------------
-- PAYROLL REPORT 2: Absence-Adjusted Cost by Department
-- -----------------------------------------------
-- Estimates the payroll cost impact of employee absences using daily rate proxy.
-- Daily rate = Annual Salary / 260 working days.
-- This mirrors absence cost reporting used in payroll reconciliation to flag
-- departments with disproportionate unplanned absence spend.

SELECT
    TRIM(Department)                                        AS department,
    COUNT(EmpID)                                            AS employee_count,
    SUM(Absences)                                           AS total_absence_days,
    ROUND(AVG(Absences), 1)                                 AS avg_absences_per_employee,
    ROUND(SUM(Salary / 260 * Absences), 2)                 AS estimated_absence_cost_usd,
    ROUND(SUM(Salary), 2)                                   AS total_payroll_usd,
    ROUND(SUM(Salary / 260 * Absences) /
          NULLIF(SUM(Salary), 0) * 100, 2)                 AS absence_cost_as_pct_of_payroll
FROM HR_Employee
WHERE EmploymentStatus = 'Active'
GROUP BY TRIM(Department)
ORDER BY estimated_absence_cost_usd DESC;


-- -----------------------------------------------
-- PAYROLL REPORT 3: Termination Offboarding Flag — Final Pay Liability
-- -----------------------------------------------
-- Lists recently terminated employees and estimates final pay exposure.
-- In payroll systems, terminated employees trigger final pay runs, accrued
-- PTO payouts, and benefits offboarding. This query surfaces the population
-- for downstream payroll offboarding workflows.

SELECT
    EmpID,
    TRIM(Employee_Name)                                     AS employee_name,
    TRIM(Department)                                        AS department,
    TRIM(Position)                                          AS job_title,
    DateofTermination                                       AS termination_date,
    TermReason                                              AS termination_reason,
    EmploymentStatus                                        AS status,
    Salary                                                  AS annual_salary,
    ROUND(Salary / 260, 2)                                 AS daily_rate_usd,
    DATEDIFF(DateofTermination, DateofHire)                AS total_days_employed,
    ROUND(DATEDIFF(DateofTermination, DateofHire) / 365, 1) AS tenure_years
FROM HR_Employee
WHERE EmploymentStatus IN ('Voluntarily Terminated', 'Terminated for Cause')
  AND DateofTermination IS NOT NULL
ORDER BY DateofTermination DESC;


-- -----------------------------------------------
-- PAYROLL REPORT 4: At-Risk Employees — PIP / Needs Improvement (Active)
-- -----------------------------------------------
-- Identifies active employees currently on Performance Improvement Plans (PIP)
-- or rated Needs Improvement. In payroll systems, these employees represent
-- potential near-term termination risk — relevant for workforce budget planning
-- and proactive offboarding cost forecasting.

SELECT
    EmpID,
    TRIM(Employee_Name)                     AS employee_name,
    TRIM(Department)                        AS department,
    TRIM(Position)                          AS job_title,
    PerformanceScore                        AS performance_score,
    Salary                                  AS annual_salary,
    Absences                                AS total_absences,
    DaysLateLast30                          AS days_late_last_30,
    EngagementSurvey                        AS engagement_score,
    EmpSatisfaction                         AS satisfaction_score,
    TRIM(ManagerName)                       AS manager_name,
    LastPerformanceReview_Date              AS last_review_date
FROM HR_Employee
WHERE PerformanceScore IN ('PIP', 'Needs Improvement')
  AND EmploymentStatus = 'Active'
ORDER BY PerformanceScore, Absences DESC;


-- -----------------------------------------------
-- PAYROLL REPORT 5: Gender Pay Equity Summary
-- -----------------------------------------------
-- Calculates average salary by gender and department to surface pay equity gaps.
-- Pay equity reporting is a core compliance requirement in HR and Payroll systems,
-- directly supporting audit and SOX-adjacent workforce compensation reviews.

SELECT
    TRIM(Department)                                        AS department,
    TRIM(Sex)                                               AS gender,
    COUNT(EmpID)                                            AS headcount,
    ROUND(AVG(Salary), 2)                                   AS avg_salary,
    ROUND(MIN(Salary), 2)                                   AS min_salary,
    ROUND(MAX(Salary), 2)                                   AS max_salary
FROM HR_Employee
WHERE EmploymentStatus = 'Active'
GROUP BY TRIM(Department), TRIM(Sex)
ORDER BY TRIM(Department), avg_salary DESC;

-- Pay gap summary: male vs female average salary across all departments
SELECT
    TRIM(Sex)                                               AS gender,
    COUNT(EmpID)                                            AS total_active_headcount,
    ROUND(AVG(Salary), 2)                                   AS avg_annual_salary,
    ROUND(AVG(Salary) / 12, 2)                             AS avg_monthly_salary
FROM HR_Employee
WHERE EmploymentStatus = 'Active'
GROUP BY TRIM(Sex)
ORDER BY avg_annual_salary DESC;
