import customtkinter as ctk
from database.db_manager import init_db
from views.dashboard_view import DashboardView
from views.kandidati_view import KandidatiView
from views.instruktori_view import InstruktoriView
from views.casovi_view import CasoviView
from views.ispiti_view import IspitiView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_PRIMARY     = "#020617"
BG_SIDEBAR     = "#0f172a"
BORDER_DARK    = "#1e293b"
ACCENT_BLUE    = "#3b82f6"
ACCENT_HOVER   = "#2563eb"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#64748b"


class AutoSkolaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Škola — Upravljanje")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        self.configure(fg_color=BG_PRIMARY)

        init_db()

        self._aktivni_kljuc = None
        self._dugmad = {}
        self._view_instanci = {}

        self._build_ui()
        self._prikazi("dashboard")

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──────────────────────────────────────────────────────────
        self._sidebar = ctk.CTkFrame(self, width=264, fg_color=BG_SIDEBAR,
                                     corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(2, weight=1)
        self._sidebar.grid_columnconfigure(0, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))

        ikonica_frame = ctk.CTkFrame(logo_frame, width=40, height=40,
                                     fg_color=ACCENT_BLUE, corner_radius=8)
        ikonica_frame.pack(side="left")
        ikonica_frame.pack_propagate(False)
        ctk.CTkLabel(ikonica_frame, text="🚗",
                     font=ctk.CTkFont(size=20)).pack(expand=True)

        ctk.CTkLabel(logo_frame, text="Auto Škola",
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=12)

        # Separator
        ctk.CTkFrame(self._sidebar, height=1, fg_color=BORDER_DARK).grid(
            row=1, column=0, sticky="ew", padx=24, pady=20)

        # Nav dugmad
        nav_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="nsew", padx=16)

        stavke = [
            ("dashboard",   "🏠   Dashboard"),
            ("kandidati",   "👤   Kandidati"),
            ("instruktori", "👨‍🏫   Instruktori"),
            ("casovi",      "📅   Časovi"),
            ("ispiti",      "📝   Ispiti"),
        ]

        self._view_klase = {
            "dashboard":   DashboardView,
            "kandidati":   KandidatiView,
            "instruktori": InstruktoriView,
            "casovi":      CasoviView,
            "ispiti":      IspitiView,
        }

        for kljuc, tekst in stavke:
            btn = ctk.CTkButton(
                nav_frame,
                text=tekst,
                anchor="w",
                fg_color="transparent",
                hover_color=BORDER_DARK,
                text_color=TEXT_SECONDARY,
                font=ctk.CTkFont(family="Arial", size=14),
                height=44,
                corner_radius=8,
                command=lambda k=kljuc: self._prikazi(k)
            )
            btn.pack(fill="x", pady=2)
            self._dugmad[kljuc] = btn

        # Verzija
        ctk.CTkLabel(self._sidebar, text="v1.0.0",
                     text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family="Arial", size=12)).grid(
            row=3, column=0, pady=24)

        # ── Main content ─────────────────────────────────────────────────────
        self._content = ctk.CTkFrame(self, fg_color=BG_PRIMARY, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

    def _prikazi(self, kljuc: str):
        for widget in self._content.winfo_children():
            widget.grid_forget()

        for k, btn in self._dugmad.items():
            if k == kljuc:
                btn.configure(fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                              text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", hover_color=BORDER_DARK,
                              text_color=TEXT_SECONDARY)

        if kljuc not in self._view_instanci:
            klasa = self._view_klase[kljuc]
            self._view_instanci[kljuc] = klasa(self._content)

        view = self._view_instanci[kljuc]
        if hasattr(view, "osvezi"):
            view.osvezi()

        view.grid(row=0, column=0, sticky="nsew")
        self._aktivni_kljuc = kljuc


if __name__ == "__main__":
    app = AutoSkolaApp()
    app.mainloop()
