import tkinter as tk
from ui.theme import BG, TEXT, FONT_SMALL, MUTED


class App(tk.Tk):
    """
    Root window and frame controller.
    Manages swapping between Sign In, Sign Up, and Dashboard frames
    without ever opening a new window.
    """

    def __init__(self):
        super().__init__()
        self.title("UserVault")
        self.geometry("460x560")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Container that all frames live inside
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Import here to avoid circular imports
        from ui.login_frame   import LoginFrame
        from ui.signup_frame  import SignupFrame
        from ui.welcome_frame import WelcomeFrame

        self._frames: dict[str, tk.Frame] = {}
        for FrameClass in (LoginFrame, SignupFrame, WelcomeFrame):
            name = FrameClass.__name__
            frame = FrameClass(parent=container, controller=self)
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Footer
        footer = tk.Label(
            self,
            text="UserVault — local auth demo  •  SQLite3 + Tkinter",
            bg=BG,
            fg=MUTED,
            font=FONT_SMALL,
        )
        footer.pack(side="bottom", pady=6)

        self.show_frame("LoginFrame")

    def show_frame(self, name: str, **kwargs):
        """Raise the named frame to the top. Pass kwargs to its on_show() hook."""
        frame = self._frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show(**kwargs)
