import customtkinter as ctk
from tkinter import ttk, messagebox
from models.cas_ispit import Cas
from models.kandidat import Kandidat
from models.instruktor import Instruktor

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


class CasoviView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="Casovi voznje",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=32, pady=(16, 0))

        ctk.CTkLabel(toolbar, text="Status:",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        self._filter_var = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(toolbar,
                               values=["Svi", "zakazan", "odrzan", "otkazan"],
                               variable=self._filter_var,
                               fg_color=BG_CARD,
                               selected_color=ACCENT_BLUE,
                               selected_hover_color=ACCENT_HOVER,
                               unselected_color=BG_CARD,
                               unselected_hover_color=BORDER_DARK,
                               text_color=TEXT_PRIMARY,
                               command=lambda _: self._ucitaj_podatke()).pack(side="left")

        ctk.CTkButton(toolbar, text="+ Zakazi cas", width=160,
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

        kolone = ("ID", "Kandidat", "Instruktor", "Datum", "Vreme", "Status", "Napomena")
        self._tabela = ttk.Treeview(tabela_frame, columns=kolone,
                                    show="headings", selectmode="browse")
        sirine = {"ID": 45, "Kandidat": 170, "Instruktor": 170,
                  "Datum": 110, "Vreme": 70, "Status": 90, "Napomena": 180}
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
        casovi = Cas.get_all()
        ft = self._filter_var.get()
        if ft != "Svi":
            casovi = [c for c in casovi if c.status == ft]
        for c in casovi:
            k_ime = f"{c.kandidat_ime or ''} {c.kandidat_prezime or ''}".strip() or f"ID {c.kandidat_id}"
            i_ime = f"{c.instruktor_ime or ''} {c.instruktor_prezime or ''}".strip() or f"ID {c.instruktor_id}"
            self._tabela.insert("", "end", iid=str(c.id), values=(
                c.id, k_ime, i_ime,
                c.datum or "—", c.vreme or "—",
                c.status or "—", c.napomena or ""
            ))
        self._lbl_ukupno.configure(text=f"Ukupno: {len(casovi)}")
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

    def _otvori_formu(self, cas_id):
        cas = Cas.get_by_id(cas_id) if cas_id else None
        je_novi = cas is None

        prozor = ctk.CTkToplevel(self)
        prozor.title("Novi cas" if je_novi else "Izmena casa")
        prozor.geometry("480x640")
        prozor.resizable(False, True)
        prozor.configure(fg_color=BG_PRIMARY)
        prozor.grab_set()
        prozor.lift()
        prozor.focus_force()

        ctk.CTkLabel(prozor,
                     text="Novi cas" if je_novi else "Izmena casa",
                     font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(prozor, text="Popunite podatke o casu",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=32)
        ctk.CTkFrame(prozor, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=32, pady=(16, 0))

        # Scrollable forma
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
        if cas:
            for k in kandidati:
                if k.id == cas.kandidat_id:
                    kandidat_var.set(f"{k.id} — {k.ime} {k.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=kandidat_var,
                          values=kandidat_opcije if kandidat_opcije else ["—"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Instruktor
        instruktori = Instruktor.get_all(samo_aktivni=True)
        instruktor_opcije = [f"{i.id} — {i.ime} {i.prezime}" for i in instruktori]

        ctk.CTkLabel(forma, text="Instruktor *", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 4))
        instruktor_var = ctk.StringVar()
        if cas:
            for i in instruktori:
                if i.id == cas.instruktor_id:
                    instruktor_var.set(f"{i.id} — {i.ime} {i.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=instruktor_var,
                          values=instruktor_opcije if instruktor_opcije else ["—"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=3, column=0, sticky="ew", pady=(0, 12))

        def polje(label, vrednost="", row=0, obavezno=False):
            ctk.CTkLabel(forma, text=label + (" *" if obavezno else ""),
                         anchor="w",
                         font=ctk.CTkFont(family="Arial", size=13),
                         text_color=TEXT_SECONDARY).grid(row=row, column=0, sticky="w", pady=(0, 4))
            entry = ctk.CTkEntry(forma, height=40,
                                  fg_color=BG_CARD, border_color=BORDER_DARK,
                                  text_color=TEXT_PRIMARY)
            entry.grid(row=row+1, column=0, sticky="ew", pady=(0, 12))
            if vrednost:
                entry.insert(0, str(vrednost))
            return entry

        e_datum   = polje("Datum (YYYY-MM-DD)", cas.datum   if cas else "", 4, True)
        e_vreme   = polje("Vreme (HH:MM)",      cas.vreme   if cas else "", 6)
        e_napomena = polje("Napomena",           cas.napomena if cas else "", 8)

        ctk.CTkLabel(forma, text="Status", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=10, column=0, sticky="w", pady=(0, 4))
        status_var = ctk.StringVar(value=cas.status if cas else "zakazan")
        ctk.CTkOptionMenu(forma, variable=status_var,
                          values=["zakazan", "odrzan", "otkazan"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK, text_color=TEXT_PRIMARY,
                          height=40).grid(row=11, column=0, sticky="ew", pady=(0, 12))

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
            if not instruktor_var.get() or instruktor_var.get() == "—":
                messagebox.showerror("Greska", "Izaberite instruktora!", parent=prozor)
                return
            datum = e_datum.get().strip()
            if not datum:
                messagebox.showerror("Greska", "Datum je obavezan!", parent=prozor)
                return
            kandidat_id   = int(kandidat_var.get().split(" — ")[0])
            instruktor_id = int(instruktor_var.get().split(" — ")[0])
            c = cas if cas else Cas()
            c.kandidat_id   = kandidat_id
            c.instruktor_id = instruktor_id
            c.datum         = datum
            c.vreme         = e_vreme.get().strip() or None
            c.status        = status_var.get()
            c.napomena      = e_napomena.get().strip() or None
            try:
                c.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex), parent=prozor)

        ctk.CTkButton(dugmad_frame, text="Sacuvaj cas",
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY, height=44, corner_radius=8,
                      font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                      command=sacuvaj).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _obrisi(self):
        if not self._izabrani_id:
            return
        if messagebox.askyesno("Potvrda", "Obrisi ovaj cas?"):
            try:
                c = Cas()
                c.id = self._izabrani_id
                c.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
