# Shared colour palette and font constants used across all UI frames.

BG        = "#0f1117"   # near-black background
SURFACE   = "#1a1d27"   # card/panel surface
BORDER    = "#2a2d3a"   # subtle border colour
ACCENT    = "#4f8ef7"   # blue accent
ACCENT_HV = "#3a78e0"   # accent on hover
SUCCESS   = "#3ecf8e"   # green for success states
DANGER    = "#f75f5f"   # red for errors
TEXT      = "#e8eaf0"   # primary text
MUTED     = "#6b7280"   # secondary / placeholder text

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_LABEL  = ("Courier", 10)
FONT_ENTRY  = ("Courier", 11)
FONT_BTN    = ("Courier", 10, "bold")
FONT_SMALL  = ("Courier", 9)

ENTRY_OPTS = dict(
    bg=SURFACE,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    font=FONT_ENTRY,
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=ACCENT,
)

PAD = 12   # standard padding unit
