import customtkinter as ctk
from tkinter import ttk, messagebox
from models.cas_ispit import Cas
from models.kandidat import Kandidat
from models.instruktor import Instruktor


class CasoviView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._izabrani_id = None
        self._build_ui()
        self._ucitaj_podatke()

    def _build_ui(self):
        vrh = ctk.CTkFrame(self, fg_color="transparent")
        vrh.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(vrh, text="Časovi vožnje",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        ctk.CTkButton(vrh, text="+ Zakaži čas", width=150,
                      command=self._otvori_formu_novi).pack(side="right")

        # Filter po statusu
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 12))

        ctk.CTkLabel(filter_frame, text="Status:").pack(side="left", padx=(0, 8))
        self._filter_var = ctk.StringVar(value="Svi")
        ctk.CTkSegmentedButton(
            filter_frame,
            values=["Svi", "zakazan", "odrzan", "otkazan"],
            variable=self._filter_var,
            command=lambda _: self._ucitaj_podatke()
        ).pack(side="left")

        # Tabela
        tabela_frame = ctk.CTkFrame(self, corner_radius=12)
        tabela_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        kolone = ("ID", "Kandidat", "Instruktor", "Datum", "Vreme", "Status", "Napomena")

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

        sirine = {"ID": 45, "Kandidat": 160, "Instruktor": 160,
                  "Datum": 110, "Vreme": 70, "Status": 90, "Napomena": 180}
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
        casovi = Cas.get_all()

        filter_status = self._filter_var.get()
        if filter_status != "Svi":
            casovi = [c for c in casovi if c.status == filter_status]

        boje_tag = {"zakazan": "zakazan_tag", "odrzan": "odrzan_tag", "otkazan": "otkazan_tag"}
        self._tabela.tag_configure("zakazan_tag", background="#1a3a6a")
        self._tabela.tag_configure("odrzan_tag", background="#1a4a2e")
        self._tabela.tag_configure("otkazan_tag", background="#5a1a1a")

        for c in casovi:
            kandidat_ime = f"{c.kandidat_ime or ''} {c.kandidat_prezime or ''}".strip() or f"ID {c.kandidat_id}"
            instruktor_ime = f"{c.instruktor_ime or ''} {c.instruktor_prezime or ''}".strip() or f"ID {c.instruktor_id}"
            tag = boje_tag.get(c.status, "")

            self._tabela.insert("", "end", iid=str(c.id), tags=(tag,), values=(
                c.id, kandidat_ime, instruktor_ime,
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
        prozor.title("Novi čas" if je_novi else "Izmena časa")
        prozor.geometry("420x500")
        prozor.resizable(False, False)
        prozor.grab_set()

        ctk.CTkLabel(prozor,
                     text="Novi čas" if je_novi else "Izmena časa",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(24, 16))

        forma = ctk.CTkFrame(prozor, fg_color="transparent")
        forma.pack(fill="both", expand=True, padx=30)
        forma.columnconfigure(0, weight=1)

        # Kandidat dropdown
        kandidati = Kandidat.get_all()
        kandidat_opcije = [f"{k.id} — {k.ime} {k.prezime}" for k in kandidati]

        ctk.CTkLabel(forma, text="Kandidat *", anchor="w").grid(
            row=0, column=0, sticky="w", pady=(8, 0))
        kandidat_var = ctk.StringVar()
        if cas and kandidati:
            for k in kandidati:
                if k.id == cas.kandidat_id:
                    kandidat_var.set(f"{k.id} — {k.ime} {k.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=kandidat_var,
                          values=kandidat_opcije if kandidat_opcije else ["—"],
                          width=280).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        # Instruktor dropdown
        instruktori = Instruktor.get_all(samo_aktivni=True)
        instruktor_opcije = [f"{i.id} — {i.ime} {i.prezime}" for i in instruktori]

        ctk.CTkLabel(forma, text="Instruktor *", anchor="w").grid(
            row=2, column=0, sticky="w", pady=(8, 0))
        instruktor_var = ctk.StringVar()
        if cas and instruktori:
            for i in instruktori:
                if i.id == cas.instruktor_id:
                    instruktor_var.set(f"{i.id} — {i.ime} {i.prezime}")
                    break
        ctk.CTkOptionMenu(forma, variable=instruktor_var,
                          values=instruktor_opcije if instruktor_opcije else ["—"],
                          width=280).grid(row=3, column=0, sticky="ew", pady=(2, 0))

        # Datum i vreme
        ctk.CTkLabel(forma, text="Datum (YYYY-MM-DD) *", anchor="w").grid(
            row=4, column=0, sticky="w", pady=(8, 0))
        e_datum = ctk.CTkEntry(forma, width=280)
        e_datum.grid(row=5, column=0, sticky="ew", pady=(2, 0))
        if cas and cas.datum:
            e_datum.insert(0, cas.datum)

        ctk.CTkLabel(forma, text="Vreme (HH:MM)", anchor="w").grid(
            row=6, column=0, sticky="w", pady=(8, 0))
        e_vreme = ctk.CTkEntry(forma, width=280)
        e_vreme.grid(row=7, column=0, sticky="ew", pady=(2, 0))
        if cas and cas.vreme:
            e_vreme.insert(0, cas.vreme)

        ctk.CTkLabel(forma, text="Status", anchor="w").grid(
            row=8, column=0, sticky="w", pady=(8, 0))
        status_var = ctk.StringVar(value=cas.status if cas else "zakazan")
        ctk.CTkOptionMenu(forma, variable=status_var,
                          values=["zakazan", "odrzan", "otkazan"],
                          width=280).grid(row=9, column=0, sticky="ew", pady=(2, 0))

        ctk.CTkLabel(forma, text="Napomena", anchor="w").grid(
            row=10, column=0, sticky="w", pady=(8, 0))
        e_napomena = ctk.CTkEntry(forma, width=280)
        e_napomena.grid(row=11, column=0, sticky="ew", pady=(2, 0))
        if cas and cas.napomena:
            e_napomena.insert(0, cas.napomena)

        def sacuvaj():
            if not kandidat_var.get() or kandidat_var.get() == "—":
                messagebox.showerror("Greška", "Izaberite kandidata!", parent=prozor)
                return
            if not instruktor_var.get() or instruktor_var.get() == "—":
                messagebox.showerror("Greška", "Izaberite instruktora!", parent=prozor)
                return
            datum = e_datum.get().strip()
            if not datum:
                messagebox.showerror("Greška", "Datum je obavezan!", parent=prozor)
                return

            kandidat_id = int(kandidat_var.get().split(" — ")[0])
            instruktor_id = int(instruktor_var.get().split(" — ")[0])

            c = cas if cas else Cas()
            c.kandidat_id = kandidat_id
            c.instruktor_id = instruktor_id
            c.datum = datum
            c.vreme = e_vreme.get().strip() or None
            c.status = status_var.get()
            c.napomena = e_napomena.get().strip() or None

            try:
                c.sacuvaj()
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
        if messagebox.askyesno("Potvrda", "Obriši ovaj čas?"):
            try:
                c = Cas()
                c.id = self._izabrani_id
                c.obrisi()
                self._ucitaj_podatke()
            except Exception as ex:
                messagebox.showerror("Greška", str(ex))

    def osvezi(self):
        self._ucitaj_podatke()
