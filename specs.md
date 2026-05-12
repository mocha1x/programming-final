# Project Specification: MyAccount

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
- Support light and dark mode with an animated theme toggle.
- Provide an admin panel for managing user accounts.

---

## 3. Tech Stack

| Layer            | Technology          |
|------------------|---------------------|
| Language         | Python 3.x          |
| GUI              | Tkinter (stdlib)    |
| Database         | SQLite3 (stdlib)    |
| Password Hashing | hashlib (stdlib)    |
| Email Validation | re (stdlib)         |
| CSV Export       | csv (stdlib)        |
| Remember Me      | json (stdlib)       |
| Icon Drawing     | math (stdlib)       |

> All dependencies are from the Python standard library — no `pip install` required.

---

## 4. File Structure

```
PROGRAMMING-FINAL/
├── final_code.py   # Entire application — database, auth, and all UI in one file
├── users.db        # Auto-generated SQLite3 database (created on first run)
├── remember.json   # Stores the remembered username between sessions
├── starter_code.py # Original starter code before development
├── specs.md        # This file
└── readme.md       # User-facing project readme
```

To run:
```
python final_code.py
```

---

## 5. final_code.py — Internal Structure

```
final_code.py
├── Config            # Color palettes, font constants, color globals, _interp()
├── Database          # All SQLite3 functions
├── Auth              # Password hashing and verification
├── Remember Me       # Save/load/clear remembered username via JSON
├── Password strength # pw_strength() scoring function
├── Shared helpers    # Reusable widget factories: field, btn, card, err_label, Checkbox
├── ThemeToggle       # Animated Canvas button that draws sun and moon icons
├── App (class)       # Root Tk window, footer, theme switcher, frame controller
├── LoginScreen       # Sign In screen
├── SignupScreen      # Sign Up screen
├── WelcomeScreen     # Post-login dashboard
├── AdminScreen       # Admin panel with user table and management tools
└── Entry point       # init_db() + App().mainloop()
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

| Function                           | Description                                      |
|------------------------------------|--------------------------------------------------|
| `init_db()`                        | Creates `users.db` and the users table if needed |
| `insert_user(username, email, pw)` | Inserts a new user record                        |
| `get_user(username)`               | Returns a user row dict or None                  |
| `user_exists(username)`            | Returns True if username is taken                |
| `email_exists(email)`              | Returns True if email is registered              |
| `get_all_users()`                  | Returns all user rows ordered by ID              |

---

## 8. Auth Functions

| Function                   | Description                                |
|----------------------------|--------------------------------------------|
| `hash_pw(password)`        | Returns SHA-256 hex digest of the password |
| `verify_pw(plain, stored)` | Returns True if plain hashes to stored     |

---

## 9. Remember Me Functions

| Function               | Description                                          |
|------------------------|------------------------------------------------------|
| `save_remember(user)`  | Writes username to `remember.json`                   |
| `load_remember()`      | Returns saved username, or empty string if not found |
| `clear_remember()`     | Overwrites the file with an empty object             |

---

## 10. Password Strength

`pw_strength(pw)` returns a tuple of `(bars, label, color)` based on a 0–5 point scoring system:

| Rule                        | Points |
|-----------------------------|--------|
| Length >= 8                 | +1     |
| Length >= 12                | +1     |
| Contains uppercase letter   | +1     |
| Contains a number           | +1     |
| Contains a special character| +1     |

| Score | Label  | Color   |
|-------|--------|---------|
| 0–1   | Weak   | DANGER  |
| 2     | Fair   | #ff9500 |
| 3–4   | Good   | #ffcc00 |
| 5     | Strong | SUCCESS |

---

## 11. Application Screens

### 11.1 — App (frame controller)

- Single `Tk()` root window, non-resizable. Geometry varies by active screen.
- Holds all four screens stacked in a container — `show(name)` raises the target screen to the top.
- Screens never open new windows.
- Footer at the bottom contains a text label and the `ThemeToggle` button.
- Footer is packed before the container so tkinter reserves its space first.

---

### 11.2 — Login screen (460x580)

**Fields:**
- `USERNAME` — Text entry
- `PASSWORD` — Masked entry (`show="*"`)

**Controls:**
- "Remember me" checkbox — pre-fills username on next launch
- Show / Hide password toggle label
- `SIGN IN` button
- "Sign up" link — switches to Sign Up screen

**Behaviour:**
- Validates both fields are non-empty.
- Hashes the entered password and checks it against the admin hash first, then the database.
- Admin login routes to AdminScreen; normal login routes to WelcomeScreen.
- On success: clears fields, transitions to the appropriate screen.
- On failure: shows inline red error, clears password field.
- Error message is deliberately vague ("Invalid username or password") to prevent username enumeration.
- Fields, toggle, and checkbox reset every time the screen is shown via `on_show()`.

---

### 11.3 — Signup screen (460x640)

**Fields:**
- `USERNAME` — Text entry
- `EMAIL` — Text entry
- `PASSWORD` — Masked entry
- `CONFIRM PASSWORD` — Masked entry

**Controls:**
- Password strength bar — 4 segments that fill and change color as you type
- `CREATE ACCOUNT` button
- "Already have an account? Sign in" clickable link — inside the card, switches to Login screen

**Behaviour:**
- Runs five validation checks in order (see Section 12).
- On success: inserts new record, shows green "Account created! Redirecting…" message,
  waits 1.2 seconds, clears fields, transitions to Login screen.
- On failure: shows specific inline red error for whichever rule was violated first.
- Fields and strength bar reset every time the screen is shown via `on_show()`.

---

### 11.4 — Welcome screen

**Shown after a successful sign-in.**

- Displays a green active indicator dot.
- Personalised heading: "Welcome back, {username}!"
- Account detail card with rows for: Username, Email, Status (Active), Member since.
- Member since date is formatted as "Month DD, YYYY" (e.g. January 15, 2025).
- `SIGN OUT` button returns the user to the Login screen.

---

### 11.5 — Admin screen (560x800)

**Accessible only via the hardcoded admin credentials.**

- Header row with "Admin • User Database" label and a "Sign out" link.
- Scrollable Treeview table showing all users: ID, USERNAME, EMAIL, CREATED AT.
- User count label below the table.
- Add user panel with USERNAME, EMAIL, and PASSWORD fields.
- Two rows of action buttons:
  - Row 1: `ADD USER` | `DELETE SELECTED`
  - Row 2: `REFRESH` | `EXPORT CSV`
- EXPORT CSV opens a save dialog and writes a CSV file with a header row.

---

## 12. Validation Rules

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

## 13. Shared Widget Helpers

| Helper          | Description                                                      |
|-----------------|------------------------------------------------------------------|
| `_round_rect()` | Draws a rounded rectangle on a Canvas using a smooth polygon     |
| `_darken()`     | Returns a darker version of a hex color for button hover effects |
| `field()`       | A labelled Entry embedded in a Canvas with a rounded border      |
| `btn()`         | A Canvas button with rounded corners and a hover effect          |
| `card()`        | A rounded SURFACE-colored panel that auto-sizes to its content   |
| `err_label()`   | A red Label for inline error messages, initially empty           |
| `Checkbox`      | A styled ttk.Checkbutton that matches the current theme          |
| `ThemeToggle`   | A Canvas button that draws an animated sun or moon icon          |

---

## 14. Theme System

Two color palettes are defined as dictionaries and unpacked into module-level globals. When the
theme switches, `_apply_theme()` updates the globals and rebuilds all screens from scratch.

### Light palette

| Constant  | Hex       | Used for                        |
|-----------|-----------|---------------------------------|
| `BG`      | `#f5f5f7` | Window and frame background     |
| `SURFACE` | `#ffffff`  | Card / panel background         |
| `BORDER`  | `#d2d2d7` | Entry borders, dividers         |
| `ACCENT`  | `#0071e3` | Buttons, links                  |
| `DANGER`  | `#ff3b30` | Error messages                  |
| `SUCCESS` | `#34c759` | Success messages, active status |
| `TEXT`    | `#1d1d1f` | Primary text                    |
| `MUTED`   | `#6e6e73` | Labels, secondary text          |

### Dark palette

| Constant  | Hex       | Used for                        |
|-----------|-----------|---------------------------------|
| `BG`      | `#1c1c1e` | Window and frame background     |
| `SURFACE` | `#2c2c2e` | Card / panel background         |
| `BORDER`  | `#3a3a3c` | Entry borders, dividers         |
| `ACCENT`  | `#0a84ff` | Buttons, links                  |
| `DANGER`  | `#ff453a` | Error messages                  |
| `SUCCESS` | `#30d158` | Success messages, active status |
| `TEXT`    | `#f5f5f7` | Primary text                    |
| `MUTED`   | `#98989d` | Labels, secondary text          |

The toggle animates over ~280ms (20 steps at 14ms each). The sun fades out over the first 60% of
the animation; the moon fades in over the last 60%, creating a brief crossfade. Colors snap
instantly at the end of the animation.

---

## 15. Admin Credentials

| Field    | Value     |
|----------|-----------|
| Username | `admin`   |
| Password | `Pa$$w0rd`|

The password is stored as a SHA-256 hash in `ADMIN_HASH`. To change it, generate a new hash and
replace that value in `final_code.py`.

---

## 16. Security Considerations

- Passwords are never stored in plain text — SHA-256 is applied before any write.
- Sign In errors are deliberately vague to prevent username enumeration.
- All database queries use parameterized statements to prevent SQL injection.
- `users.db` should be added to `.gitignore` if the project is version-controlled.

> **Note:** SHA-256 via `hashlib` is sufficient for a local demo. For any real-world or
> production deployment, replace it with `bcrypt` or `argon2`, which are designed
> specifically for password storage and are resistant to brute-force attacks.

---

## 17. How to View the Database

| Method                | How                                                              |
|-----------------------|------------------------------------------------------------------|
| VS Code extension     | Install SQLite Viewer by Florian Klampfer, click `users.db`     |
| DB Browser for SQLite | Download at sqlitebrowser.org, open `users.db`, Browse Data tab |
| Python script         | Run a quick SELECT * FROM users script using sqlite3 (stdlib)   |

---

## 18. Out of Scope (v1.0)

- Password reset / "Forgot Password" flow
- Email verification
- Session tokens or JWT
- Multi-user roles or permissions
- Remote / networked database

---

## 19. Future Enhancements (v2.0+)

- Upgrade password hashing to `bcrypt` or `argon2`
- Password strength indicator on the admin "Add User" panel
- Light mode toggle persistence between sessions
- Edit existing user details from the admin panel
- Account deletion from the Welcome screen
