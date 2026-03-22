import customtkinter as ctk
from models.kandidat import Kandidat
from models.instruktor import Instruktor
from models.cas_ispit import Cas, Ispit


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()

    def _build_ui(self):
        # Naslov
        naslov = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        naslov.pack(anchor="w", padx=30, pady=(30, 5))

        podnaslov = ctk.CTkLabel(
            self,
            text="Pregled stanja auto škole",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        podnaslov.pack(anchor="w", padx=30, pady=(0, 25))

        # Grid za kartice
        kartice_frame = ctk.CTkFrame(self, fg_color="transparent")
        kartice_frame.pack(fill="x", padx=30)

        kartice_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self._stat_kartica(kartice_frame, "👤 Aktivni kandidati", self._aktivni_kandidati(), "#1a73e8", 0)
        self._stat_kartica(kartice_frame, "✅ Položili", self._polozili(), "#0f9d58", 1)
        self._stat_kartica(kartice_frame, "👨‍🏫 Instruktori", self._aktivni_instruktori(), "#f4b400", 2)
        self._stat_kartica(kartice_frame, "📅 Časovi danas", self._casovi_danas(), "#db4437", 3)

        # Separator
        sep = ctk.CTkFrame(self, height=2, fg_color="#e0e0e0")
        sep.pack(fill="x", padx=30, pady=25)

        # Donji red — kandidati po statusu + poslednji ispiti
        donji_frame = ctk.CTkFrame(self, fg_color="transparent")
        donji_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        donji_frame.columnconfigure(0, weight=1)
        donji_frame.columnconfigure(1, weight=1)

        self._kartica_statusi(donji_frame)
        self._kartica_ispiti(donji_frame)

    # ── Pomocne metode za podatke ───────────────────────────────────────────

    def _aktivni_kandidati(self):
        try:
            statusi = Kandidat.broj_po_statusu()
            return str(statusi.get("aktivan", 0))
        except Exception:
            return "—"

    def _polozili(self):
        try:
            statusi = Kandidat.broj_po_statusu()
            return str(statusi.get("polozio", 0))
        except Exception:
            return "—"

    def _aktivni_instruktori(self):
        try:
            return str(len(Instruktor.get_all(samo_aktivni=True)))
        except Exception:
            return "—"

    def _casovi_danas(self):
        try:
            from datetime import date
            danas = date.today().isoformat()
            svi = Cas.get_all()
            return str(sum(1 for c in svi if c.datum == danas and c.status == "zakazan"))
        except Exception:
            return "—"

    # ── Gradnja kartica ─────────────────────────────────────────────────────

    def _stat_kartica(self, parent, tekst, vrednost, boja, col):
        kartica = ctk.CTkFrame(parent, corner_radius=12, fg_color=boja)
        kartica.grid(row=0, column=col, padx=8, pady=8, sticky="ew")

        ctk.CTkLabel(
            kartica,
            text=vrednost,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            kartica,
            text=tekst,
            font=ctk.CTkFont(size=13),
            text_color="white"
        ).pack(pady=(0, 18))

    def _kartica_statusi(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        ctk.CTkLabel(
            frame,
            text="Kandidati po statusu",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 10))

        try:
            statusi = Kandidat.broj_po_statusu()
            boje = {"aktivan": "#1a73e8", "polozio": "#0f9d58", "odustao": "#db4437"}
            labele = {"aktivan": "Aktivni", "polozio": "Položili", "odustao": "Odustali"}

            for status, broj in statusi.items():
                red = ctk.CTkFrame(frame, fg_color="transparent")
                red.pack(fill="x", padx=20, pady=4)

                boja = boje.get(status, "#888888")
                ind = ctk.CTkFrame(red, width=12, height=12, corner_radius=6, fg_color=boja)
                ind.pack(side="left", padx=(0, 8))

                ctk.CTkLabel(red, text=labele.get(status, status),
                             font=ctk.CTkFont(size=13)).pack(side="left")
                ctk.CTkLabel(red, text=str(broj),
                             font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

            if not statusi:
                ctk.CTkLabel(frame, text="Nema podataka", text_color="gray").pack(pady=10)

        except Exception as e:
            ctk.CTkLabel(frame, text=f"Greška: {e}", text_color="red").pack(pady=10)

        ctk.CTkFrame(frame, height=1).pack(fill="x", padx=20, pady=(10, 18))

    def _kartica_ispiti(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        ctk.CTkLabel(
            frame,
            text="Poslednji ispiti",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 10))

        try:
            ispiti = Ispit.get_all()
            poslednji = ispiti[-5:] if len(ispiti) >= 5 else ispiti
            poslednji = list(reversed(poslednji))

            boje_rezultat = {"polozio": "#0f9d58", "pao": "#db4437", "ceka": "#f4b400"}

            for ispit in poslednji:
                red = ctk.CTkFrame(frame, fg_color="transparent")
                red.pack(fill="x", padx=20, pady=3)

                ime = f"{ispit.kandidat_ime or ''} {ispit.kandidat_prezime or ''}".strip() or f"ID {ispit.kandidat_id}"
                ctk.CTkLabel(red, text=ime,
                             font=ctk.CTkFont(size=12)).pack(side="left")

                boja = boje_rezultat.get(ispit.rezultat, "#888888")
                ctk.CTkLabel(red, text=ispit.rezultat.upper(),
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=boja).pack(side="right")

            if not poslednji:
                ctk.CTkLabel(frame, text="Nema ispita", text_color="gray").pack(pady=10)

        except Exception as e:
            ctk.CTkLabel(frame, text=f"Greška: {e}", text_color="red").pack(pady=10)

        ctk.CTkFrame(frame, height=1).pack(fill="x", padx=20, pady=(10, 18))

    def osvezi(self):
        """Poziva se kada se vrati na dashboard — rebuilds UI sa svežim podacima."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
