# ProtonNxt Login Test Suite

## LGN-001 - Login page loads successfully

**Steps**

1. Open the ProtonNxt login URL.
2. Observe the page load.

**Expected Result**

- Login page loads without layout issues.
- Company Code field is visible.
- Login Email field is visible.
- Password field is visible.
- Remember me checkbox is visible.
- Sign in button is visible.

---

## LGN-002 - Password is masked by default

**Steps**

1. Open the ProtonNxt Login page.
2. Click the Password field.
3. Type a password value.

**Expected Result**

- Password characters are masked.

---

## LGN-003 - Password visibility toggle works

**Steps**

1. Open the ProtonNxt Login page.
2. Enter a password.
3. Click the password visibility icon.
4. Click the password visibility icon again.

**Expected Result**

- First click reveals the password.
- Second click hides the password again.

---

## LGN-004 - Forgot password link opens reset flow

**Steps**

1. Open the ProtonNxt Login page.
2. Click **Forgot password**.

**Expected Result**

- User is navigated to the forgot-password page or reset flow.

---

## LGN-005 - Remember me checkbox can be selected

**Steps**

1. Open the ProtonNxt Login page.
2. Click the **Remember me** checkbox.
3. Click the checkbox again.

**Expected Result**

- Checkbox toggles between checked and unchecked state.

---

## LGN-006 - Submit with all fields blank

**Steps**

1. Open the ProtonNxt Login page.
2. Leave Company Code, Login Email, and Password blank.
3. Click **Sign in**.

**Expected Result**

- User stays on the Login page.
- Required field validation is shown.

---

## LGN-007 - Submit with blank company code only

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Login Email.
3. Enter valid Password.
4. Leave Company Code blank.
5. Click **Sign in**.

**Expected Result**

- User stays on the Login page.
- Company Code required validation is shown.

---

## LGN-008 - Submit with blank email only

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Password.
4. Leave Login Email blank.
5. Click **Sign in**.

**Expected Result**

- User stays on the Login page.
- Login Email required validation is shown.

---

## LGN-009 - Submit with blank password only

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Login Email.
4. Leave Password blank.
5. Click **Sign in**.

**Expected Result**

- User stays on the Login page.
- Password required validation is shown.

---

## LGN-010 - Company code with surrounding spaces

**Steps**

1. Open the ProtonNxt Login page.
2. Enter Company Code with leading and trailing spaces.
3. Enter valid Login Email.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Spaces are trimmed or handled correctly.
- Login proceeds successfully if the credentials are valid.

---

## LGN-011 - Login email with surrounding spaces

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter Login Email with leading and trailing spaces.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Spaces are trimmed or handled correctly.
- Login proceeds successfully if the credentials are valid.

---

## LGN-012 - Valid admin login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid admin Login Email.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Admin user is authenticated successfully.
- User is redirected to the admin dashboard.

---

## LGN-013 - Valid recruiter login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid recruiter Login Email.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Recruiter user is authenticated successfully.
- User is redirected to the home page or recruiter landing page.

---

## LGN-014 - Invalid company code

**Steps**

1. Open the ProtonNxt Login page.
2. Enter invalid Company Code.
3. Enter valid-looking Login Email.
4. Enter valid-looking Password.
5. Click **Sign in**.

**Expected Result**

- User is not logged in.
- Appropriate invalid Company Code error is displayed.

---

## LGN-015 - Wrong password for valid user

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Login Email.
4. Enter wrong Password.
5. Click **Sign in**.

**Expected Result**

- User is not logged in.
- Invalid credentials message is displayed.

---

## LGN-016 - Unknown user login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter unknown Login Email.
4. Enter any Password.
5. Click **Sign in**.

**Expected Result**

- User is not logged in.
- Invalid credentials message is displayed.

---

## LGN-017 - Disabled or inactive account login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter disabled or inactive Login Email.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Login is blocked.
- Disabled or inactive account message is displayed.

---

## LGN-020 - Successful login resets failed-attempt counter

**Steps**

1. Create one or more failed login attempts for a valid user.
2. Login successfully with valid credentials.
3. Logout.
4. Try one wrong password again.

**Expected Result**

- Successful login resets the failed-attempt counter.
- Next wrong attempt is treated as a fresh failed attempt.

---

## LGN-021 - New web login replaces previous web session

**Steps**

1. Login with a valid user in browser A.
2. Login with the same user in browser B.
3. Refresh or interact with a protected page in browser A.

**Expected Result**

- Second login succeeds.
- Previous web session becomes invalid.

---

## LGN-022 - Web login does not remove active mobile session

**Steps**

1. Login with a valid user on mobile.
2. Login with the same user on web.
3. Validate the mobile session.

**Expected Result**

- Web login succeeds.
- Mobile session remains active if that is the intended behavior.

---

## LGN-023 - Session creation failure is handled gracefully

**Steps**

1. Simulate a session creation or persistence failure.
2. Attempt valid login.

**Expected Result**

- User is not taken into the application.
- A meaningful session creation failure message is shown.

---

## LGN-024 - Remember me stores company code and email

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Login Email.
4. Enter valid Password.
5. Select **Remember me**.
6. Click **Sign in**.
7. Logout and reopen the Login page in the same browser.

**Expected Result**

- Company Code is retained.
- Login Email is retained.

---

## LGN-025 - Unchecked Remember me does not store login data

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Login Email.
4. Enter valid Password.
5. Keep **Remember me** unchecked.
6. Click **Sign in**.
7. Logout and reopen the Login page.

**Expected Result**

- Company Code is not retained.
- Login Email is not retained.

---

## LGN-026 - Blocked tenant cannot complete login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid credentials for a blocked tenant.
3. Click **Sign in**.

**Expected Result**

- User is not allowed into the application.
- User is redirected to the blocked subscription page or shown the blocked reason.

---

## LGN-027 - Grandfathered tenant is allowed to login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid credentials for a grandfathered tenant.
3. Click **Sign in**.

**Expected Result**

- Login succeeds.
- Subscription enforcement does not block the user.

---

## LGN-028 - Direct access to protected page without login

**Steps**

1. Open a protected ProtonNxt page URL directly without logging in.

**Expected Result**

- User is redirected to the Login page.

---

## LGN-029 - Login form preserves company code and email after failed login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter Company Code.
3. Enter Login Email.
4. Enter wrong Password.
5. Click **Sign in**.

**Expected Result**

- Login fails.
- Company Code remains populated.
- Login Email remains populated.

---

## LGN-030 - Password field is not repopulated after failed login

**Steps**

1. Open the ProtonNxt Login page.
2. Enter Company Code.
3. Enter Login Email.
4. Enter wrong Password.
5. Click **Sign in**.

**Expected Result**

- Login fails.
- Password field is cleared or not repopulated.
