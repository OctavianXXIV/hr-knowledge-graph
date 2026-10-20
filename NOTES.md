# Design decisions

Log of decisions that shape the graph. Each entry: decision, reason, alternative rejected.
Source: D1 exploratory analysis ([notebooks/01_eda.ipynb](notebooks/01_eda.ipynb)). All entries logged 2026-10-20 at the close of D1.

Ground truth for D5 (Cypher must reproduce these): 1470 employees, 237 leavers, 16.1% attrition.

## Identity and loading

### 1. `EmployeeNumber` is the business key
- **Decision:** `Employee` nodes are keyed by `EmployeeNumber` with a uniqueness constraint. It is an identifier, not a feature, and is never used in analysis or embeddings.
- **Reason:** 1470 unique values, no nulls, no duplicate rows (also none when ignoring the ID). IDs run 1-2068 with 598 gaps, so it is not a row index.
- **Rejected:** using the DataFrame row index as the ID, which would drift from `EmployeeNumber` after the first gap.

### 2. Load the CSV with `utf-8-sig`
- **Decision:** `pd.read_csv(..., encoding="utf-8-sig")`.
- **Reason:** the file starts with a UTF-8 BOM, which turns the first column name into `'﻿Age'`.
- **Rejected:** renaming the column after load, which hides the cause.

## Dropped columns

### 3. Drop the constants `Over18`, `StandardHours`, `EmployeeCount`
- **Decision:** drop them. Rule: keep a column only if its top-value share is below 0.95.
- **Reason:** each has one value for every employee (`'Y'`, `80`, `1`). No other column crosses 0.95 (next are `PerformanceRating` 0.85 and `Attrition` 0.84).
- **Rejected:** keeping them as properties, which adds storage and noise only.

### 4. Drop `MonthlyRate`, `DailyRate`, `HourlyRate`
- **Decision:** drop them.
- **Reason:** `DailyRate` and `HourlyRate` should be near-proportional if they describe pay, but correlations among all four pay columns are 0.03 or less in absolute value. They stay flat across `JobLevel` while `MonthlyIncome` rises from 2787 to 19192.
- **Rejected:** keeping them as properties.

## Nodes versus properties

### 5. Nodes: `Employee`, `Department`, `JobRole`
- **Decision:** only these three are nodes. Test: a value is a node only if it has an identity and relationships beyond its label.
- **Reason:** departments and roles have structure of their own (roles belong to departments, policies and managers attach to them).
- **Rejected:** "would traverse through and see who shares", which cannot separate `Department` from `Gender`.

### 6. Everything else is a property
- **Decision:** `Attrition`, `OverTime`, `BusinessTravel`, `EducationField`, `Gender`, `MaritalStatus`, `PerformanceRating`, `WorkLifeBalance` and the numeric columns (`Years*`, `PercentSalaryHike`, `TrainingTimesLastYear`, income, distance, age, and so on) are properties.
- **Reason:** nodes for these would be supernodes (84% of employees share one `Attrition` value, 85% one `PerformanceRating`, 72% one `OverTime`, 71% one `BusinessTravel`), or they are quantities that policies compare with thresholds. `EducationField` has nothing to attach beyond its label.
- **Rejected:** node-per-value for these columns.

### 7. Coded scales stay as ordinal integer properties
- **Decision:** `Education`, the satisfaction scales, `JobInvolvement`, `WorkLifeBalance`, `PerformanceRating`, `StockOptionLevel` and `JobLevel` are integer properties. Summarise with median, mode or counts per code, never the mean. `JobLevel` is treated as seniority rising 1-5 (evidence: `MonthlyIncome` rises with level). `StockOptionLevel` and `JobLevel` are documented as unlabeled in the source.
- **Reason:** the codes are ordered but not guaranteed evenly spaced. `PerformanceRating` uses only 3 and 4 although documented as 1-4.
- **Rejected:** inventing labels for `StockOptionLevel`/`JobLevel`; averaging codes.

### 8. `attrition` is stored as a boolean
- **Decision:** map `'Yes'/'No'` to a boolean at load and fail on any other value.
- **Reason:** a typo cannot create a third value, a SHACL shape can require the boolean datatype, and queries read cleaner (`WHERE e.attrition`). Counting still needs `CASE WHEN e.attrition THEN 1 ELSE 0 END`.
- **Rejected:** the string, mainly for type safety. Speed is not a reason at 1470 rows.

## Roles and hierarchy

### 9. Department-scoped `JobRole` nodes (option B)
- **Decision:** one role node per department and title (for example Sales Manager, HR Manager, R&D Manager). Keep an explicit `Employee -> Department` edge, and require exactly one per employee (the department query must return all 1470).
- **Reason:** `Manager` appears in 3 departments (11 HR, 54 R&D, 37 Sales); every other role is in exactly one. Scoping keeps `JobRole -> Department` many-to-one so a SHACL shape can enforce it.
- **Cost:** `Manager` is no longer a unique name, so a composite or synthetic key is needed (such as `"Manager|Sales"`). Statistics split into small groups (HR Manager is 11 people).
- **Rejected:** one shared `Manager` node linked to 3 departments, which makes `Employee -> JobRole -> Department` ambiguous and breaks a many-to-one shape.

### 10. `REPORTS_TO` generation rule (D3)
- **Decision:** a manager must be in the same department, have `JobRole` in {Manager, Research Director}, have a strictly higher `JobLevel` (nearest level first), and have `YearsAtCompany` >= the employee's `YearsWithCurrManager`.
- **Reason:** employees per manager come out at 4.7 (HR), 6.2 (R&D) and 11.1 (Sales), which is realistic. A strictly higher level cannot form cycles. The check found 0 employees with no candidate under the role-limited pool. Manufacturing Director is excluded: adding it drops R&D to 2.4 per manager, and 90 of its 145 people sit at level 2.
- **Rejected:** "any higher level in the department can manage" (0.3-2.9 employees per manager, so nearly everyone is a manager); including Manufacturing Director.
- **Open:** the tiebreak among equally near candidates (random, or weighted by span of control).

### 11. Level-5 employees are roots
- **Decision:** the 69 level-5 employees (HR 7, R&D 49, Sales 13; 43 Manager and 26 Research Director) have no `REPORTS_TO` edge and no invented external node. The hierarchy is a forest of 69 trees, none crossing departments. Graph-grounded answers must say "no manager data in source" for them.
- **Reason:** no real manager exists in the data; an invented node would corrupt counts like "how many managers do we have?".
- **Consequences:** there is no single top or company-wide org chart; `REPORTS_TO*` ends at level 5, at most 4 hops; rules that escalate to a manager's manager need a fallback. The whole graph stays connected through Department and JobRole edges.
- **Rejected:** a synthetic CEO or external-manager node.

## Analysis and policy

### 12. Reporting rule for attrition differences
- **Decision:** trust a group's rate only when `n >= 30` and `|difference from overall| > 1.96 * sqrt(p(1-p)/n) * 100` percentage points, with `p = 0.161`. Judge per row, not per table.
- **Reason:** a rate on 11 people means little (margin of about 22 points). `HR Manager` (n=11, 0%) is excluded and must not be reported as a finding.
- **Fragile rows:** `Sales` (+4.5 vs 3.4), `Level 5` (-8.9 vs 8.7), `R&D` (-2.3 vs 2.3, fails). `Manager`/`Research Director` and levels 4-5 describe largely the same people, so they are not independent evidence.
- **Rejected:** trusting whole tables; reading any non-trusted row as "equal to average".

### 13. Promotion-eligibility thresholds (D8)
- **Decision:** `YearsInCurrentRole >= 2` and `PerformanceRating >= 4` and `JobLevel < 5`. This selects 175 employees (11.9%, inside the 10-15% band): HR 6, R&D 115, Sales 54, at levels 1-4. The mix mirrors the workforce (HR 4.3%, R&D 65.4%, Sales 30.3%).
- **Reason:** `PerformanceRating >= 3` removes nobody, since only codes 3 and 4 exist, so it adds no criterion.
- **Rejected:** `rating >= 3`.

### 14. The "level 5 cannot be promoted" fact lives only in the rule
- **Decision:** encode it as `JobLevel < 5` in the policy, not as a property on employees.
- **Reason:** one source of truth. A derived `promotable` flag on 69 nodes duplicates the rule and can drift when it changes. Level 5 is the top of this CSV, not necessarily of the company.
- **Rejected:** a `promotable` property on level-5 employees.

## Open for D2-D4
- Relationship type and property names (`WORKS_IN`, `REPORTS_TO`, `attrition` are placeholders).
- Key format for department-scoped roles.
- Tiebreak among equally near manager candidates.
