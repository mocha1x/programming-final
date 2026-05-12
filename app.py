"""
UserVault — single file version
Run: python app.py
"""

import sqlite3
import hashlib
import re
import json
import math
import csv
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

DB           = "users.db"
REMEMBER_FILE = "remember.json"
EMAIL_RE     = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ADMIN_USER = "admin"
ADMIN_HASH = "97c94ebe5d767a353b77f3c0ce2d429741f2e8c99473c3c150e2faa3d14c9da6"

FONT  = "Segoe UI"

LIGHT = dict(BG="#f5f5f7", SURFACE="#ffffff", BORDER="#d2d2d7",
             ACCENT="#0071e3", DANGER="#ff3b30", SUCCESS="#34c759",
             TEXT="#1d1d1f",   MUTED="#6e6e73")
DARK  = dict(BG="#1c1c1e",  SURFACE="#2c2c2e", BORDER="#3a3a3c",
             ACCENT="#0a84ff", DANGER="#ff453a", SUCCESS="#30d158",
             TEXT="#f5f5f7",   MUTED="#98989d")
_dark = False

BG, SURFACE, BORDER = LIGHT["BG"], LIGHT["SURFACE"], LIGHT["BORDER"]
ACCENT, DANGER, SUCCESS = LIGHT["ACCENT"], LIGHT["DANGER"], LIGHT["SUCCESS"]
TEXT, MUTED = LIGHT["TEXT"], LIGHT["MUTED"]

def _interp(c1, c2, t):
    r = int(int(c1[1:3], 16) * (1-t) + int(c2[1:3], 16) * t)
    g = int(int(c1[3:5], 16) * (1-t) + int(c2[3:5], 16) * t)
    b = int(int(c1[5:7], 16) * (1-t) + int(c2[5:7], 16) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE,
            email      TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")

def insert_user(username, email, password_hash):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO users (username,email,password,created_at) VALUES (?,?,?,?)",
                  (username, email, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def get_user(username):
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        return c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

def user_exists(username):
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() is not None

def email_exists(email):
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone() is not None

def get_all_users():
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        return c.execute(
            "SELECT id, username, email, created_at FROM users ORDER BY id"
        ).fetchall()

# ── Auth ──────────────────────────────────────────────────────────────────────

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(plain, stored):
    return hash_pw(plain) == stored

# ── Remember Me ───────────────────────────────────────────────────────────────

def save_remember(username):
    with open(REMEMBER_FILE, "w") as f:
        json.dump({"username": username}, f)

def load_remember():
    try:
        with open(REMEMBER_FILE) as f:
            return json.load(f).get("username", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

def clear_remember():
    try:
        with open(REMEMBER_FILE, "w") as f:
            json.dump({}, f)
    except OSError:
        pass

# ── Password strength ─────────────────────────────────────────────────────────

def pw_strength(pw):
    """Returns (bars 0-4, label, color) for the given password."""
    if not pw:
        return 0, "", MUTED
    score = 0
    if len(pw) >= 8:                    score += 1
    if len(pw) >= 12:                   score += 1
    if re.search(r"[A-Z]", pw):         score += 1
    if re.search(r"[0-9]", pw):         score += 1
    if re.search(r"[^A-Za-z0-9]", pw): score += 1
    if score <= 1: return 1, "Weak",   DANGER
    if score == 2: return 2, "Fair",   "#ff9500"
    if score <= 4: return 3, "Good",   "#ffcc00"
    return              4, "Strong",  SUCCESS

# ── Shared widget helpers ─────────────────────────────────────────────────────

_FIELD_H = 42

def _round_rect(cv, x1, y1, x2, y2, r, **kw):
    pts = [x1+r, y1,  x2-r, y1,  x2, y1,  x2, y1+r,
           x2, y2-r,  x2, y2,  x2-r, y2,  x1+r, y2,
           x1, y2,  x1, y2-r,  x1, y1+r,  x1, y1]
    cv.create_polygon(pts, smooth=True, **kw)

def field(parent, label, show=""):
    if label:
        tk.Label(parent, text=label, bg=SURFACE, fg=MUTED,
                 font=(FONT, 9, "bold"), anchor="w").pack(fill="x")
    cv = tk.Canvas(parent, height=_FIELD_H, bg=SURFACE, highlightthickness=0)
    cv.pack(fill="x", pady=(2, 10))
    entry = tk.Entry(cv, show=show, bg=SURFACE, fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     font=(FONT, 11), bd=0, highlightthickness=0)

    def _draw(border=BORDER):
        cv.delete("all")
        w = cv.winfo_width() or 300
        _round_rect(cv, 1, 1, w-2, _FIELD_H-2, 8,
                    fill=SURFACE, outline=border, width=1)
        cv.create_window(12, _FIELD_H//2, anchor="w", window=entry,
                         width=w-24, height=_FIELD_H-14)

    cv.bind("<Configure>", lambda e: _draw())
    entry.bind("<FocusIn>",  lambda e: _draw(ACCENT))
    entry.bind("<FocusOut>", lambda e: _draw(BORDER))
    return entry

_BTN_H  = 44
_CARD_R = 10

def _darken(color, amount=22):
    r = max(0, int(color[1:3], 16) - amount)
    g = max(0, int(color[3:5], 16) - amount)
    b = max(0, int(color[5:7], 16) - amount)
    return f"#{r:02x}{g:02x}{b:02x}"

def btn(parent, text, color, command):
    cv = tk.Canvas(parent, height=_BTN_H, bg=parent.cget("bg"),
                   highlightthickness=0, cursor="hand2")

    def _draw(fill=color):
        cv.delete("all")
        w = cv.winfo_width() or 200
        _round_rect(cv, 0, 0, w, _BTN_H, 8, fill=fill, outline="")
        cv.create_text(w // 2, _BTN_H // 2, text=text,
                       fill="#fff", font=(FONT, 10, "bold"))

    cv.bind("<Configure>", lambda e: _draw())
    cv.bind("<Enter>",     lambda e: _draw(_darken(color)))
    cv.bind("<Leave>",     lambda e: _draw(color))
    cv.bind("<Button-1>",  lambda e: command())
    return cv

def card(parent):
    cv = tk.Canvas(parent, bg=BG, highlightthickness=0)
    cv.pack(padx=50, fill="x")
    content = tk.Frame(cv, bg=SURFACE)
    win_id  = cv.create_window(4, 4, anchor="nw", window=content)
    _prev   = [0, 0]

    def _resize(e=None):
        cw = cv.winfo_width() or 360
        ch = content.winfo_reqheight() or 40
        total_h = ch + 8
        if cw == _prev[0] and total_h == _prev[1]:
            return
        _prev[0], _prev[1] = cw, total_h
        cv.config(height=total_h)
        cv.itemconfig(win_id, width=cw - 8)
        cv.delete("bg")
        _round_rect(cv, 0, 0, cw, total_h, _CARD_R,
                    fill=SURFACE, outline=BORDER, width=1, tags="bg")
        cv.tag_lower("bg")

    cv.bind("<Configure>",    lambda e: _resize())
    content.bind("<Configure>", lambda e: _resize())
    inner = tk.Frame(content, bg=SURFACE)
    inner.pack(padx=24, pady=24, fill="x")
    return inner

def err_label(parent):
    lbl = tk.Label(parent, text="", bg=SURFACE, fg=DANGER,
                   font=(FONT, 9), wraplength=300, justify="left")
    lbl.pack(fill="x", pady=(0, 8))
    return lbl

class Checkbox(tk.Frame):
    def __init__(self, parent, text, variable):
        bg = parent.cget("bg")
        super().__init__(parent, bg=bg)
        s = ttk.Style()
        s.configure("CB.TCheckbutton",
                    background=bg, foreground=MUTED,
                    font=(FONT, 10), focusthickness=0, focuscolor=bg,
                    indicatorrelief="flat", indicatorsize=18, padding=2)
        s.map("CB.TCheckbutton",
              background=[("active", bg)],
              foreground=[("active", MUTED)],
              indicatorcolor=[("selected", ACCENT), ("!selected", SURFACE)])
        ttk.Checkbutton(self, text=text, variable=variable,
                        style="CB.TCheckbutton",
                        cursor="hand2").pack(side="left")

# ── Theme toggle button ───────────────────────────────────────────────────────

class ThemeToggle(tk.Canvas):
    _W, _H = 36, 36

    def __init__(self, parent, callback):
        super().__init__(parent, width=self._W, height=self._H,
                         highlightthickness=0, cursor="hand2")
        self.bind("<Button-1>", lambda _: callback())
        self.draw(0.0)

    def draw(self, t):
        self.delete("all")
        W, H = self._W, self._H
        cx, cy = W // 2, H // 2

        self.create_oval(1, 1, W-1, H-1, fill=SURFACE, outline=BORDER, width=1)

        sun_alpha  = max(0.0, 1.0 - t / 0.6)
        moon_alpha = max(0.0, min(1.0, (t - 0.4) / 0.6))

        # ── Sun: yellow core + 8 rays ─────────────────────────────────
        if sun_alpha > 0.02:
            sc = _interp(SURFACE, "#ff9f0a", sun_alpha)
            sr = 4
            self.create_oval(cx-sr, cy-sr, cx+sr, cy+sr, fill=sc, outline="")
            for i in range(8):
                a  = math.radians(i * 45)
                x1 = cx + 6  * math.cos(a)
                y1 = cy + 6  * math.sin(a)
                x2 = cx + 10 * math.cos(a)
                y2 = cy + 10 * math.sin(a)
                self.create_line(x1, y1, x2, y2,
                                 fill=sc, width=2, capstyle="round")

        # ── Moon: circle with bite to form crescent ───────────────────
        if moon_alpha > 0.02:
            mr  = 7
            mc  = _interp(SURFACE, "#98989d", moon_alpha)
            self.create_oval(cx-mr, cy-mr, cx+mr, cy+mr, fill=mc, outline="")
            bx, by, br = cx + 3, cy - 2, 6
            self.create_oval(bx-br, by-br, bx+br, by+br,
                             fill=SURFACE, outline="")

# ── App ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UserVault")
        self.geometry("460x580")
        self.resizable(False, False)
        self.configure(bg=BG)
        ttk.Style().theme_use("default")

        self._current    = "LoginScreen"
        self._current_kw = {}
        self._animating  = False

        # Footer must be packed BEFORE the expand=True container so tkinter
        # reserves its space before the container claims everything.
        self._footer = tk.Frame(self, bg=BG)
        self._footer.pack(side="bottom", fill="x", padx=16, pady=6)
        self._footer_lbl = tk.Label(
            self._footer, text="SQLite3 + Tkinter  •  local auth demo",
            bg=BG, fg=MUTED, font=(FONT, 9))
        self._footer_lbl.pack(side="left")
        self._toggle_btn = ThemeToggle(self._footer, self._start_toggle)
        self._toggle_btn.config(bg=BG)
        self._toggle_btn.pack(side="right")

        self._container = tk.Frame(self, bg=BG)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self._frames = {}
        self._build_screens()
        self.show("LoginScreen")

    def _build_screens(self):
        for F in (LoginScreen, SignupScreen, WelcomeScreen, AdminScreen):
            f = F(self._container, self)
            self._frames[F.__name__] = f
            f.grid(row=0, column=0, sticky="nsew")

    def show(self, name, **kw):
        self._current    = name
        self._current_kw = kw
        f = self._frames[name]
        f.tkraise()
        if hasattr(f, "on_show"):
            f.on_show(**kw)

    def _start_toggle(self):
        if self._animating:
            return
        self._animating = True
        going_dark = not _dark
        TOTAL, MS = 20, 14   # ~280 ms total

        def step(i=0):
            # Icon morphs fully before theme snaps — no window transparency
            t_icon = (i / TOTAL) if going_dark else (1.0 - i / TOTAL)
            self._toggle_btn.draw(t_icon)
            if i < TOTAL:
                self.after(MS, lambda: step(i + 1))
            else:
                # Icon has finished morphing; now snap colours instantly
                self._apply_theme(going_dark)
                self._animating = False

        step()

    def _apply_theme(self, going_dark):
        global _dark, BG, SURFACE, BORDER, ACCENT, DANGER, SUCCESS, TEXT, MUTED
        _dark = going_dark
        th = DARK if going_dark else LIGHT
        BG, SURFACE, BORDER = th["BG"], th["SURFACE"], th["BORDER"]
        ACCENT, DANGER, SUCCESS = th["ACCENT"], th["DANGER"], th["SUCCESS"]
        TEXT, MUTED = th["TEXT"], th["MUTED"]

        # Update persistent chrome
        self.configure(bg=BG)
        self._container.configure(bg=BG)
        self._footer.configure(bg=BG)
        self._footer_lbl.configure(bg=BG, fg=MUTED)
        self._toggle_btn.configure(bg=BG)
        self._toggle_btn.draw(1.0 if going_dark else 0.0)

        for f in self._frames.values():
            f.destroy()
        self._frames = {}
        self._build_screens()
        self.show(self._current, **self._current_kw)

# ── Login screen ──────────────────────────────────────────────────────────────

class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=(FONT, 22, "bold")).pack(pady=(44, 4))
        tk.Label(self, text="Sign in to your account", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(pady=(0, 24))

        c = card(self)

        self.u = field(c, "USERNAME")
        self.p = field(c, "PASSWORD", show="*")
        self.p.bind("<Return>", lambda e: self._login())

        row = tk.Frame(c, bg=SURFACE)
        row.pack(fill="x", pady=(0, 8))
        self.remember_var = tk.BooleanVar()
        Checkbox(row, "Remember me", self.remember_var).pack(side="left")
        self.eye = tk.Label(row, text="Show password", bg=SURFACE, fg=MUTED,
                            font=(FONT, 9), cursor="hand2")
        self.eye.pack(side="right")
        self.eye.bind("<Button-1>", lambda e: self._toggle())

        self.err = err_label(c)
        btn(c, "SIGN  IN", ACCENT, self._login).pack(fill="x")

        row2 = tk.Frame(self, bg=BG)
        row2.pack(pady=16)
        tk.Label(row2, text="No account? ", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side="left")
        lnk = tk.Label(row2, text="Sign up", bg=BG, fg=ACCENT,
                       font=(FONT, 9), cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: app.show("SignupScreen"))

    def _toggle(self):
        showing = self.p.cget("show") == ""
        self.p.config(show="*" if showing else "")
        self.eye.config(text="Show password" if showing else "Hide password")

    def _login(self):
        u, p = self.u.get().strip(), self.p.get()
        self.err.config(text="")

        if not u or not p:
            self.err.config(text="All fields are required.")
            return

        ph = hash_pw(p)
        if u == ADMIN_USER and ph == ADMIN_HASH:
            save_remember(u) if self.remember_var.get() else clear_remember()
            self._clear()
            self.app.show("AdminScreen")
            return

        user = get_user(u)
        if not user or ph != user["password"]:
            self.err.config(text="Invalid username or password.")
            self.p.delete(0, "end")
            return

        save_remember(u) if self.remember_var.get() else clear_remember()
        self._clear()
        self.app.show("WelcomeScreen", username=user["username"],
                      email=user["email"], created_at=user["created_at"])

    def _clear(self):
        self.u.delete(0, "end")
        self.p.delete(0, "end")
        self.err.config(text="")

    def on_show(self, **kw):
        self.app.geometry("460x580")
        remembered = load_remember()
        self.u.delete(0, "end")
        if remembered:
            self.u.insert(0, remembered)
            self.remember_var.set(True)
        else:
            self.remember_var.set(False)
        self.p.delete(0, "end")
        self.err.config(text="")
        self.p.config(show="*")
        self.eye.config(text="Show password")

# ── Signup screen ─────────────────────────────────────────────────────────────

class SignupScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=(FONT, 22, "bold")).pack(pady=(32, 4))
        tk.Label(self, text="Create a new account", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(pady=(0, 18))

        c = card(self)

        self.u  = field(c, "USERNAME")
        self.e  = field(c, "EMAIL")
        self.p  = field(c, "PASSWORD", show="*")
        self.p.bind("<KeyRelease>", lambda e: self._update_strength())

        srow = tk.Frame(c, bg=SURFACE)
        srow.pack(fill="x", pady=(0, 10))
        self._strength_lbl = tk.Label(srow, text="", bg=SURFACE, fg=MUTED,
                                      font=(FONT, 8), width=8, anchor="e")
        self._strength_lbl.pack(side="right")
        bar_frame = tk.Frame(srow, bg=SURFACE)
        bar_frame.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._bars = []
        for _ in range(4):
            seg = tk.Frame(bar_frame, bg=BORDER, height=4)
            seg.pack(side="left", fill="x", expand=True, padx=(0, 3))
            self._bars.append(seg)

        self.cp = field(c, "CONFIRM PASSWORD", show="*")

        self.err = err_label(c)
        btn(c, "CREATE ACCOUNT", ACCENT, self._signup).pack(fill="x")

        lnk = tk.Label(c, text="Already have an account? Sign in",
                       bg=SURFACE, fg=ACCENT, font=(FONT, 9), cursor="hand2")
        lnk.pack(pady=(10, 0))
        lnk.bind("<Button-1>", lambda _: app.show("LoginScreen"))

    def _update_strength(self):
        bars, label, color = pw_strength(self.p.get())
        for i, seg in enumerate(self._bars):
            seg.config(bg=color if i < bars else BORDER)
        self._strength_lbl.config(text=label, fg=color)

    def _signup(self):
        u  = self.u.get().strip()
        e  = self.e.get().strip()
        p  = self.p.get()
        cp = self.cp.get()
        self.err.config(text="", fg=DANGER)

        if not all([u, e, p, cp]):
            self.err.config(text="All fields are required.")
            return
        if not EMAIL_RE.match(e):
            self.err.config(text="Please enter a valid email address.")
            return
        if p != cp:
            self.err.config(text="Passwords do not match.")
            self.cp.delete(0, "end")
            return
        if user_exists(u):
            self.err.config(text="That username is already in use.")
            return
        if email_exists(e):
            self.err.config(text="An account with that email already exists.")
            return

        insert_user(u, e, hash_pw(p))
        self.err.config(text="Account created! Redirecting…", fg=SUCCESS)
        self.after(1200, lambda: (self._clear(), self.app.show("LoginScreen")))

    def _clear(self):
        for w in (self.u, self.e, self.p, self.cp):
            w.delete(0, "end")
        self.err.config(text="")
        for seg in self._bars:
            seg.config(bg=BORDER)
        self._strength_lbl.config(text="")

    def on_show(self, **kw):
        self.app.geometry("460x640")
        self._clear()

# ── Welcome screen ────────────────────────────────────────────────────────────

class WelcomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=(FONT, 22, "bold")).pack(pady=(56, 4))
        tk.Label(self, text="●", bg=BG, fg=SUCCESS,
                 font=(FONT, 10)).pack()

        self.welcome = tk.Label(self, text="", bg=BG, fg=TEXT,
                                font=(FONT, 15, "bold"))
        self.welcome.pack(pady=(10, 4))

        c = card(self)
        tk.Label(c, text="ACCOUNT DETAILS", bg=SURFACE, fg=MUTED,
                 font=(FONT, 10), anchor="w").pack(fill="x")
        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", pady=8)

        def _row(label):
            f = tk.Frame(c, bg=SURFACE)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, bg=SURFACE, fg=MUTED,
                     font=(FONT, 9), width=14, anchor="w").pack(side="left")
            val = tk.Label(f, text="", bg=SURFACE, fg=TEXT, font=(FONT, 9))
            val.pack(side="left")
            return val

        self.username_val = _row("Username")
        self.email_val    = _row("Email")
        status_val        = _row("Status")
        status_val.config(text="Active", fg=SUCCESS)
        self.joined       = _row("Member since")

        btn(self, "SIGN  OUT", MUTED, lambda: app.show("LoginScreen")).pack(
            padx=50, fill="x", pady=20)

    def on_show(self, username="", email="", created_at="", **kw):
        self.welcome.config(text=f"Welcome back, {username}!")
        self.username_val.config(text=username)
        self.email_val.config(text=email)
        try:
            dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            self.joined.config(text=dt.strftime("%B %d, %Y"))
        except ValueError:
            self.joined.config(text=created_at)

# ── Admin screen ─────────────────────────────────────────────────────────────

class AdminScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        tk.Label(self, text="UserVault", bg=BG, fg=TEXT,
                 font=(FONT, 22, "bold")).pack(pady=(20, 2))

        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(hdr, text="Admin  •  User Database", bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side="left")
        sign_out_lbl = tk.Label(hdr, text="Sign out", bg=BG, fg=ACCENT,
                                font=(FONT, 9), cursor="hand2")
        sign_out_lbl.pack(side="right")
        sign_out_lbl.bind("<Button-1>", lambda _: app.show("LoginScreen"))

        style = ttk.Style()
        style.configure("Admin.Treeview",
                        background=SURFACE, foreground=TEXT,
                        fieldbackground=SURFACE, borderwidth=0,
                        rowheight=26, font=(FONT, 9))
        style.configure("Admin.Treeview.Heading",
                        background=BORDER, foreground=MUTED,
                        font=(FONT, 9, "bold"), relief="flat")
        style.map("Admin.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        wrapper = tk.Frame(self, bg=BORDER, height=185)
        wrapper.pack(padx=20, fill="x")
        wrapper.pack_propagate(False)

        cols = ("id", "username", "email", "created_at")
        self.tree = ttk.Treeview(wrapper, columns=cols, show="headings",
                                  style="Admin.Treeview", selectmode="browse")
        self.tree.heading("id",         text="ID",         anchor="w")
        self.tree.heading("username",   text="USERNAME",   anchor="w")
        self.tree.heading("email",      text="EMAIL",      anchor="w")
        self.tree.heading("created_at", text="CREATED AT", anchor="w")
        self.tree.column("id",         width=36,  stretch=False, anchor="center")
        self.tree.column("username",   width=110, stretch=False)
        self.tree.column("email",      width=210, stretch=True)
        self.tree.column("created_at", width=150, stretch=False)

        sb = ttk.Scrollbar(wrapper, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.count_lbl = tk.Label(self, text="", bg=BG, fg=MUTED, font=(FONT, 9))
        self.count_lbl.pack(pady=(5, 0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(8, 4))

        add_panel = tk.Frame(self, bg=SURFACE, highlightthickness=1,
                             highlightbackground=BORDER)
        add_panel.pack(padx=20, fill="x")
        add_inner = tk.Frame(add_panel, bg=SURFACE)
        add_inner.pack(padx=16, pady=10, fill="x")

        tk.Label(add_inner, text="ADD USER", bg=SURFACE, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 4))

        self.new_u = field(add_inner, "USERNAME")
        self.new_e = field(add_inner, "EMAIL")
        self.new_p = field(add_inner, "PASSWORD", show="*")

        self.add_err = tk.Label(self, text="", bg=BG, fg=DANGER,
                                font=(FONT, 9), wraplength=500, anchor="w")
        self.add_err.pack(padx=20, fill="x", pady=(6, 0))

        def _btn_row(pairs, pady):
            row = tk.Frame(self, bg=BG)
            row.pack(padx=20, fill="x", pady=pady)
            for text, color, cmd in pairs:
                f = tk.Frame(row, bg=BG)
                f.pack(side="left", fill="x", expand=True, padx=(0, 4))
                btn(f, text, color, cmd).pack(fill="x")

        _btn_row([
            ("ADD USER",        ACCENT, self._add_user),
            ("DELETE SELECTED", DANGER, self._delete_user),
        ], pady=(4, 4))
        _btn_row([
            ("REFRESH",    MUTED,   self._load),
            ("EXPORT CSV", SUCCESS, self._export_csv),
        ], pady=(0, 10))

    def _add_user(self):
        u = self.new_u.get().strip()
        e = self.new_e.get().strip()
        p = self.new_p.get()
        self.add_err.config(text="", fg=DANGER)

        if not u or not e or not p:
            self.add_err.config(text="All fields are required.")
            return
        if not EMAIL_RE.match(e):
            self.add_err.config(text="Please enter a valid email address.")
            return
        if user_exists(u):
            self.add_err.config(text=f"Username '{u}' is already in use.")
            return
        if email_exists(e):
            self.add_err.config(text="That email is already registered.")
            return

        insert_user(u, e, hash_pw(p))
        self.new_u.delete(0, "end")
        self.new_e.delete(0, "end")
        self.new_p.delete(0, "end")
        self.add_err.config(text=f"User '{u}' added successfully.", fg=SUCCESS)
        self._load()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="users_export.csv",
            title="Export users")
        if not path:
            return
        rows = get_all_users()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "USERNAME", "EMAIL", "CREATED AT"])
            for r in rows:
                writer.writerow([r["id"], r["username"], r["email"], r["created_at"]])
        self.add_err.config(text=f"Exported {len(rows)} user(s) to {path}", fg=SUCCESS)

    def _delete_user(self):
        sel = self.tree.selection()
        if not sel:
            return
        username = self.tree.item(sel[0])["values"][1]
        with sqlite3.connect(DB) as c:
            c.execute("DELETE FROM users WHERE username=?", (username,))
        self.add_err.config(text=f"User '{username}' removed.", fg=MUTED)
        self._load()

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = get_all_users()
        for r in rows:
            self.tree.insert("", "end",
                             values=(r["id"], r["username"], r["email"], r["created_at"]))
        n = len(rows)
        self.count_lbl.config(text=f"{n} user{'s' if n != 1 else ''} in database")

    def on_show(self, **kw):
        self.app.geometry("560x800")
        self._load()

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    App().mainloop()
