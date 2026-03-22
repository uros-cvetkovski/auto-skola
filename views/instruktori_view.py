import customtkinter as ctk
from tkinter import ttk, messagebox
from models.instruktor import Instruktor


class InstruktoriView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        # ── Naslov + dugme ──────────────────────────────────────────────────
        vrh = ctk.CTkFrame(self, fg_color="transparent")
        vrh.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(vrh, text="Instruktori",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        ctk.CTkButton(vrh, text="+ Dodaj instruktora", width=170,
                      command=self._otvori_formu_novi).pack(side="right")

        # ── Filter ──────────────────────────────────────────────────────────
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 12))

        ctk.CTkLabel(filter_frame, text="Prikaži:").pack(side="left", padx=(0, 8))
        self._filter_var = ctk.StringVar(value="Aktivni")
        ctk.CTkSegmentedButton(
            filter_frame,
            values=["Aktivni", "Svi"],
            variable=self._filter_var,
            command=lambda _: self._ucitaj_podatke()
        ).pack(side="left")

        # ── Tabela ──────────────────────────────────────────────────────────
        tabela_frame = ctk.CTkFrame(self, corner_radius=12)
        tabela_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        kolone = ("ID", "Ime", "Prezime", "Telefon", "Kategorija", "Status")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=32,
                        font=("Helvetica", 12))
        style.configure("Treeview.Heading",
                        background="#1a73e8", foreground="white",
                        font=("Helvetica", 12, "bold"))
        style.map("Treeview",
                  background=[("selected", "#1a73e8")],
                  foreground=[("selected", "white")])

        self._tabela = ttk.Treeview(tabela_frame, columns=kolone,
                                    show="headings", selectmode="browse")

        sirine = {"ID": 50, "Ime": 140, "Prezime": 150,
                  "Telefon": 130, "Kategorija": 100, "Status": 100}
        for k in kolone:
            self._tabela.heading(k, text=k)
            self._tabela.column(k, width=sirine[k], anchor="center")

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical",
                                  command=self._tabela.yview)
        self._tabela.configure(yscrollcommand=scrollbar.set)
        self._tabela.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self._tabela.bind("<<TreeviewSelect>>", self._na_selekciju)
        self._tabela.bind("<Double-1>", lambda _: self._otvori_formu_edit())

        # ── Dugmad ──────────────────────────────────────────────────────────
        dno = ctk.CTkFrame(self, fg_color="transparent")
        dno.pack(fill="x", padx=30, pady=(0, 25))

        self._btn_edit = ctk.CTkButton(dno, text="✏️  Izmeni", width=130,
                                       state="disabled", command=self._otvori_formu_edit)
        self._btn_edit.pack(side="left", padx=(0, 8))

        self._btn_obrisi = ctk.CTkButton(dno, text="🗑️  Obriši", width=130,
                                          fg_color="#db4437", hover_color="#b03228",
                                          state="disabled", command=self._obrisi)
        self._btn_obrisi.pack(side="left")

        self._lbl_ukupno = ctk.CTkLabel(dno, text="", text_color="gray",
                                         font=ctk.CTkFont(size=12))
        self._lbl_ukupno.pack(side="right")

    # ── Punjenje tabele ─────────────────────────────────────────────────────

    def _ucitaj_podatke(self):
        self._tabela.delete(*self._tabela.get_children())
        samo_aktivni = self._filter_var.get() == "Aktivni"
        instruktori = Instruktor.get_all(samo_aktivni=samo_aktivni)

        self._tabela.tag_configure("aktivan", background="#1a3a6a")
        self._tabela.tag_configure("neaktivan", background="#3a3a3a")

        for i in instruktori:
            tag = "aktivan" if i.aktivan else "neaktivan"
            self._tabela.insert("", "end", iid=str(i.id), tags=(tag,), values=(
                i.id, i.ime, i.prezime,
                i.telefon or "—",
                i.kategorija or "B",
                "Aktivan" if i.aktivan else "Neaktivan"
            ))

        self._lbl_ukupno.configure(text=f"Ukupno: {len(instruktori)}")
        self._izabrani_id = None
        self._btn_edit.configure(state="disabled")
        self._btn_obrisi.configure(state="disabled")

    # ── Selekcija ───────────────────────────────────────────────────────────

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

    # ── Forma ───────────────────────────────────────────────────────────────

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
        prozor.geometry("420x420")
        prozor.resizable(False, False)
        prozor.grab_set()

        ctk.CTkLabel(prozor,
                     text="Novi instruktor" if je_novi else "Izmena instruktora",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(24, 16))

        forma = ctk.CTkFrame(prozor, fg_color="transparent")
        forma.pack(fill="both", expand=True, padx=30)
        forma.columnconfigure(0, weight=1)

        def polje(label, vrednost="", row=0):
            ctk.CTkLabel(forma, text=label, anchor="w").grid(
                row=row, column=0, sticky="w", pady=(8, 0))
            entry = ctk.CTkEntry(forma, width=280)
            entry.grid(row=row+1, column=0, sticky="ew", pady=(2, 0))
            if vrednost:
                entry.insert(0, str(vrednost))
            return entry

        e_ime = polje("Ime *", instruktor.ime if instruktor else "", 0)
        e_prezime = polje("Prezime *", instruktor.prezime if instruktor else "", 2)
        e_telefon = polje("Telefon", instruktor.telefon if instruktor else "", 4)

        ctk.CTkLabel(forma, text="Kategorija", anchor="w").grid(
            row=6, column=0, sticky="w", pady=(8, 0))
        kat_var = ctk.StringVar(value=instruktor.kategorija if instruktor else "B")
        ctk.CTkOptionMenu(forma, variable=kat_var,
                          values=["A", "A1", "A2", "AM", "B", "B1", "C", "D"],
                          width=280).grid(row=7, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(forma, text="Status", anchor="w").grid(
            row=8, column=0, sticky="w", pady=(8, 0))
        aktivan_var = ctk.StringVar(
            value="Aktivan" if (instruktor.aktivan if instruktor else True) else "Neaktivan")
        ctk.CTkOptionMenu(forma, variable=aktivan_var,
                          values=["Aktivan", "Neaktivan"],
                          width=280).grid(row=9, column=0, sticky="ew", pady=(2, 0))

        def sacuvaj():
            ime = e_ime.get().strip()
            prezime = e_prezime.get().strip()
            if not ime or not prezime:
                messagebox.showerror("Greška", "Ime i prezime su obavezni!", parent=prozor)
                return

            i = instruktor if instruktor else Instruktor()
            i.ime = ime
            i.prezime = prezime
            i.telefon = e_telefon.get().strip() or None
            i.kategorija = kat_var.get()
            i.aktivan = 1 if aktivan_var.get() == "Aktivan" else 0

            try:
                i.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex), parent=prozor)

        dugmad = ctk.CTkFrame(prozor, fg_color="transparent")
        dugmad.pack(pady=20)
        ctk.CTkButton(dugmad, text="Otkaži", width=120, fg_color="gray",
                      command=prozor.destroy).pack(side="left", padx=8)
        ctk.CTkButton(dugmad, text="Sačuvaj", width=120,
                      command=sacuvaj).pack(side="left", padx=8)

    # ── Brisanje ────────────────────────────────────────────────────────────

    def _obrisi(self):
        if not self._izabrani_id:
            return
        i = Instruktor.get_by_id(self._izabrani_id)
        if not i:
            return
        if messagebox.askyesno("Potvrda", f"Obriši instruktora {i.ime} {i.prezime}?"):
            try:
                i.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
