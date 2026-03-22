import customtkinter as ctk
from tkinter import ttk, messagebox
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


class InstruktoriView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 0))
        ctk.CTkLabel(header, text="Instruktori",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=32, pady=(16, 0))

        ctk.CTkLabel(toolbar, text="Prikazi:",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        self._filter_var = ctk.StringVar(value="Aktivni")
        ctk.CTkSegmentedButton(toolbar,
                               values=["Aktivni", "Svi"],
                               variable=self._filter_var,
                               fg_color=BG_CARD,
                               selected_color=ACCENT_BLUE,
                               selected_hover_color=ACCENT_HOVER,
                               unselected_color=BG_CARD,
                               unselected_hover_color=BORDER_DARK,
                               text_color=TEXT_PRIMARY,
                               command=lambda _: self._ucitaj_podatke()).pack(side="left")

        ctk.CTkButton(toolbar, text="+ Dodaj instruktora", width=180,
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY,
                      font=ctk.CTkFont(family="Arial", size=14),
                      height=40, corner_radius=8,
                      command=self._otvori_formu_novi).pack(side="right")

        # Tabela
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

        kolone = ("ID", "Ime", "Prezime", "Telefon", "Kategorija", "Status")
        self._tabela = ttk.Treeview(tabela_frame, columns=kolone,
                                    show="headings", selectmode="browse")
        sirine = {"ID": 50, "Ime": 160, "Prezime": 170,
                  "Telefon": 140, "Kategorija": 110, "Status": 110}
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

        # Dugmad
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
        samo_aktivni = self._filter_var.get() == "Aktivni"
        instruktori = Instruktor.get_all(samo_aktivni=samo_aktivni)
        for i in instruktori:
            self._tabela.insert("", "end", iid=str(i.id), values=(
                i.id, i.ime, i.prezime,
                i.telefon or "—",
                i.kategorija or "B",
                "Aktivan" if i.aktivan else "Neaktivan"
            ))
        self._lbl_ukupno.configure(text=f"Ukupno: {len(instruktori)}")
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

    def _otvori_formu(self, instruktor_id):
        instruktor = Instruktor.get_by_id(instruktor_id) if instruktor_id else None
        je_novi = instruktor is None

        prozor = ctk.CTkToplevel(self)
        prozor.title("Novi instruktor" if je_novi else "Izmena instruktora")
        prozor.geometry("480x540")
        prozor.resizable(False, False)
        prozor.configure(fg_color=BG_PRIMARY)
        prozor.grab_set()
        prozor.lift()
        prozor.focus_force()

        ctk.CTkLabel(prozor,
                     text="Novi instruktor" if je_novi else "Izmena instruktora",
                     font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=32, pady=(28, 4))
        ctk.CTkLabel(prozor,
                     text="Popunite podatke o instruktoru",
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

        e_ime     = polje("Ime",     instruktor.ime      if instruktor else "", 0, True)
        e_prezime = polje("Prezime", instruktor.prezime  if instruktor else "", 2, True)
        e_telefon = polje("Telefon", instruktor.telefon  if instruktor else "", 4)

        ctk.CTkLabel(forma, text="Kategorija", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=6, column=0, sticky="w", pady=(0, 4))
        kat_var = ctk.StringVar(value=instruktor.kategorija if instruktor else "B")
        ctk.CTkOptionMenu(forma, variable=kat_var,
                          values=["A", "A1", "A2", "AM", "B", "B1", "C", "D"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK,
                          text_color=TEXT_PRIMARY,
                          height=40).grid(row=7, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(forma, text="Status", anchor="w",
                     font=ctk.CTkFont(family="Arial", size=13),
                     text_color=TEXT_SECONDARY).grid(row=8, column=0, sticky="w", pady=(0, 4))
        aktivan_var = ctk.StringVar(
            value="Aktivan" if (instruktor.aktivan if instruktor else True) else "Neaktivan")
        ctk.CTkOptionMenu(forma, variable=aktivan_var,
                          values=["Aktivan", "Neaktivan"],
                          fg_color=BG_CARD, button_color=BORDER_LIGHT,
                          button_hover_color=BORDER_DARK,
                          text_color=TEXT_PRIMARY,
                          height=40).grid(row=9, column=0, sticky="ew", pady=(0, 12))

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
            if not ime or not prezime:
                messagebox.showerror("Greska", "Ime i prezime su obavezni!", parent=prozor)
                return
            i = instruktor if instruktor else Instruktor()
            i.ime       = ime
            i.prezime   = prezime
            i.telefon   = e_telefon.get().strip() or None
            i.kategorija = kat_var.get()
            i.aktivan   = 1 if aktivan_var.get() == "Aktivan" else 0
            try:
                i.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex), parent=prozor)

        ctk.CTkButton(dugmad_frame, text="Sacuvaj instruktora",
                      fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
                      text_color=TEXT_PRIMARY, height=44, corner_radius=8,
                      font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                      command=sacuvaj).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _obrisi(self):
        if not self._izabrani_id:
            return
        i = Instruktor.get_by_id(self._izabrani_id)
        if not i:
            return
        if messagebox.askyesno("Potvrda", f"Obrisi instruktora {i.ime} {i.prezime}?"):
            try:
                i.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greska", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
