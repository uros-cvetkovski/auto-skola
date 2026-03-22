import customtkinter as ctk
from tkinter import ttk, messagebox
from models.cas_ispit import Ispit
from models.kandidat import Kandidat


class IspitiView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        vrh = ctk.CTkFrame(self, fg_color="transparent")
        vrh.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(vrh, text="Ispiti",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        ctk.CTkButton(vrh, text="+ Dodaj ispit", width=150,
                      command=self._otvori_formu_novi).pack(side="right")

        # Filteri
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 12))

        ctk.CTkLabel(filter_frame, text="Tip:").pack(side="left", padx=(0, 6))
        self._filter_tip = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(
            filter_frame,
            values=["Svi", "teorija", "praksa"],
            variable=self._filter_tip,
            command=lambda _: self._ucitaj_podatke()
        ).pack(side="left")

        ctk.CTkLabel(filter_frame, text="Rezultat:").pack(side="left", padx=(18, 6))
        self._filter_rezultat = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(
            filter_frame,
            values=["Svi", "ceka", "polozio", "pao"],
            variable=self._filter_rezultat,
            command=lambda _: self._ucitaj_podatke()
        ).pack(side="left")

        # Tabela
        tabela_frame = ctk.CTkFrame(self, corner_radius=12)
        tabela_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        kolone = ("ID", "Kandidat", "Tip", "Datum", "Rezultat", "Napomena")

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

        sirine = {"ID": 45, "Kandidat": 200, "Tip": 90,
                  "Datum": 110, "Rezultat": 100, "Napomena": 220}
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

        # Dugmad
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

    def _ucitaj_podatke(self):
        self._tabela.delete(*self._tabela.get_children())
        ispiti = Ispit.get_all()

        ft = self._filter_tip.get()
        fr = self._filter_rezultat.get()
        if ft != "Svi":
            ispiti = [i for i in ispiti if i.tip == ft]
        if fr != "Svi":
            ispiti = [i for i in ispiti if i.rezultat == fr]

        self._tabela.tag_configure("polozio_tag", background="#1a4a2e")
        self._tabela.tag_configure("pao_tag", background="#5a1a1a")
        self._tabela.tag_configure("ceka_tag", background="#4a3a10")

        boje_tag = {"polozio": "polozio_tag", "pao": "pao_tag", "ceka": "ceka_tag"}

        for ispit in ispiti:
            kandidat_ime = f"{ispit.kandidat_ime or ''} {ispit.kandidat_prezime or ''}".strip() or f"ID {ispit.kandidat_id}"
            tag = boje_tag.get(ispit.rezultat, "")

            self._tabela.insert("", "end", iid=str(ispit.id), tags=(tag,), values=(
                ispit.id, kandidat_ime, ispit.tip or "—",
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
        prozor.geometry("420x440")
        prozor.resizable(False, False)
        prozor.grab_set()

        ctk.CTkLabel(prozor,
                     text="Novi ispit" if je_novi else "Izmena ispita",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(24, 16))

        forma = ctk.CTkFrame(prozor, fg_color="transparent")
        forma.pack(fill="both", expand=True, padx=30)
        forma.columnconfigure(0, weight=1)

        # Kandidat
        kandidati = Kandidat.get_all()
        kandidat_opcije = [f"{k.id} — {k.ime} {k.prezime}" for k in kandidati]

        ctk.CTkLabel(forma, text="Kandidat *", anchor="w").grid(
            row=0, column=0, sticky="w", pady=(8, 0))
        kandidat_var = ctk.StringVar()
        if ispit and kandidati:
            for k in kandidati:
                if k.id == ispit.kandidat_id:
                    kandidat_var.set(f"{k.id} — {k.ime} {k.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=kandidat_var,
                          values=kandidat_opcije if kandidat_opcije else ["—"],
                          width=280).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(forma, text="Tip ispita *", anchor="w").grid(
            row=2, column=0, sticky="w", pady=(8, 0))
        tip_var = ctk.StringVar(value=ispit.tip if ispit else "teorija")
        ctk.CTkOptionMenu(forma, variable=tip_var,
                          values=["teorija", "praksa"],
                          width=280).grid(row=3, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(forma, text="Datum (YYYY-MM-DD) *", anchor="w").grid(
            row=4, column=0, sticky="w", pady=(8, 0))
        e_datum = ctk.CTkEntry(forma, width=280)
        e_datum.grid(row=5, column=0, sticky="ew", pady=(2, 0))
        if ispit and ispit.datum:
            e_datum.insert(0, ispit.datum)

        ctk.CTkLabel(forma, text="Rezultat", anchor="w").grid(
            row=6, column=0, sticky="w", pady=(8, 0))
        rezultat_var = ctk.StringVar(value=ispit.rezultat if ispit else "ceka")
        ctk.CTkOptionMenu(forma, variable=rezultat_var,
                          values=["ceka", "polozio", "pao"],
                          width=280).grid(row=7, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(forma, text="Napomena", anchor="w").grid(
            row=8, column=0, sticky="w", pady=(8, 0))
        e_napomena = ctk.CTkEntry(forma, width=280)
        e_napomena.grid(row=9, column=0, sticky="ew", pady=(2, 0))
        if ispit and ispit.napomena:
            e_napomena.insert(0, ispit.napomena)

        def sacuvaj():
            if not kandidat_var.get() or kandidat_var.get() == "—":
                messagebox.showerror("Greška", "Izaberite kandidata!", parent=prozor)
                return
            datum = e_datum.get().strip()
            if not datum:
                messagebox.showerror("Greška", "Datum je obavezan!", parent=prozor)
                return

            kandidat_id = int(kandidat_var.get().split(" — ")[0])

            isp = ispit if ispit else Ispit()
            isp.kandidat_id = kandidat_id
            isp.tip = tip_var.get()
            isp.datum = datum
            isp.rezultat = rezultat_var.get()
            isp.napomena = e_napomena.get().strip() or None

            try:
                isp.sacuvaj()
                prozor.destroy()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex), parent=prozor)

        dugmad = ctk.CTkFrame(prozor, fg_color="transparent")
        dugmad.pack(pady=16)
        ctk.CTkButton(dugmad, text="Otkaži", width=120, fg_color="gray",
                      command=prozor.destroy).pack(side="left", padx=8)
        ctk.CTkButton(dugmad, text="Sačuvaj", width=120,
                      command=sacuvaj).pack(side="left", padx=8)

    def _obrisi(self):
        if not self._izabrani_id:
            return
        if messagebox.askyesno("Potvrda", "Obriši ovaj ispit?"):
            try:
                isp = Ispit()
                isp.id = self._izabrani_id
                isp.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
