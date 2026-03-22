import customtkinter as ctk
from tkinter import ttk, messagebox
from models.kandidat import Kandidat


class KandidatiView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        # ── Naslov + dugme Dodaj ────────────────────────────────────────────
        vrh = ctk.CTkFrame(self, fg_color="transparent")
        vrh.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(vrh, text="Kandidati",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        ctk.CTkButton(vrh, text="+ Dodaj kandidata", width=160,
                      command=self._otvori_formu_novi).pack(side="right")

        # ── Traka za pretragu ───────────────────────────────────────────────
        pretraga_frame = ctk.CTkFrame(self, fg_color="transparent")
        pretraga_frame.pack(fill="x", padx=30, pady=(0, 12))

        self._pretraga_var = ctk.StringVar()
        self._pretraga_var.trace_add("write", lambda *_: self._pretrazi())

        ctk.CTkEntry(
            pretraga_frame,
            placeholder_text="🔍  Pretraži po imenu, prezimenu, JMBG ili telefonu...",
            textvariable=self._pretraga_var,
            width=400
        ).pack(side="left")

        # Filter po statusu
        self._filter_var = ctk.StringVar(value="Svi")
        ctk.CTkOptionMenu(
            pretraga_frame,
            variable=self._filter_var,
            values=["Svi", "aktivan", "polozio", "odustao"],
            width=130,
            command=lambda _: self._pretrazi()
        ).pack(side="left", padx=(12, 0))

        # ── Tabela ──────────────────────────────────────────────────────────
        tabela_frame = ctk.CTkFrame(self, corner_radius=12)
        tabela_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        kolone = ("ID", "Ime", "Prezime", "JMBG", "Telefon", "Email", "Datum upisa", "Status")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=32,
                        font=("Helvetica", 12))
        style.configure("Treeview.Heading",
                        background="#1a73e8",
                        foreground="white",
                        font=("Helvetica", 12, "bold"))
        style.map("Treeview",
                  background=[("selected", "#1a73e8")],
                  foreground=[("selected", "white")])

        self._tabela = ttk.Treeview(tabela_frame, columns=kolone, show="headings",
                                    selectmode="browse")

        sirine = {"ID": 50, "Ime": 120, "Prezime": 130, "JMBG": 140,
                  "Telefon": 120, "Email": 170, "Datum upisa": 110, "Status": 90}

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

        # ── Dugmad ispod tabele ─────────────────────────────────────────────
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

    def _ucitaj_podatke(self, kandidati=None):
        self._tabela.delete(*self._tabela.get_children())
        if kandidati is None:
            kandidati = Kandidat.get_all()

        boje = {"aktivan": "#1a4a8a", "polozio": "#1a5c38", "odustao": "#7a2020"}
        self._tabela.tag_configure("aktivan", background="#1a3a6a")
        self._tabela.tag_configure("polozio", background="#1a4a2e")
        self._tabela.tag_configure("odustao", background="#5a1a1a")

        for k in kandidati:
            tag = k.status if k.status in boje else ""
            self._tabela.insert("", "end", iid=str(k.id), tags=(tag,), values=(
                k.id, k.ime, k.prezime, k.jmbg,
                k.telefon or "—", k.email or "—",
                k.datum_upisa or "—", k.status or "—"
            ))

        self._lbl_ukupno.configure(text=f"Ukupno: {len(kandidati)} kandidata")
        self._izabrani_id = None
        self._btn_edit.configure(state="disabled")
        self._btn_obrisi.configure(state="disabled")

    def _pretrazi(self):
        upit = self._pretraga_var.get().strip()
        filter_status = self._filter_var.get()

        if upit:
            rezultati = Kandidat.pretrazi(upit)
        else:
            rezultati = Kandidat.get_all()

        if filter_status != "Svi":
            rezultati = [k for k in rezultati if k.status == filter_status]

        self._ucitaj_podatke(rezultati)

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

    # ── Forma (dodaj / izmeni) ──────────────────────────────────────────────

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
        prozor.geometry("460x560")
        prozor.resizable(False, False)
        prozor.grab_set()

        ctk.CTkLabel(prozor,
                     text="Novi kandidat" if je_novi else "Izmena kandidata",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(24, 16))

        forma = ctk.CTkFrame(prozor, fg_color="transparent")
        forma.pack(fill="both", expand=True, padx=30)

        def polje(label, vrednost="", row=0):
            ctk.CTkLabel(forma, text=label, anchor="w").grid(
                row=row, column=0, sticky="w", pady=(8, 0))
            entry = ctk.CTkEntry(forma, width=280)
            entry.grid(row=row+1, column=0, sticky="ew", pady=(2, 0))
            if vrednost:
                entry.insert(0, str(vrednost))
            return entry

        forma.columnconfigure(0, weight=1)

        e_ime = polje("Ime *", kandidat.ime if kandidat else "", 0)
        e_prezime = polje("Prezime *", kandidat.prezime if kandidat else "", 2)
        e_jmbg = polje("JMBG *", kandidat.jmbg if kandidat else "", 4)
        e_telefon = polje("Telefon", kandidat.telefon if kandidat else "", 6)
        e_email = polje("Email", kandidat.email if kandidat else "", 8)
        e_datum = polje("Datum upisa (YYYY-MM-DD)",
                        kandidat.datum_upisa if kandidat else "", 10)

        ctk.CTkLabel(forma, text="Status", anchor="w").grid(
            row=12, column=0, sticky="w", pady=(8, 0))
        status_var = ctk.StringVar(
            value=kandidat.status if kandidat else "aktivan")
        ctk.CTkOptionMenu(forma, variable=status_var,
                          values=["aktivan", "polozio", "odustao"],
                          width=280).grid(row=13, column=0, sticky="ew", pady=(2, 0))

        def sacuvaj():
            ime = e_ime.get().strip()
            prezime = e_prezime.get().strip()
            jmbg = e_jmbg.get().strip()

            if not ime or not prezime or not jmbg:
                messagebox.showerror("Greška", "Ime, prezime i JMBG su obavezni!",
                                     parent=prozor)
                return

            k = kandidat if kandidat else Kandidat()
            k.ime = ime
            k.prezime = prezime
            k.jmbg = jmbg
            k.telefon = e_telefon.get().strip() or None
            k.email = e_email.get().strip() or None
            k.datum_upisa = e_datum.get().strip() or None
            k.status = status_var.get()

            try:
                k.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška pri čuvanju", str(ex), parent=prozor)

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
        k = Kandidat.get_by_id(self._izabrani_id)
        if not k:
            return
        odgovor = messagebox.askyesno(
            "Potvrda brisanja",
            f"Da li ste sigurni da želite da obrišete kandidata\n{k.ime} {k.prezime}?"
        )
        if odgovor:
            try:
                k.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
