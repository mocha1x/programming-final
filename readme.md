# MyAccount

A desktop sign-in and sign-up application built with Python, Tkinter, and SQLite3. Users can create accounts, log in, and view their account details — all stored locally in a database file. No internet connection or third-party packages required.

---

## Features

- **Sign Up** — Create an account with a username, email, and password
- **Sign In** — Log in and view your account details on a personalized welcome screen
- **Password security** — Passwords are hashed with SHA-256 before being stored; plain text is never saved
- **Password strength meter** — Live feedback as you type your password during sign-up
- **Remember Me** — Optionally save your username so it pre-fills on the next launch
- **Show / Hide password** — Toggle password visibility on the login screen
- **Light and dark mode** — Animated theme toggle with a sun/moon icon in the footer
- **Admin panel** — Log in as admin to view all users, add new accounts, delete accounts, and export the database to a CSV file
- **Input validation** — Clear inline error messages for empty fields, invalid emails, duplicate usernames, and mismatched passwords

---

## Requirements

- Python 3.x
- No third-party packages — everything used is from the Python standard library

---

## How to Run

```bash
python final_code.py
```

The database file `users.db` is created automatically on first run.

---

## File Structure

```
programming-final/
├── final_code.py     # The entire application — database, auth, and all UI in one file
├── users.db          # SQLite3 database, auto-generated on first run
├── remember.json     # Stores the "Remember Me" username between sessions
├── starter_code.py   # Original starter code before development
├── specs.md          # Full project specification and design decisions
└── readme.md         # This file
```

---

## Default Admin Credentials

| Field    | Value     |
|----------|-----------|
| Username | `admin`   |
| Password | `Pa$$w0rd`|

Log in with these credentials to access the admin panel.

> The admin password is stored as a SHA-256 hash in the source code. To change it, generate a new SHA-256 hash of your chosen password and replace `ADMIN_HASH` in `final_code.py`.

---

## Screens

### Login
Enter your username and password to sign in. Check "Remember me" to have your username pre-filled next time. Wrong credentials show a vague error message on purpose — this prevents someone from figuring out whether a username exists.

### Sign Up
Fill in a username, email, and password to create a new account. The password strength meter updates in real time. After a successful sign-up, you are automatically redirected to the login screen.

### Welcome
Shows your username, email, account status, and the date you joined. Click "Sign Out" to return to the login screen.

### Admin Panel
Only accessible with the admin credentials. Lets you view the full user database in a table, add new users manually, delete selected users, refresh the list, and export everything to a CSV file.

---

## Security Notes

- Passwords are hashed with SHA-256 via Python's built-in `hashlib` — plain text is never written to disk
- All database queries use parameterized statements to prevent SQL injection
- Login errors are deliberately vague to prevent username enumeration
- `users.db` should be added to `.gitignore` if this project is pushed to a public repository

> For a real-world deployment, replace SHA-256 with `bcrypt` or `argon2`, which are specifically designed to resist brute-force attacks on password databases.

---

## Tech Stack

| Layer            | Technology       |
|------------------|------------------|
| Language         | Python 3.x       |
| GUI              | Tkinter (stdlib) |
| Database         | SQLite3 (stdlib) |
| Password hashing | hashlib (stdlib) |
| Email validation | re (stdlib)      |
| CSV export       | csv (stdlib)     |
| Remember Me      | json (stdlib)    |
