import customtkinter as ctk
from tkinter import ttk, messagebox
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


class KandidatiView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="Kandidati",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=32, pady=(16, 0))

        self._pretraga_var = ctk.StringVar()
        self._pretraga_var.trace_add("write", lambda *_: self._pretrazi())

        ctk.CTkEntry(toolbar,
                     placeholder_text="Pretrazi po imenu, prezimenu, JMBG...",
                     textvariable=self._pretraga_var,
                     fg_color=BG_CARD, border_color=BORDER_DARK,
                     text_color=TEXT_PRIMARY,
                     placeholder_text_color=TEXT_MUTED,
                     height=40, width=340).pack(side="left")

        self._filter_var = ctk.StringVar(value="Svi")
        ctk.CTkOptionMenu(toolbar,
                          variable=self._filter_var,
                          values=["Svi", "aktivan", "polozio", "odustao"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK,
                          text_color=TEXT_PRIMARY,
                          width=130, height=40,
                          command=lambda _: self._pretrazi()).pack(side="left", padx=(10, 0))

        ctk.CTkButton(toolbar, text="+ Dodaj kandidata", width=170,
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

        kolone = ("ID", "Ime", "Prezime", "JMBG", "Telefon", "Email", "Datum upisa", "Kat.", "Status")
        self._tabela = ttk.Treeview(tabela_frame, columns=kolone,
                                    show="headings", selectmode="browse")

        sirine = {"ID": 50, "Ime": 120, "Prezime": 130, "JMBG": 150,
                  "Telefon": 110, "Email": 170, "Datum upisa": 110, "Kat.": 50, "Status": 90}
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
                                       text_color="#FFFFFF", height=38,
                                       corner_radius=8, state="disabled",
                                       command=self._otvori_formu_edit)
        self._btn_edit.pack(side="left", padx=(0, 8))

        self._btn_obrisi = ctk.CTkButton(dno, text="Obrisi", width=120,
                                          fg_color=RED, hover_color=RED_HOVER,
                                          text_color="#FFFFFF", height=38,
                                          corner_radius=8, state="disabled",
                                          command=self._obrisi)
        self._btn_obrisi.pack(side="left")

        self._lbl_ukupno = ctk.CTkLabel(dno, text="",
                                         text_color=TEXT_MUTED,
                                         font=ctk.CTkFont(family="Arial", size=12))
        self._lbl_ukupno.pack(side="right")

    def _ucitaj_podatke(self, kandidati=None):
        self._tabela.delete(*self._tabela.get_children())
        if kandidati is None:
            kandidati = Kandidat.get_all()
        for k in kandidati:
            self._tabela.insert("", "end", iid=str(k.id), values=(
                k.id, k.ime, k.prezime, k.jmbg,
                k.telefon or "—", k.email or "—",
                k.datum_upisa or "—", k.kategorija or "B", k.status or "—"
            ))
        self._lbl_ukupno.configure(text=f"Ukupno: {len(kandidati)} kandidata")
        self._izabrani_id = None
        self._btn_edit.configure(state="disabled")
        self._btn_obrisi.configure(state="disabled")

    def _pretrazi(self):
        upit = self._pretraga_var.get().strip()
        filter_status = self._filter_var.get()
        rezultati = Kandidat.pretrazi(upit) if upit else Kandidat.get_all()
        if filter_status != "Svi":
            rezultati = [k for k in rezultati if k.status == filter_status]
        self._ucitaj_podatke(rezultati)

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

    def _otvori_formu(self, kandidat_id):
        kandidat = Kandidat.get_by_id(kandidat_id) if kandidat_id else None
        je_novi = kandidat is None

        prozor = ctk.CTkToplevel(self)
        prozor.title("Novi kandidat" if je_novi else "Izmena kandidata")
        prozor.geometry("480x680")
        prozor.resizable(False, False)
        prozor.configure(fg_color=BG_PRIMARY)
        prozor.grab_set()
        prozor.lift()
        prozor.focus_force()

        ctk.CTkLabel(prozor,
                     text="Novi kandidat" if je_novi else "Izmena kandidata",
                     font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(prozor,
                     text="Popunite podatke o kandidatu",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=32)
        ctk.CTkFrame(prozor, height=1, fg_color=BORDER_DARK).pack(fill="x", padx=32, pady=(16, 0))

        forma = ctk.CTkScrollableFrame(prozor, fg_color="transparent",
                                        scrollbar_button_color=BORDER_DARK)
        forma.pack(fill="both", expand=True, padx=32, pady=(12, 0))
        forma.grid_columnconfigure(0, weight=1)

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

        e_ime     = polje("Ime",     kandidat.ime      if kandidat else "", 0,  True)
        e_prezime = polje("Prezime", kandidat.prezime  if kandidat else "", 2,  True)
        e_jmbg    = polje("JMBG",    kandidat.jmbg     if kandidat else "", 4,  True)
        e_telefon = polje("Telefon", kandidat.telefon  if kandidat else "", 6)
        e_email   = polje("Email",   kandidat.email    if kandidat else "", 8)
        e_datum   = polje("Datum upisa (YYYY-MM-DD)",
                          kandidat.datum_upisa if kandidat else "", 10)

        ctk.CTkLabel(forma, text="Kategorija *", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=12, column=0, sticky="w", pady=(0, 4))
        kategorija_var = ctk.StringVar(value=kandidat.kategorija if kandidat else "B")
        ctk.CTkOptionMenu(forma, variable=kategorija_var,
                          values=["A", "A1", "A2", "B", "C", "D", "BE", "CE"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK,
                          text_color=TEXT_PRIMARY,
                          height=40).grid(row=13, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(forma, text="Status", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=14, column=0, sticky="w", pady=(0, 4))
        status_var = ctk.StringVar(value=kandidat.status if kandidat else "aktivan")
        ctk.CTkOptionMenu(forma, variable=status_var,
                          values=["aktivan", "polozio", "odustao"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK,
                          text_color=TEXT_PRIMARY,
                          height=40).grid(row=15, column=0, sticky="ew", pady=(0, 12))

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
            ime     = e_ime.get().strip()
            prezime = e_prezime.get().strip()
            jmbg    = e_jmbg.get().strip()
            if not ime or not prezime or not jmbg:
                messagebox.showerror("Greska", "Ime, prezime i JMBG su obavezni!", parent=prozor)
                return
            k = kandidat if kandidat else Kandidat()
            k.ime         = ime
            k.prezime     = prezime
            k.jmbg        = jmbg
            k.telefon     = e_telefon.get().strip() or None
            k.email       = e_email.get().strip() or None
            k.datum_upisa = e_datum.get().strip() or None
            k.kategorija  = kategorija_var.get()
            k.status      = status_var.get()
            try:
                k.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska pri cuvanju", str(ex), parent=prozor)

        ctk.CTkButton(dugmad_frame, text="Sacuvaj kandidata",
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY, height=44, corner_radius=8,
                      font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                      command=sacuvaj).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _obrisi(self):
        if not self._izabrani_id:
            return
        k = Kandidat.get_by_id(self._izabrani_id)
        if not k:
            return
        if messagebox.askyesno("Potvrda", f"Obrisi kandidata {k.ime} {k.prezime}?"):
            try:
                k.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()