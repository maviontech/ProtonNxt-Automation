# Create Team Sanity Test Suite

| ID | Scenario | Preconditions | Steps | Test Data | Expected Result | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| CTM-001 | Create Team UI loads | Logged-in admin | Open `Teams > Create Team` | — | Team input, member list, member search, Existing Teams list, and team search are available. | High |
| CTM-002 | Blank Team Name is rejected | Logged-in admin | Leave Team Name blank and validate the field. | Blank | Native required validation is available. | High |
| CTM-003 | Member is required | Logged-in admin | Enter a unique name, choose a team lead but no member, then submit. | Unique name | `Select at least one member` is displayed. | High |
| CTM-004 | Team lead is required | Logged-in admin | Enter a unique name, choose a member but no team lead, then submit. | Unique name | `Team lead must be selected` is displayed. | High |
| CTM-005 | Valid team creation | Logged-in admin | Enter a unique name, select a member and team lead, then submit. | Unique name | Success feedback is displayed and the team appears in Existing Teams. | Critical |
| CTM-006 | Duplicate team is rejected | Logged-in admin | Create a unique team, then submit the same name again. | Unique name | Duplicate-name error is displayed. | High |
| CTM-007 | Member search input | Logged-in admin | Enter a member-name query. | `Admin User` | The member search accepts the query. | Medium |
| CTM-008 | Existing Team search input | Logged-in admin | Enter a team search query. | `Automation` | The Existing Teams search accepts the query. | Medium |

## Manual coverage

Edit, delete, pagination, and filters are not automated because their controls are not available on the current Create Team screen. Team-name whitespace and server-side boundary behavior also remain manual until the product contract defines their expected result.
