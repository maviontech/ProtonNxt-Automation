# Calendar & MavionMeet settings smoke suite

Run `./run_calendar_settings_smoke_report.ps1` to generate `reports/smoke/calendar_settings_smoke_report.html`.
The existing login configuration supplies the ProtonNxt account. CM-002 expects that account to have an existing MavionMeet connection, as shown in the module screenshot.

| ID | Scenario | Expected result |
| --- | --- | --- |
| CM-001 | Open settings | Heading, email, API key, Connect & verify, and Back to Calendar controls are visible. |
| CM-002 | Existing connection | Connected confirmation and account email appear. |
| CM-003 | Saved key | API key value is absent from the input; format hint remains visible. |
| CM-004 | Back to Calendar | Link opens `/interview/calendar/`. |
| CM-005 | Connect and verify | Optional: a disconnected dedicated account can connect and persists after refresh. |

For CM-005, set `MAVIONMEET_TEST_EMAIL` and `MAVIONMEET_TEST_API_KEY` in the process environment. The test skips when either is missing or the account is already connected. It never revokes a connection. Keep the key out of committed files and test logs.
