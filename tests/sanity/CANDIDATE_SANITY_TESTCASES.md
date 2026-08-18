# ProtonNxt Candidate Management - Sanity Test Suite

## Status

Candidate Management automation is scaffolded, but implementation is blocked until
the real ProtonNxt module path, locators, and approved test data are available.

## Proposed Sanity Scenarios

### SAN_CAND_001 - Candidate Management page loads

**Steps**

1. Login to ProtonNxt with valid credentials.
2. Open Candidate Management from the application navigation.
3. Wait for the page to load.

**Expected Result**

- Candidate Management page opens successfully.
- Candidate list/grid and primary controls are visible.

---

### SAN_CAND_002 - Candidate search returns expected record

**Steps**

1. Open Candidate Management.
2. Search using a known test candidate.
3. Observe the result set.

**Expected Result**

- Matching candidate record is displayed.
- Search/filter controls respond correctly.

---

### SAN_CAND_003 - Candidate profile opens successfully

**Steps**

1. Open Candidate Management.
2. Search for a known test candidate.
3. Open the candidate profile.

**Expected Result**

- Candidate detail page/modal opens.
- Core candidate information loads correctly.

---

### SAN_CAND_004 - Candidate create flow works

**Steps**

1. Open Candidate Management.
2. Start the create-candidate flow.
3. Enter approved test data.
4. Save the candidate.

**Expected Result**

- Candidate is created successfully in the test environment.
- New candidate can be searched and opened.

---

### SAN_CAND_005 - Candidate update persists

**Steps**

1. Open a known test candidate.
2. Update one critical field related to the changed functionality.
3. Save the record.
4. Reopen or refresh the record.

**Expected Result**

- Update is saved successfully.
- Changed value persists after reload.

---

### SAN_CAND_006 - Required validation is enforced

**Steps**

1. Open candidate create or edit flow.
2. Leave a required field empty or enter invalid data.
3. Attempt to save.

**Expected Result**

- Relevant validation message is displayed.
- Invalid record is not saved.
