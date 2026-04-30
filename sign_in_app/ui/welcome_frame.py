import tkinter as tk
from ui.theme import (
    BG, SURFACE, BORDER, ACCENT, ACCENT_HV,
    SUCCESS, TEXT, MUTED,
    FONT_TITLE, FONT_LABEL, FONT_BTN, FONT_SMALL,
    PAD,
)


class WelcomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    # ------------------------------------------------------------------ build
    def _build(self):
        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(pady=(56, 4))

        # Green dot + welcome message
        dot = tk.Label(self, text="●", bg=BG, fg=SUCCESS, font=("Courier", 10))
        dot.pack()

        self.welcome_label = tk.Label(
            self, text="", bg=BG, fg=TEXT,
            font=("Georgia", 15, "bold"),
        )
        self.welcome_label.pack(pady=(10, 4))

        self.subtitle_label = tk.Label(
            self, text="", bg=BG, fg=MUTED, font=FONT_SMALL,
        )
        self.subtitle_label.pack()

        # Info card
        card = tk.Frame(self, bg=SURFACE, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=60, pady=32, fill="x")

        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(padx=PAD*2, pady=PAD*2, fill="x")

        tk.Label(inner, text="ACCOUNT DETAILS", bg=SURFACE,
                 fg=MUTED, font=FONT_LABEL).pack(anchor="w")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=8)

        row = tk.Frame(inner, bg=SURFACE)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Status", bg=SURFACE, fg=MUTED,
                 font=FONT_SMALL, width=14, anchor="w").pack(side="left")
        tk.Label(row, text="Active", bg=SURFACE, fg=SUCCESS,
                 font=FONT_SMALL).pack(side="left")

        row2 = tk.Frame(inner, bg=SURFACE)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Member since", bg=SURFACE, fg=MUTED,
                 font=FONT_SMALL, width=14, anchor="w").pack(side="left")
        self.joined_label = tk.Label(row2, text="", bg=SURFACE,
                                     fg=TEXT, font=FONT_SMALL)
        self.joined_label.pack(side="left")

        # Sign Out button
        signout_btn = tk.Button(
            self, text="SIGN  OUT",
            bg=SURFACE, fg=TEXT, font=FONT_BTN,
            relief="flat", cursor="hand2", pady=9,
            highlightthickness=1, highlightbackground=BORDER,
            activebackground=BG, activeforeground=TEXT,
            command=lambda: self.controller.show_frame("LoginFrame"),
        )
        signout_btn.pack(padx=60, fill="x")

    # ---------------------------------------------------------------- on_show
    def on_show(self, username: str = "", created_at: str = "", **kwargs):
        self.welcome_label.config(text=f"Welcome back, {username}!")
        self.subtitle_label.config(text="You are signed in.")
        self.joined_label.config(text=created_at)
