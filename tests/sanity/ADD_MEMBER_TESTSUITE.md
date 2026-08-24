# Add Team Member Test Suite

## ATM-001 - Add Member page loads successfully

**Steps**

1. Login to ProtonNxt ATS with a valid admin account.
2. Open `Teams > Add Member`.

**Expected Result**

- Add Team Member page is displayed.
- Member form and Add Member button are visible.
- Field placeholders match the expected UX copy.

---

## ATM-002 - Required fields and status options are configured

**Steps**

1. Open the Add Team Member page.
2. Inspect the form fields and status dropdown.

**Expected Result**

- `First Name`, `Last Name`, `Email`, `Role`, and `Date Joined` are required.
- Status options are `Active`, `Inactive`, and `On Leave`.

---

## ATM-003 - Valid member can be added

**Steps**

1. Open the Add Team Member page.
2. Enter valid member data with a unique email address.
3. Submit the form.

**Expected Result**

- Form submits successfully.
- No validation summary is shown.
- Success feedback is displayed.

---

## ATM-004 - First Name is required

**Steps**

1. Fill all mandatory fields except `First Name`.
2. Validate the field.

**Expected Result**

- `First Name` is marked invalid.

---

## ATM-005 - Last Name is required

**Steps**

1. Fill all mandatory fields except `Last Name`.
2. Validate the field.

**Expected Result**

- `Last Name` is marked invalid.

---

## ATM-006 - Email is required

**Steps**

1. Fill all mandatory fields except `Email`.
2. Validate the field.

**Expected Result**

- `Email` is marked invalid.

---

## ATM-007 - Invalid email format is rejected

**Steps**

1. Enter `invalid-email` in the `Email` field.
2. Validate the field.

**Expected Result**

- Email field is invalid.
- Browser validation message is available.

---

## ATM-008 - Invalid phone format is rejected

**Steps**

1. Enter a non-numeric phone like `abc123`.
2. Validate the field.

**Expected Result**

- Phone field is invalid.
- Browser validation message is available.

---

## ATM-009 - Role is required

**Steps**

1. Fill all mandatory fields except `Role`.
2. Validate the field.

**Expected Result**

- `Role` is marked invalid.

---

## ATM-010 - Date Joined is required

**Steps**

1. Fill all mandatory fields except `Date Joined`.
2. Validate the field.

**Expected Result**

- `Date Joined` is marked invalid.

---

## ATM-011 - Date Joined bounds are enforced

**Steps**

1. Verify the configured min and max date.
2. Try a date before `2020-01-01`.
3. Try a future date.

**Expected Result**

- Minimum date is `2020-01-01`.
- Maximum date is today's date.
- Out-of-range dates are invalid.

---

## ATM-012 - Max length and inactive status selection work

**Steps**

1. Verify field maxlength constraints.
2. Select `Inactive` as status.
3. Enter a valid phone format.

**Expected Result**

- Maxlength values match the form contract.
- `Inactive` is selected successfully.
- Valid phone number passes validation.

---

## ATM-013 - Whitespace input and alternate status selection are accepted

**Steps**

1. Enter values with leading and trailing spaces.
2. Select `On Leave`.

**Expected Result**

- Input values are accepted into the fields.
- `On Leave` status is selected successfully.
