import customtkinter as ctk
from database.db_manager import init_db
from views.dashboard_view import DashboardView
from views.kandidati_view import KandidatiView
from views.instruktori_view import InstruktoriView
from views.casovi_view import CasoviView
from views.ispiti_view import IspitiView

# ── Tema ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AutoSkolaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Škola — Upravljanje")
        self.geometry("1100x700")
        self.minsize(900, 600)

        init_db()
        self._aktivni_view = None
        self._dugmad = {}

        self._build_ui()
        self._prikazi("dashboard")

    def _build_ui(self):
        # ── Sidebar ─────────────────────────────────────────────────────────
        self._sidebar = ctk.CTkFrame(self, width=210, corner_radius=0,
                                     fg_color="#1a1a2e")
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Logo / naziv
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(24, 8), padx=16)

        ctk.CTkLabel(logo_frame, text="🚗",
                     font=ctk.CTkFont(size=32)).pack(side="left")
        ctk.CTkLabel(logo_frame, text="Auto Škola",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(side="left", padx=8)

        sep = ctk.CTkFrame(self._sidebar, height=1, fg_color="#333355")
        sep.pack(fill="x", padx=16, pady=(0, 16))

        # Navigaciona dugmad
        stavke = [
            ("dashboard",    "🏠  Dashboard",    DashboardView),
            ("kandidati",    "👤  Kandidati",     KandidatiView),
            ("instruktori",  "👨‍🏫  Instruktori",   InstruktoriView),
            ("casovi",       "📅  Časovi",         CasoviView),
            ("ispiti",       "📝  Ispiti",         IspitiView),
        ]

        self._view_klase = {k: v for k, _, v in stavke}

        for kljuc, tekst, _ in stavke:
            btn = ctk.CTkButton(
                self._sidebar,
                text=tekst,
                anchor="w",
                fg_color="transparent",
                hover_color="#2a2a4e",
                text_color="white",
                font=ctk.CTkFont(size=14),
                height=42,
                corner_radius=8,
                command=lambda k=kljuc: self._prikazi(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._dugmad[kljuc] = btn

        # Verzija na dnu
        ctk.CTkLabel(self._sidebar, text="v1.0.0",
                     text_color="#555577",
                     font=ctk.CTkFont(size=11)).pack(side="bottom", pady=16)

        # ── Glavni sadržaj ───────────────────────────────────────────────────
        self._content = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e2e")
        self._content.pack(side="left", fill="both", expand=True)

        self._view_instanci = {}

    def _prikazi(self, kljuc: str):
        # Sakrij stari view
        if self._aktivni_view:
            self._aktivni_view.pack_forget()

        # Resetuj stil svih dugmadi
        for k, btn in self._dugmad.items():
            btn.configure(fg_color="#1a73e8" if k == kljuc else "transparent")

        # Kreiraj view ako ne postoji
        if kljuc not in self._view_instanci:
            klasa = self._view_klase[kljuc]
            self._view_instanci[kljuc] = klasa(self._content)

        view = self._view_instanci[kljuc]

        # Osvezi podatke ako view ima osvezi() metodu
        if hasattr(view, "osvezi"):
            view.osvezi()

        view.pack(fill="both", expand=True)
        self._aktivni_view = view


if __name__ == "__main__":
    app = AutoSkolaApp()
    app.mainloop()
