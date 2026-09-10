# Employee View smoke execution

Executed against http://127.0.0.1:8000/ on 2026-09-09 using headless Chrome.

14 checks for 13 source cases: **9 passed, 2 failed, 3 skipped** (241.17 seconds).

- SMK-EV-003 failed: full-name search `Admin User` returns no autocomplete suggestion. The application JavaScript filters first name and last name separately.
- SMK-EV-008 failed: an unmatched query clears stale data but has no explicit no-results message.
- SMK-EV-009 skipped: requires an existing assigned member and independently known JD records.
- SMK-EV-010 skipped: requires an independently confirmed member without assignments.
- SMK-EV-012 skipped: requires a second distinct member.

All other checks passed, including both short-input variations, reset, and unauthenticated direct access. Assignment comparisons, assignment pagination, and second-member behavior remain unverified until the missing data is configured.

The source workbook's Expected Result cells are preserved. Actual Result and Status are recorded in `Employee_View_Smoke_Test_Suite.xlsx`. Detailed evidence and failed screenshots are in `../../reports/employee_view_smoke_report.html`.
