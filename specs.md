# Project Specification: SQLite3 + Tkinter Sign Up / Sign In Sheet

---

## 1. Project Overview

A desktop GUI application built with **Python**, **Tkinter**, and **SQLite3** that allows users to create accounts and authenticate themselves. All user records are persisted locally in a SQLite3 database. The application validates credentials at sign-in by cross-referencing the stored database records.

---

## 2. Goals

- Provide a clean, user-friendly GUI for account registration and login.
- Persist user data securely in a local SQLite3 database.
- Authenticate returning users by validating credentials against the database.
- Protect passwords using hashing (no plain-text storage).
- Handle all edge cases (duplicate users, wrong passwords, empty fields, etc.) gracefully with feedback to the user.

---

## 3. Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Language     | Python 3.x              |
| GUI          | Tkinter (stdlib)        |
| Database     | SQLite3 (stdlib)        |
| Password Hashing | `hashlib` (stdlib) |
| Styling      | `ttk` themed widgets    |

> All dependencies are from the Python standard library — no `pip install` required.

---

## 4. File Structure

```
sign_in_app/
├── main.py              # Entry point — launches the app
├── database.py          # All SQLite3 logic (init, insert, query)
├── auth.py              # Password hashing and credential validation
├── ui/
│   ├── __init__.py
│   ├── app.py           # Root Tk window and frame controller
│   ├── login_frame.py   # Sign In screen
│   └── signup_frame.py  # Sign Up screen
├── users.db             # Auto-generated SQLite3 database (gitignored)
└── specs.md             # This file
```

---

## 5. Database Schema

### Table: `users`

| Column       | Type     | Constraints                        |
|--------------|----------|------------------------------------|
| `id`         | INTEGER  | PRIMARY KEY, AUTOINCREMENT         |
| `username`   | TEXT     | NOT NULL, UNIQUE                   |
| `email`      | TEXT     | NOT NULL, UNIQUE                   |
| `password`   | TEXT     | NOT NULL (stored as SHA-256 hash)  |
| `created_at` | TEXT     | NOT NULL (ISO 8601 timestamp)      |

> The database file `users.db` is created automatically on first run if it does not exist.

---

## 6. Application Screens

### 6.1 — Launch / Root Window
- Single `Tk()` root window, fixed size.
- Acts as a **frame controller**: swaps between the Sign In and Sign Up frames without opening new windows.
- Displays the application title at the top.

---

### 6.2 — Sign In Screen (`login_frame.py`)

**Fields:**
- `Username` — Text entry
- `Password` — Masked text entry (`show="*"`)

**Buttons:**
- `Sign In` — Validates credentials against the database
- `Go to Sign Up` — Switches the frame to the Sign Up screen

**Behavior:**
- On `Sign In`:
  - Validates that both fields are non-empty.
  - Hashes the entered password and compares it to the stored hash for the given username.
  - **Success:** Displays a welcome dialog and could transition to a "dashboard" placeholder frame.
  - **Failure:** Displays an inline error message (e.g., *"Invalid username or password."*).
- Clears the password field on each failed attempt.

---

### 6.3 — Sign Up Screen (`signup_frame.py`)

**Fields:**
- `Username` — Text entry
- `Email` — Text entry
- `Password` — Masked text entry
- `Confirm Password` — Masked text entry

**Buttons:**
- `Create Account` — Validates and writes new user to the database
- `Back to Sign In` — Switches the frame back to the Sign In screen

**Behavior:**
- On `Create Account`:
  - Validates all fields are non-empty.
  - Validates email format (basic regex check).
  - Validates `Password` and `Confirm Password` match.
  - Validates username and email are not already taken (queries the database).
  - Hashes the password before storing.
  - **Success:** Inserts the new record, displays a success dialog, and redirects to the Sign In screen.
  - **Failure:** Displays specific, inline error messages per validation rule violated.

---

### 6.4 — Welcome / Dashboard Screen *(placeholder)*

- Displayed after a successful sign-in.
- Shows a personalized message: *"Welcome back, {username}!"*
- Displays the account's `created_at` date.
- Provides a `Sign Out` button that returns the user to the Sign In screen.

---

## 7. Module Responsibilities

### `database.py`
- `init_db()` — Creates `users.db` and the `users` table if they don't exist.
- `insert_user(username, email, hashed_password)` — Inserts a new user record.
- `get_user_by_username(username)` — Returns a user row or `None`.
- `username_exists(username)` — Returns `True`/`False`.
- `email_exists(email)` — Returns `True`/`False`.

### `auth.py`
- `hash_password(password)` — Returns a SHA-256 hex digest of the password.
- `verify_password(plain_password, stored_hash)` — Returns `True` if the hash matches.

### `ui/app.py`
- Initializes the root `Tk` window.
- Manages frame switching via a `show_frame(frame_name)` method.
- Holds references to all frames.

---

## 8. Validation Rules

| Rule                        | Scope       | Error Message                                      |
|-----------------------------|-------------|----------------------------------------------------|
| Empty fields                | Both screens | "All fields are required."                        |
| Invalid email format        | Sign Up     | "Please enter a valid email address."              |
| Passwords don't match       | Sign Up     | "Passwords do not match."                          |
| Username already taken      | Sign Up     | "That username is already in use."                 |
| Email already registered    | Sign Up     | "An account with that email already exists."       |
| Username not found          | Sign In     | "Invalid username or password."                    |
| Incorrect password          | Sign In     | "Invalid username or password."                    |

> Sign In intentionally uses a generic error for both "not found" and "wrong password" to prevent username enumeration.

---

## 9. Security Considerations

- Passwords are **never stored in plain text**; SHA-256 hashing is applied before any database write.
- Sign In errors are deliberately **non-specific** to prevent user enumeration attacks.
- Database interactions use **parameterized queries** exclusively to prevent SQL injection.
- The `users.db` file should be listed in `.gitignore` if the project is version controlled.

> **Future enhancement:** Replace SHA-256 with `bcrypt` or `argon2` for production-grade password storage, as SHA-256 alone is not considered sufficient for password hashing in real applications.

---

## 10. Error Handling

- All database operations are wrapped in `try/except` blocks.
- GUI errors are surfaced to the user via `tkinter.messagebox` dialogs or inline `Label` widgets styled in red.
- Application does not crash on unexpected input — all edge cases return user-friendly messages.

---

## 11. Out of Scope (v1.0)

- Password reset / "Forgot Password" flow
- Email verification
- Session tokens or JWT
- Multi-user roles or permissions
- Remote/networked database
- Admin panel or user management UI

---

## 12. Future Enhancements (v2.0+)

- Add a `bcrypt`-based password hashing upgrade
- "Remember Me" checkbox using a local config file
- Admin view to list all registered users
- Export user records to CSV
- Dark mode / theme toggle
