import customtkinter as ctk
from tkinter import ttk, messagebox
from models.cas_ispit import Ispit
from models.kandidat import Kandidat

BG_PRIMARY     = "#020617"
BG_CARD        = "#0f172a"
BORDER_DARK    = "#1e293b"
BORDER_LIGHT   = "#334155"
ACCENT_BLUE    = "#3b82f6"
ACCENT_HOVER   = "#2563eb"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#64748b"
RED            = "#ef4444"
RED_HOVER      = "#dc2626"


class IspitiView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 0))
        ctk.CTkLabel(header, text="Ispiti",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=32, pady=(16, 0))

        ctk.CTkLabel(toolbar, text="Tip:",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        self._filter_tip = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(toolbar,
                               values=["Svi", "teorija", "praksa"],
                               variable=self._filter_tip,
                               fg_color=BG_CARD,
                               selected_color=ACCENT_BLUE,
                               selected_hover_color=ACCENT_HOVER,
                               unselected_color=BG_CARD,
                               unselected_hover_color=BORDER_DARK,
                               text_color=TEXT_PRIMARY,
                               command=lambda _: self._ucitaj_podatke()).pack(side="left")

        ctk.CTkLabel(toolbar, text="Rezultat:",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(16, 6))
        self._filter_rezultat = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(toolbar,
                               values=["Svi", "ceka", "polozio", "pao"],
                               variable=self._filter_rezultat,
                               fg_color=BG_CARD,
                               selected_color=ACCENT_BLUE,
                               selected_hover_color=ACCENT_HOVER,
                               unselected_color=BG_CARD,
                               unselected_hover_color=BORDER_DARK,
                               text_color=TEXT_PRIMARY,
                               command=lambda _: self._ucitaj_podatke()).pack(side="left")

        ctk.CTkButton(toolbar, text="+ Dodaj ispit", width=150,
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY,
                      font=ctk.CTkFont(family="Arial", size=14),
                      height=40, corner_radius=8,
                      command=self._otvori_formu_novi).pack(side="right")

        tabela_frame = ctk.CTkFrame(self, fg_color=BG_CARD,
                                    border_color=BORDER_DARK, border_width=1,
                                    corner_radius=12)
        tabela_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=(16, 0))
        tabela_frame.grid_rowconfigure(0, weight=1)
        tabela_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG_CARD, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD, rowheight=36,
                        font=("Arial", 12), borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BORDER_DARK, foreground=TEXT_SECONDARY,
                        font=("Arial", 12, "bold"), borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", TEXT_PRIMARY)])

        kolone = ("ID", "Kandidat", "Tip", "Datum", "Rezultat", "Napomena")
        self._tabela = ttk.Treeview(tabela_frame, columns=kolone,
                                    show="headings", selectmode="browse")
        sirine = {"ID": 45, "Kandidat": 210, "Tip": 90,
                  "Datum": 110, "Rezultat": 100, "Napomena": 230}
        for k in kolone:
            self._tabela.heading(k, text=k)
            self._tabela.column(k, width=sirine[k], anchor="center")

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical",
                                  command=self._tabela.yview)
        self._tabela.configure(yscrollcommand=scrollbar.set)
        self._tabela.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))

        self._tabela.bind("<<TreeviewSelect>>", self._na_selekciju)
        self._tabela.bind("<Double-1>", lambda _: self._otvori_formu_edit())

        dno = ctk.CTkFrame(self, fg_color="transparent")
        dno.grid(row=3, column=0, sticky="ew", padx=32, pady=(12, 24))

        self._btn_edit = ctk.CTkButton(dno, text="Izmeni", width=120,
                                       fg_color=BORDER_LIGHT, hover_color=BORDER_DARK,
                                       text_color=TEXT_PRIMARY, height=38,
                                       corner_radius=8, state="disabled",
                                       command=self._otvori_formu_edit)
        self._btn_edit.pack(side="left", padx=(0, 8))

        self._btn_obrisi = ctk.CTkButton(dno, text="Obrisi", width=120,
                                          fg_color=RED, hover_color=RED_HOVER,
                                          text_color=TEXT_PRIMARY, height=38,
                                          corner_radius=8, state="disabled",
                                          command=self._obrisi)
        self._btn_obrisi.pack(side="left")

        self._lbl_ukupno = ctk.CTkLabel(dno, text="", text_color=TEXT_MUTED,
                                         font=ctk.CTkFont(family="Arial", size=12))
        self._lbl_ukupno.pack(side="right")

    def _ucitaj_podatke(self):
        self._tabela.delete(*self._tabela.get_children())
        ispiti = Ispit.get_all()
        ft = self._filter_tip.get()
        fr = self._filter_rezultat.get()
        if ft != "Svi":
            ispiti = [i for i in ispiti if i.tip == ft]
        if fr != "Svi":
            ispiti = [i for i in ispiti if i.rezultat == fr]
        for ispit in ispiti:
            ime = f"{ispit.kandidat_ime or ''} {ispit.kandidat_prezime or ''}".strip() \
                  or f"ID {ispit.kandidat_id}"
            self._tabela.insert("", "end", iid=str(ispit.id), values=(
                ispit.id, ime, ispit.tip or "—",
                ispit.datum or "—", ispit.rezultat or "—",
                ispit.napomena or ""
            ))
        self._lbl_ukupno.configure(text=f"Ukupno: {len(ispiti)}")
        self._izabrani_id = None
        self._btn_edit.configure(state="disabled")
        self._btn_obrisi.configure(state="disabled")

    def _na_selekciju(self, event=None):
        sel = self._tabela.selection()
        if sel:
            self._izabrani_id = int(sel[0])
            self._btn_edit.configure(state="normal")
            self._btn_obrisi.configure(state="normal")
        else:
            self._izabrani_id = None
            self._btn_edit.configure(state="disabled")
            self._btn_obrisi.configure(state="disabled")

    def _otvori_formu_novi(self):
        self._otvori_formu(None)

    def _otvori_formu_edit(self):
        if self._izabrani_id:
            self._otvori_formu(self._izabrani_id)

    def _otvori_formu(self, ispit_id):
        ispit = Ispit.get_by_id(ispit_id) if ispit_id else None
        je_novi = ispit is None

        prozor = ctk.CTkToplevel(self)
        prozor.title("Novi ispit" if je_novi else "Izmena ispita")
        prozor.geometry("480x580")
        prozor.resizable(False, True)
        prozor.configure(fg_color=BG_PRIMARY)
        prozor.grab_set()
        prozor.lift()
        prozor.focus_force()

        ctk.CTkLabel(prozor,
                     text="Novi ispit" if je_novi else "Izmena ispita",
                     font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(prozor, text="Popunite podatke o ispitu",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=32)
        ctk.CTkFrame(prozor, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=32, pady=(16, 0))

        forma = ctk.CTkScrollableFrame(prozor, fg_color="transparent",
                                        scrollbar_button_color=BORDER_DARK)
        forma.pack(fill="both", expand=True, padx=32, pady=(12, 0))
        forma.grid_columnconfigure(0, weight=1)

        # Kandidat
        kandidati = Kandidat.get_all()
        kandidat_opcije = [f"{k.id} — {k.ime} {k.prezime}" for k in kandidati]

        ctk.CTkLabel(forma, text="Kandidat *", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        kandidat_var = ctk.StringVar()
        if ispit:
            for k in kandidati:
                if k.id == ispit.kandidat_id:
                    kandidat_var.set(f"{k.id} — {k.ime} {k.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=kandidat_var,
                          values=kandidat_opcije if kandidat_opcije else ["—"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(forma, text="Tip ispita *", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 4))
        tip_var = ctk.StringVar(value=ispit.tip if ispit else "teorija")
        ctk.CTkOptionMenu(forma, variable=tip_var,
                          values=["teorija", "praksa"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(forma, text="Datum (YYYY-MM-DD) *", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=4, column=0, sticky="w", pady=(0, 4))
        e_datum = ctk.CTkEntry(forma, height=40,
                                fg_color=BG_CARD, border_color=BORDER_DARK,
                                text_color=TEXT_PRIMARY)
        e_datum.grid(row=5, column=0, sticky="ew", pady=(0, 12))
        if ispit and ispit.datum:
            e_datum.insert(0, ispit.datum)

        ctk.CTkLabel(forma, text="Rezultat", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=6, column=0, sticky="w", pady=(0, 4))
        rezultat_var = ctk.StringVar(value=ispit.rezultat if ispit else "ceka")
        ctk.CTkOptionMenu(forma, variable=rezultat_var,
                          values=["ceka", "polozio", "pao"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=7, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(forma, text="Napomena", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=8, column=0, sticky="w", pady=(0, 4))
        e_napomena = ctk.CTkEntry(forma, height=40,
                                   fg_color=BG_CARD, border_color=BORDER_DARK,
                                   text_color=TEXT_PRIMARY)
        e_napomena.grid(row=9, column=0, sticky="ew", pady=(0, 12))
        if ispit and ispit.napomena:
            e_napomena.insert(0, ispit.napomena)

        ctk.CTkFrame(prozor, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=32, pady=(8, 0))

        dugmad_frame = ctk.CTkFrame(prozor, fg_color="transparent")
        dugmad_frame.pack(fill="x", padx=32, pady=16)
        dugmad_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(dugmad_frame, text="Otkazi",
                      fg_color=BORDER_DARK, hover_color=BORDER_LIGHT,
                      text_color=TEXT_PRIMARY, height=44, corner_radius=8,
                      font=ctk.CTkFont(family="Arial", size=14),
                      command=prozor.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        def sacuvaj():
            if not kandidat_var.get() or kandidat_var.get() == "—":
                messagebox.showerror("Greska", "Izaberite kandidata!", parent=prozor)
                return
            datum = e_datum.get().strip()
            if not datum:
                messagebox.showerror("Greska", "Datum je obavezan!", parent=prozor)
                return
            kandidat_id = int(kandidat_var.get().split(" — ")[0])
            isp = ispit if ispit else Ispit()
            isp.kandidat_id = kandidat_id
            isp.tip         = tip_var.get()
            isp.datum       = datum
            isp.rezultat    = rezultat_var.get()
            isp.napomena    = e_napomena.get().strip() or None
            try:
                isp.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex), parent=prozor)

        ctk.CTkButton(dugmad_frame, text="Sacuvaj ispit",
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY, height=44, corner_radius=8,
                      font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                      command=sacuvaj).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _obrisi(self):
        if not self._izabrani_id:
            return
        if messagebox.askyesno("Potvrda", "Obrisi ovaj ispit?"):
            try:
                isp = Ispit()
                isp.id = self._izabrani_id
                isp.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
