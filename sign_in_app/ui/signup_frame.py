import re
import tkinter as tk
from ui.theme import (
    BG, SURFACE, BORDER, ACCENT, ACCENT_HV,
    SUCCESS, DANGER, TEXT, MUTED,
    FONT_TITLE, FONT_LABEL, FONT_BTN, FONT_SMALL,
    ENTRY_OPTS, PAD,
)
import database
import auth

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _make_field(parent, label_text: str, show: str = "") -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent, bg=SURFACE)
    tk.Label(frame, text=label_text, bg=SURFACE, fg=MUTED,
             font=FONT_LABEL, anchor="w").pack(fill="x")
    entry = tk.Entry(frame, show=show, **ENTRY_OPTS)
    entry.pack(fill="x", ipady=7, pady=(2, 0))
    return frame, entry


class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    # ------------------------------------------------------------------ build
    def _build(self):
        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(pady=(32, 4))
        tk.Label(self, text="Create a new account", bg=BG, fg=MUTED,
                 font=FONT_SMALL).pack(pady=(0, 20))

        card = tk.Frame(self, bg=SURFACE, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=50, fill="x")

        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(padx=PAD*2, pady=PAD*2, fill="x")

        u_frame, self.username_entry = _make_field(inner, "USERNAME")
        u_frame.pack(fill="x", pady=(0, PAD))

        e_frame, self.email_entry = _make_field(inner, "EMAIL")
        e_frame.pack(fill="x", pady=(0, PAD))

        p_frame, self.passw_entry = _make_field(inner, "PASSWORD", show="*")
        p_frame.pack(fill="x", pady=(0, PAD))

        cp_frame, self.confirm_entry = _make_field(inner, "CONFIRM PASSWORD", show="*")
        cp_frame.pack(fill="x")

        # Error label
        self.error_label = tk.Label(
            inner, text="", bg=SURFACE, fg=DANGER, font=FONT_SMALL,
            wraplength=300, justify="left",
        )
        self.error_label.pack(fill="x", pady=(PAD, 0))

        # Create Account button
        self.signup_btn = tk.Button(
            inner, text="CREATE ACCOUNT",
            bg=ACCENT, fg="#ffffff", font=FONT_BTN,
            relief="flat", cursor="hand2", pady=9,
            activebackground=ACCENT_HV, activeforeground="#ffffff",
            command=self._sign_up,
        )
        self.signup_btn.pack(fill="x", pady=(PAD, 0))

        # Footer link
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(pady=16)
        tk.Label(bottom, text="Already have an account? ", bg=BG,
                 fg=MUTED, font=FONT_SMALL).pack(side="left")
        link = tk.Label(bottom, text="Sign in", bg=BG,
                        fg=ACCENT, font=FONT_SMALL, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self.controller.show_frame("LoginFrame"))

    # ---------------------------------------------------------------- actions
    def _set_error(self, msg: str):
        self.error_label.config(text=msg, fg=DANGER)

    def _set_success(self, msg: str):
        self.error_label.config(text=msg, fg=SUCCESS)

    def _clear_error(self):
        self.error_label.config(text="")

    def _sign_up(self):
        self._clear_error()
        username = self.username_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.passw_entry.get()
        confirm  = self.confirm_entry.get()

        # ── Validation ───────────────────────────────────────────────────────
        if not all([username, email, password, confirm]):
            self._set_error("All fields are required.")
            return

        if not EMAIL_RE.match(email):
            self._set_error("Please enter a valid email address.")
            return

        if password != confirm:
            self._set_error("Passwords do not match.")
            self.confirm_entry.delete(0, "end")
            return

        # ── Database uniqueness checks ───────────────────────────────────────
        try:
            if database.username_exists(username):
                self._set_error("That username is already in use.")
                return
            if database.email_exists(email):
                self._set_error("An account with that email already exists.")
                return
        except RuntimeError as e:
            self._set_error(f"Database error: {e}")
            return

        # ── Insert ───────────────────────────────────────────────────────────
        try:
            database.insert_user(username, email, auth.hash_password(password))
        except (ValueError, RuntimeError) as e:
            self._set_error(f"Could not create account: {e}")
            return

        # ── Success ──────────────────────────────────────────────────────────
        self._set_success(f"Account created! Redirecting to sign in…")
        self.after(1200, self._redirect_to_login)

    def _redirect_to_login(self):
        self._clear_fields()
        self.controller.show_frame("LoginFrame")

    def _clear_fields(self):
        for entry in (self.username_entry, self.email_entry,
                      self.passw_entry, self.confirm_entry):
            entry.delete(0, "end")
        self._clear_error()

    def on_show(self, **kwargs):
        self._clear_fields()
