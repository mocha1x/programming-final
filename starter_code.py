# Connect database through SQL

import sqlite3

try:
    with sqlite3.connect("my.db") as conn:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)

# GUI

from tkinter import *
from tkinter import messagebox

def toggle_password():
    if passw_entry.cget("show") == "*":
        passw_entry.config(show="")
        eye_btn.config(text="Hide")
    else:
        passw_entry.config(show="*")
        eye_btn.config(text="Show")

def sign_up():
    if email_entry or passw_entry == "":
        messagebox.showerror("Invalid input","Must use a valid email and password")
    else:
        messagebox.showinfo("Successful","Successfully signed up. Please log in now.")

root = Tk()
root.title("Sign Up")
root.geometry("400x400")

title_label = Label(root,text="Sign Up")
title_label.pack(pady=10)

email_entry = Entry(root)
email_entry.pack()

passw_entry = Entry(root, show="*")
passw_entry.pack()

eye_btn = Button(root,text="Show", command=toggle_password)
eye_btn.pack()

signup = Button(root,text="Sign Up", command=sign_up)
signup.pack()

root.mainloop()