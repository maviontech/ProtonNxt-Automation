# Create JD Sanity Test Suite

| ID | Scenario | Preconditions | Steps | Test Data | Expected Result | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| CJD-SAN-001 | Create JD page loads successfully | Logged-in user with JD creation permission | Open `Recruitment Tasks > Create New JD`. | N/A | Create JD page loads without application or server error and the form is visible. | Critical |
| CJD-SAN-002 | All critical Create JD controls are displayed | Create JD page is open | Verify JD Summary, Company, SPOC Name, SPOC Email, Description, skills, Budget/CTC, Experience, Education, Location, Positions, Status, and Create JD button. | N/A | All critical controls are visible and available for interaction. | Critical |
| CJD-SAN-003 | Job Title / JD Summary accepts valid input | Create JD page is open | Enter a valid JD summary/title. | `Senior Python Developer` | The entered JD summary is retained in the field. | High |
| CJD-SAN-004 | Company can be searched and selected | At least one selectable company exists | Search for a company and select it from the custom dropdown. | Existing company | Selected company remains displayed and hidden company ID is populated. | Critical |
| CJD-SAN-005 | JD SPOC Name accepts valid input | Create JD page is open | Enter a valid customer-side SPOC name. | `Rahul Sharma` | SPOC name is retained without unexpected validation errors. | Medium |
| CJD-SAN-006 | JD SPOC Email accepts valid email | Create JD page is open | Enter a valid SPOC email address. | `spoc@example.com` | Valid email is accepted and retained. | High |
| CJD-SAN-007 | JD Description editor accepts multiline content | Create JD page is open | Enter multiple lines of JD content in the rich-text editor. | Multiline JD content | Description accepts the content, preserves meaningful line breaks, and remains editable. | Critical |
| CJD-SAN-008 | JD Description basic formatting controls work | Text exists in JD Description | Select text and apply a basic format such as bold. | Sample description text | Formatting is applied without clearing the description. | Medium |
| CJD-SAN-009 | Format Pasted Text works with pasted JD content | JD Description contains pasted text | Paste JD content and click `Format Pasted Text`. | Pasted multiline JD text | Formatting completes without unexpected alert/error and important content remains present. | High |
| CJD-SAN-010 | Must Have Skills accepts valid skills | Create JD page is open | Enter required skills. | `Python, Django, REST API, MySQL` | Must Have Skills are retained correctly. | High |
| CJD-SAN-011 | Good to Have Skills accepts valid skills | Create JD page is open | Enter preferred skills. | `Docker, Redis, AWS` | Good to Have Skills are retained correctly. | Medium |
| CJD-SAN-012 | Budget/CTC accepts valid value | Create JD page is open | Enter a valid budget/CTC value. | `10-15 LPA` | Budget/CTC is accepted and retained. | Medium |
| CJD-SAN-013 | Experience Required accepts valid value | Create JD page is open | Enter a valid experience requirement. | `3-5 years` | Experience requirement is accepted and retained. | High |
| CJD-SAN-014 | Education Required accepts valid value | Create JD page is open | Enter a valid education requirement. | `Bachelor's in Computer Science` | Education requirement is accepted and retained. | Medium |
| CJD-SAN-015 | Location accepts valid value | Create JD page is open | Enter the job location. | `Pune / Remote` | Location is accepted and retained. | Medium |
| CJD-SAN-016 | Number of Positions accepts a valid positive number | Create JD page is open | Enter a valid number of positions. | `2` | Positions retains the valid positive number. | High |
| CJD-SAN-017 | Default Number of Positions is usable | Create JD page is newly opened | Observe the default Positions value without changing it. | Default shown on page | A valid default value is displayed and usable for submission. | Medium |
| CJD-SAN-018 | Status dropdown loads and allows selection | Create JD page is open | Open Status dropdown and choose an available status. | `active` | Status options load and the selected status remains selected. | High |
| CJD-SAN-019 | Minimum valid JD can be created | Logged-in user and selectable company available | Fill the minimum required valid data and submit the form. | Unique JD title and required fields | JD is created successfully with positive feedback. | Critical |
| CJD-SAN-020 | Complete JD can be created with all available fields | Logged-in user and selectable company available | Fill all Create JD fields with valid data and submit the form. | Complete valid JD dataset | Complete JD is created successfully and saved. | Critical |
| CJD-SAN-021 | Missing mandatory data prevents JD creation | Create JD page is open | Leave mandatory fields blank and click Create JD. | Blank required fields | JD is not created and validation is shown for required data. | Critical |
| CJD-SAN-022 | Invalid SPOC email is rejected | Create JD page is open | Enter an invalid SPOC email and attempt submission. | `invalid-email` | Invalid email is not accepted for successful submission and validation is shown. | High |
| CJD-SAN-023 | Created JD appears in View/Edit JDs | A valid JD has just been created | Open `View/Edit JDs` and search using the created JD title. | Previously created unique JD title | Created JD is found in the list/search results. | Critical |
| CJD-SAN-024 | Created JD core values persist correctly | A valid JD has been created and is available in View/Edit JDs | Open the created JD and compare the saved values with the input data. | JD Summary, Company, Positions, Status | Saved core values match the creation data. | Critical |
| CJD-SAN-025 | Create JD button submits only once per user action | Mandatory valid data is filled | Click Create JD once and observe the result. | Valid JD dataset | A single JD is created for a single submission without duplicates. | High |

## Manual coverage

Company-specific search edge cases, rich-text formatting beyond a basic bold verification, and any workflow that depends on unstable edit-modal controls remain partly manual if the DOM changes in future builds.
