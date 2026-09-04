# Assign JD to Team Sanity Test Suite

| ID | Scenario | Preconditions | Expected Result |
| --- | --- | --- | --- |
| SAN-AJD-001 | Page loads successfully | Logged-in user has Assign JDs access | Assignment Details and Recent JD Assignments are visible without an error. |
| SAN-AJD-002 | JD list is displayed and selectable | Active JDs exist | A JD can be selected and remains selected. |
| SAN-AJD-003 | JD search filters the list | Matching JD exists | Only matching JD records are displayed and selectable. |
| SAN-AJD-004 | Team list is displayed and selectable | Teams exist | A Team can be selected and remains selected. |
| SAN-AJD-005 | Team search filters the list | Matching Team exists | Only matching Team records are displayed and selectable. |
| SAN-AJD-006 | Valid JD-to-Team assignment | A JD and Team are available | Assignment completes without a blocking application error. |
| SAN-AJD-007 | Success confirmation after assignment | Valid JD and Team are selected | A recognizable success confirmation is displayed. |
| SAN-AJD-008 | Assignment appears in Recent JD Assignments | A JD was just assigned | The JD appears with its assigned Team. |
| SAN-AJD-009 | JD-required validation | Team selected, JD blank | Assignment is blocked with a JD-required message. |
| SAN-AJD-010 | Team-required validation | JD selected, Team blank | Assignment is blocked with a Team-required message. |
| SAN-AJD-011 | Both-required validation | JD and Team blank | Required-selection validation is displayed. |
| SAN-AJD-012 | Reset clears selections and searches | JD/Team state is present | Searches and selections return to their default state. |
| SAN-AJD-013 | Recent assignment search | Recent records exist | Results are filtered or a clear empty state is shown. |
| SAN-AJD-014 | List and Cards toggle | Recent records exist | Both views work without breaking the page. |
| SAN-AJD-015 | Page stability after assignment/reset | Assign page is open | Controls remain responsive with no blocking error. |
