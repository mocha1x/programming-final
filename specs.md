# Project Specification: SQLite3 + Tkinter Sign Up / Sign In Sheet

---

## 1. Project Overview

A desktop GUI application built with **Python**, **Tkinter**, and **SQLite3** that allows users to
create accounts and authenticate themselves. All user records are persisted locally in a SQLite3
database. The application validates credentials at sign-in by cross-referencing stored database
records. The entire program lives in a single file for simplicity.

---

## 2. Goals

- Provide a clean, user-friendly GUI for account registration and login.
- Persist user data securely in a local SQLite3 database.
- Authenticate returning users by validating credentials against the database.
- Protect passwords using hashing (no plain-text storage).
- Handle all edge cases (duplicate users, wrong passwords, empty fields, etc.) gracefully.

---

## 3. Tech Stack

| Layer            | Technology          |
|------------------|---------------------|
| Language         | Python 3.x          |
| GUI              | Tkinter (stdlib)    |
| Database         | SQLite3 (stdlib)    |
| Password Hashing | hashlib (stdlib)    |
| Email Validation | re (stdlib)         |

> All dependencies are from the Python standard library — no `pip install` required.

---

## 4. File Structure

```
PROGRAMMING-FINAL/
├── app.py        # Entire application — database, auth, and all UI in one file
├── users.db      # Auto-generated SQLite3 database (created on first run)
├── starter_code.py # Starter code before AI
└── specs.md      # This file
```

To run:
```
python app.py
```

---

## 5. app.py — Internal Structure

The single file is organised into clearly separated sections:

```
app.py
├── Config          # Colour palette, font constants, shared widget options
├── Database        # All SQLite3 functions
├── Auth            # Password hashing and verification
├── Widget helpers  # Reusable factory functions for entries, buttons, cards
├── App (class)     # Root Tk window + frame controller
├── LoginScreen     # Sign In screen
├── SignupScreen    # Sign Up screen
├── WelcomeScreen   # Post-login dashboard
└── Entry point     # init_db() + App().mainloop()
```

---

## 6. Database Schema

### Table: `users`

| Column       | Type    | Constraints                       |
|--------------|---------|-----------------------------------|
| `id`         | INTEGER | PRIMARY KEY, AUTOINCREMENT        |
| `username`   | TEXT    | NOT NULL, UNIQUE                  |
| `email`      | TEXT    | NOT NULL, UNIQUE                  |
| `password`   | TEXT    | NOT NULL (stored as SHA-256 hash) |
| `created_at` | TEXT    | NOT NULL (YYYY-MM-DD HH:MM:SS)    |

> `users.db` is created automatically on first run if it does not exist.

---

## 7. Database Functions

| Function                          | Description                               |
|-----------------------------------|-------------------------------------------|
| `init_db()`                       | Creates `users.db` and table if needed    |
| `insert_user(username, email, pw)`| Inserts a new user record                 |
| `get_user(username)`              | Returns a user row dict or None           |
| `user_exists(username)`           | Returns True if username is taken         |
| `email_exists(email)`             | Returns True if email is registered       |

---

## 8. Auth Functions

| Function                  | Description                                  |
|---------------------------|----------------------------------------------|
| `hash_pw(password)`       | Returns SHA-256 hex digest of the password   |
| `verify_pw(plain, stored)`| Returns True if plain hashes to stored       |

---

## 9. Application Screens

### 9.1 — App (frame controller)

- Single `Tk()` root window, fixed at 460x580px, non-resizable.
- Holds all three screens stacked in a container — `show(name)` raises the target screen to the top.
- Screens never open new windows.
- Footer label at the bottom of the root window.

---

### 9.2 — Login screen

**Fields:**
- `USERNAME` — Text entry
- `PASSWORD` — Masked entry (`show="*"`)

**Controls:**
- Show / Hide password toggle label
- `SIGN IN` button
- "Sign up" link — switches to Sign Up screen

**Behaviour:**
- Validates both fields are non-empty.
- Looks up username in the database; hashes the entered password and compares to stored hash.
- On success: clears fields, transitions to Welcome screen passing `username` and `created_at`.
- On failure: shows inline red error, clears password field.
- Error message is deliberately vague ("Invalid username or password") for both missing user
  and wrong password to prevent username enumeration.
- Fields and toggle reset every time the screen is shown via `on_show()`.

---

### 9.3 — Signup screen

**Fields:**
- `USERNAME` — Text entry
- `EMAIL` — Text entry
- `PASSWORD` — Masked entry
- `CONFIRM PASSWORD` — Masked entry

**Controls:**
- `CREATE ACCOUNT` button
- "Sign in" link — switches back to Login screen

**Behaviour:**
- Runs six validation checks in order (see Section 10).
- On success: inserts new record, shows green "Account created! Redirecting..." message,
  waits 1.2 seconds, clears fields, transitions to Login screen.
- On failure: shows specific inline red error for whichever rule was violated first.
- Fields reset every time the screen is shown via `on_show()`.

---

### 9.4 — Welcome screen

- Shown after a successful sign-in.
- Displays a green active indicator dot.
- Personalised heading: "Welcome back, {username}!"
- Account detail card showing status (Active) and member since date (`created_at`).
- `SIGN OUT` button returns the user to the Login screen.

---

## 10. Validation Rules

| # | Rule                       | Scope   | Error Message                                |
|---|----------------------------|---------|----------------------------------------------|
| 1 | Any field empty            | Both    | "All fields are required."                   |
| 2 | Invalid email format       | Sign Up | "Please enter a valid email address."        |
| 3 | Passwords don't match      | Sign Up | "Passwords do not match."                    |
| 4 | Username already taken     | Sign Up | "That username is already in use."           |
| 5 | Email already registered   | Sign Up | "An account with that email already exists." |
| 6 | Wrong username or password | Sign In | "Invalid username or password."              |

Email format is validated with the regex: `^[^@\s]+@[^@\s]+\.[^@\s]+$`

---

## 11. Shared Widget Helpers

These factory functions are defined once and reused across all three screens:

| Helper        | Returns                                                         |
|---------------|-----------------------------------------------------------------|
| `field()`     | A labelled `Entry` widget packed into the parent frame          |
| `btn()`       | A styled flat `Button` with consistent font and hover colour    |
| `card()`      | A raised SURFACE-coloured panel with an inner padding frame     |
| `err_label()` | A red `Label` for inline error messages, initially empty        |

---

## 12. Colour Palette

| Constant  | Hex       | Used for                        |
|-----------|-----------|---------------------------------|
| `BG`      | `#0f1117` | Window and frame background     |
| `SURFACE` | `#1a1d27` | Card / panel background         |
| `BORDER`  | `#2a2d3a` | Entry borders, dividers         |
| `ACCENT`  | `#4f8ef7` | Buttons, links                  |
| `DANGER`  | `#f75f5f` | Error messages                  |
| `SUCCESS` | `#3ecf8e` | Success messages, active status |
| `TEXT`    | `#e8eaf0` | Primary text                    |
| `MUTED`   | `#6b7280` | Labels, secondary text          |

---

## 13. Security Considerations

- Passwords are never stored in plain text — SHA-256 is applied before any write.
- Sign In errors are deliberately vague to prevent username enumeration.
- All database queries use parameterized statements to prevent SQL injection.
- `users.db` should be added to `.gitignore` if the project is version-controlled.

> **Note:** SHA-256 via `hashlib` is sufficient for a local demo. For any real-world or
> production deployment, replace it with `bcrypt` or `argon2`, which are designed
> specifically for password storage and are resistant to brute-force attacks.

---

## 14. How to View the Database

| Method                | How                                                              |
|-----------------------|------------------------------------------------------------------|
| VS Code extension     | Install SQLite Viewer by Florian Klampfer, click `users.db`     |
| DB Browser for SQLite | Download at sqlitebrowser.org, open `users.db`, Browse Data tab |
| Python script         | Run a quick SELECT * FROM users script using sqlite3 (stdlib)   |

---

## 15. Out of Scope (v1.0)

- Password reset / "Forgot Password" flow
- Email verification
- Session tokens or JWT
- Multi-user roles or permissions
- Remote / networked database
- Admin panel or user management UI

---

## 16. Future Enhancements (v2.0+)

- Upgrade password hashing to `bcrypt` or `argon2`
- "Remember Me" checkbox persisted to a local config file
- Admin view to browse all registered users
- Export user records to CSV
- Password strength indicator on the Sign Up screen
- Light mode toggle
