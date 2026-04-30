"""
UserVault — SQLite3 + Tkinter Sign Up / Sign In App
Entry point: python main.py
"""

import database
from ui.app import App


def main():
    # Initialise the database (creates users.db + table if not present)
    database.init_db()

    # Launch the GUI
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
