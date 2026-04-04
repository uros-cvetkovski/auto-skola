import customtkinter as ctk
from PIL import Image
import os
from models.kandidat import Kandidat
from models.instruktor import Instruktor
from models.cas_ispit import Cas, Ispit

BG_PRIMARY     = "#020617"
BG_CARD        = "#0f172a"
BORDER_DARK    = "#1e293b"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#64748b"

BLUE      = "#3b82f6"
BLUE_BG   = "#1e3a5f"
GREEN     = "#22c55e"
GREEN_BG  = "#14532d"
AMBER     = "#f59e0b"
AMBER_BG  = "#78350f"
RED       = "#ef4444"
RED_BG    = "#7f1d1d"

ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

def load_icon(name: str, size=(22, 22)):
    path = os.path.join(ICONS_DIR, f"{name}.png")
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._ikone = {
            "kandidati":   load_icon("kandidati"),
            "polozili":    load_icon("kandidati"),
            "instruktori": load_icon("instruktori"),
            "casovi":      load_icon("casovi"),
        }

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 24))
        ctk.CTkLabel(header, text="Dashboard",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Pregled stanja auto škole",
                     font=ctk.CTkFont(family="Arial", size=14),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=BORDER_DARK)
        scroll.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 32))
        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        kartice_data = [
            (self._ikone["kandidati"],   "Aktivni kandidati", self._aktivni_kandidati(), BLUE,  BLUE_BG),
            (self._ikone["polozili"],    "Položili",          self._polozili(),           GREEN, GREEN_BG),
            (self._ikone["instruktori"], "Instruktori",       self._aktivni_instruktori(), AMBER, AMBER_BG),
            (self._ikone["casovi"],      "Časovi danas",      self._casovi_danas(),       RED,   RED_BG),
        ]

        for col, (ikona, label, vrednost, boja, boja_bg) in enumerate(kartice_data):
            self._stat_kartica(scroll, ikona, label, vrednost, boja, boja_bg, col)

        donji = ctk.CTkFrame(scroll, fg_color="transparent")
        donji.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(24, 0))
        donji.grid_columnconfigure((0, 1), weight=1, uniform="col")

        self._kartica_statusi(donji)
        self._kartica_ispiti(donji)

    def _aktivni_kandidati(self):
        try:
            return str(Kandidat.broj_po_statusu().get("aktivan", 0))
        except Exception:
            return "0"

    def _polozili(self):
        try:
            return str(Kandidat.broj_po_statusu().get("polozio", 0))
        except Exception:
            return "0"

    def _aktivni_instruktori(self):
        try:
            return str(len(Instruktor.get_all(samo_aktivni=True)))
        except Exception:
            return "0"

    def _casovi_danas(self):
        try:
            from datetime import date
            danas = date.today().isoformat()
            return str(sum(1 for c in Cas.get_all()
                           if c.datum == danas and c.status == "zakazan"))
        except Exception:
            return "0"

    def _stat_kartica(self, parent, ikona, label, vrednost, boja, boja_bg, col):
        kartica = ctk.CTkFrame(parent, fg_color=BG_CARD,
                               border_color=BORDER_DARK, border_width=1,
                               corner_radius=12)
        kartica.grid(row=0, column=col,
                     padx=(0 if col == 0 else 12, 0), pady=0, sticky="ew")

        inner = ctk.CTkFrame(kartica, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        # Ikonica u obojenoj kutiji
        ikon_frame = ctk.CTkFrame(inner, width=48, height=48,
                                  fg_color=boja_bg, corner_radius=8)
        ikon_frame.pack(anchor="w")
        ikon_frame.pack_propagate(False)

        if ikona:
            ctk.CTkLabel(ikon_frame, text="", image=ikona).pack(expand=True)
        else:
            ctk.CTkLabel(ikon_frame, text="●",
                         font=ctk.CTkFont(size=20),
                         text_color=boja).pack(expand=True)

        ctk.CTkLabel(inner, text=vrednost,
                     font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(12, 4))

        ctk.CTkLabel(inner, text=label,
                     font=ctk.CTkFont(family="Arial", size=12),
                     text_color=TEXT_SECONDARY).pack(anchor="w")

    def _kartica_statusi(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_CARD,
                             border_color=BORDER_DARK, border_width=1,
                             corner_radius=12)
        frame.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        ctk.CTkLabel(frame, text="Kandidati po statusu",
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 16))
        ctk.CTkFrame(frame, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=24)

        try:
            statusi = Kandidat.broj_po_statusu()
            boje   = {"aktivan": BLUE, "polozio": GREEN, "odustao": RED}
            labele = {"aktivan": "Aktivni", "polozio": "Položili", "odustao": "Odustali"}
            if statusi:
                for status, broj in statusi.items():
                    red = ctk.CTkFrame(frame, fg_color="transparent")
                    red.pack(fill="x", padx=24, pady=8)
                    levo = ctk.CTkFrame(red, fg_color="transparent")
                    levo.pack(side="left", fill="x", expand=True)
                    ind = ctk.CTkFrame(levo, width=10, height=10, corner_radius=5,
                                       fg_color=boje.get(status, TEXT_MUTED))
                    ind.pack(side="left", padx=(0, 10))
                    ind.pack_propagate(False)
                    ctk.CTkLabel(levo, text=labele.get(status, status),
                                 font=ctk.CTkFont(family="Arial", size=14),
                                 text_color=TEXT_SECONDARY).pack(side="left")
                    ctk.CTkLabel(red, text=str(broj),
                                 font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                                 text_color=TEXT_PRIMARY).pack(side="right")
            else:
                ctk.CTkLabel(frame, text="Nema podataka",
                             font=ctk.CTkFont(family="Arial", size=14),
                             text_color=TEXT_MUTED).pack(pady=40)
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Greška: {e}", text_color=RED).pack(pady=20)

        ctk.CTkFrame(frame, height=1).pack(fill="x", padx=24, pady=(8, 24))

    def _kartica_ispiti(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=BG_CARD,
                             border_color=BORDER_DARK, border_width=1,
                             corner_radius=12)
        frame.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        ctk.CTkLabel(frame, text="Poslednji ispiti",
                     font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(24, 16))
        ctk.CTkFrame(frame, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=24)

        try:
            ispiti = list(reversed(Ispit.get_all()[-5:]))
            boje_r = {"polozio": GREEN, "pao": RED, "ceka": AMBER}
            if ispiti:
                for ispit in ispiti:
                    red = ctk.CTkFrame(frame, fg_color="transparent")
                    red.pack(fill="x", padx=24, pady=8)
                    ime = f"{ispit.kandidat_ime or ''} {ispit.kandidat_prezime or ''}".strip() \
                          or f"ID {ispit.kandidat_id}"
                    ctk.CTkLabel(red, text=ime,
                                 font=ctk.CTkFont(family="Arial", size=14),
                                 text_color=TEXT_SECONDARY).pack(side="left")
                    boja = boje_r.get(ispit.rezultat, TEXT_MUTED)
                    ctk.CTkLabel(red, text=ispit.rezultat.upper(),
                                 font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                                 text_color=boja).pack(side="right")
            else:
                ctk.CTkLabel(frame, text="Nema ispita",
                             font=ctk.CTkFont(family="Arial", size=14),
                             text_color=TEXT_MUTED).pack(pady=40)
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Greška: {e}", text_color=RED).pack(pady=20)

        ctk.CTkFrame(frame, height=1).pack(fill="x", padx=24, pady=(8, 24))

    def osvezi(self):
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()