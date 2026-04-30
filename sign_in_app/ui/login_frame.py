import tkinter as tk
from ui.theme import (
    BG, SURFACE, BORDER, ACCENT, ACCENT_HV,
    DANGER, TEXT, MUTED,
    FONT_TITLE, FONT_LABEL, FONT_BTN, FONT_SMALL,
    ENTRY_OPTS, PAD,
)
import database
import auth


def _make_field(parent, label_text: str, show: str = "") -> tuple[tk.Frame, tk.Entry]:
    """Helper: returns a labelled entry widget pair."""
    frame = tk.Frame(parent, bg=BG)
    tk.Label(frame, text=label_text, bg=BG, fg=MUTED, font=FONT_LABEL,
             anchor="w").pack(fill="x")
    entry = tk.Entry(frame, show=show, **ENTRY_OPTS)
    entry.pack(fill="x", ipady=7, pady=(2, 0))
    return frame, entry


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    # ------------------------------------------------------------------ build
    def _build(self):
        # ── Title block ──────────────────────────────────────────────────────
        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(pady=(44, 4))
        tk.Label(self, text="Sign in to your account", bg=BG, fg=MUTED,
                 font=FONT_SMALL).pack(pady=(0, 28))

        # ── Card panel ───────────────────────────────────────────────────────
        card = tk.Frame(self, bg=SURFACE, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=50, fill="x")

        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(padx=PAD*2, pady=PAD*2, fill="x")

        # Username field
        u_frame, self.username_entry = _make_field(inner, "USERNAME")
        u_frame.pack(fill="x", pady=(0, PAD))

        # Password field
        p_frame, self.passw_entry = _make_field(inner, "PASSWORD", show="*")
        p_frame.pack(fill="x")

        # Show / Hide toggle — kept from your starter code
        toggle_row = tk.Frame(inner, bg=SURFACE)
        toggle_row.pack(fill="x", pady=(4, 0))
        self.eye_btn = tk.Label(
            toggle_row, text="Show password", bg=SURFACE,
            fg=MUTED, font=FONT_SMALL, cursor="hand2"
        )
        self.eye_btn.pack(side="right")
        self.eye_btn.bind("<Button-1>", lambda e: self._toggle_password())

        # Error label (hidden until needed)
        self.error_label = tk.Label(
            inner, text="", bg=SURFACE, fg=DANGER, font=FONT_SMALL,
            wraplength=300, justify="left"
        )
        self.error_label.pack(fill="x", pady=(PAD, 0))

        # Sign In button
        self.signin_btn = tk.Button(
            inner, text="SIGN  IN",
            bg=ACCENT, fg="#ffffff", font=FONT_BTN,
            relief="flat", cursor="hand2", pady=9,
            activebackground=ACCENT_HV, activeforeground="#ffffff",
            command=self._sign_in,
        )
        self.signin_btn.pack(fill="x", pady=(PAD, 0))

        # ── Footer link ──────────────────────────────────────────────────────
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(pady=18)
        tk.Label(bottom, text="Don't have an account? ", bg=BG,
                 fg=MUTED, font=FONT_SMALL).pack(side="left")
        link = tk.Label(bottom, text="Sign up", bg=BG,
                        fg=ACCENT, font=FONT_SMALL, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self.controller.show_frame("SignupFrame"))

    # ---------------------------------------------------------------- actions
    def _toggle_password(self):
        """Toggling show/hide — adapted from your starter code."""
        if self.passw_entry.cget("show") == "*":
            self.passw_entry.config(show="")
            self.eye_btn.config(text="Hide password")
        else:
            self.passw_entry.config(show="*")
            self.eye_btn.config(text="Show password")

    def _set_error(self, msg: str):
        self.error_label.config(text=msg)

    def _clear_error(self):
        self.error_label.config(text="")

    def _sign_in(self):
        self._clear_error()
        username = self.username_entry.get().strip()
        password = self.passw_entry.get()

        # ── Validation ───────────────────────────────────────────────────────
        if not username or not password:
            self._set_error("All fields are required.")
            return

        # ── Database lookup ──────────────────────────────────────────────────
        try:
            user = database.get_user_by_username(username)
        except RuntimeError as e:
            self._set_error(f"Database error: {e}")
            return

        # Deliberately vague to prevent username enumeration
        if user is None or not auth.verify_password(password, user["password"]):
            self._set_error("Invalid username or password.")
            self.passw_entry.delete(0, "end")
            return

        # ── Success ──────────────────────────────────────────────────────────
        self._clear_fields()
        self.controller.show_frame(
            "WelcomeFrame",
            username=user["username"],
            created_at=user["created_at"],
        )

    def _clear_fields(self):
        self.username_entry.delete(0, "end")
        self.passw_entry.delete(0, "end")
        self._clear_error()

    def on_show(self, **kwargs):
        """Called by the controller whenever this frame is raised."""
        self._clear_fields()
        self.passw_entry.config(show="*")
        self.eye_btn.config(text="Show password")
