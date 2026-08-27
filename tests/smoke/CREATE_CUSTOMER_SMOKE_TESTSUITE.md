# Create Customer Smoke Test Suite

## CC-SMK-001 - Create Customer page loads successfully

**Steps**

1. Open the ProtonNxt application.
2. Login with a valid authorized user.
3. Navigate to `Customers > Create Customer`.

**Expected Result**

- Create Customer page loads successfully.
- Expected heading is displayed.
- Customer form and customer list are visible.
- No blocking application or server error is shown.

---

## CC-SMK-002 - Critical Create Customer controls are available

**Steps**

1. Open Create Customer.
2. Verify the key form controls and customer list controls are visible.

**Expected Result**

- Company Name, Contact Person Name, Contact Email, Contact Phone, Create Customer button, Search Company field, and Customer List table are available.

---

## CC-SMK-003 - Customer fields accept valid data

**Steps**

1. Open Create Customer.
2. Enter realistic valid values in all customer fields.

**Expected Result**

- Each customer field accepts and retains the entered value.

---

## CC-SMK-004 - Valid customer can be created

**Steps**

1. Fill the Create Customer form with a unique valid company.
2. Submit the form.

**Expected Result**

- Success feedback is shown.
- Created customer appears in the Customer List.

---

## CC-SMK-005 - Created customer is searchable

**Steps**

1. Create a unique valid customer.
2. Search for the newly created company name in Customer List.

**Expected Result**

- Filtered customer list shows the created company and its saved values.

---

## CC-SMK-006 - Missing required company name prevents creation

**Steps**

1. Open Create Customer.
2. Leave mandatory data empty.
3. Click `Create Customer`.

**Expected Result**

- Browser or application validation prevents submission.
- Customer is not created.
