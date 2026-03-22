from database.db_manager import get_connection


class Kandidat:
    def __init__(self):
        self.id = None
        self.ime = ""
        self.prezime = ""
        self.jmbg = ""
        self.telefon = None
        self.email = None
        self.datum_upisa = None
        self.status = "aktivan"

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM kandidati ORDER BY prezime, ime"
        ).fetchall()
        conn.close()
        return [Kandidat._from_row(r) for r in rows]

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM kandidati WHERE id = ?", (id,)
        ).fetchone()
        conn.close()
        return Kandidat._from_row(row) if row else None

    @staticmethod
    def pretrazi(upit):
        conn = get_connection()
        q = f"%{upit}%"
        rows = conn.execute(
            "SELECT * FROM kandidati WHERE ime LIKE ? OR prezime LIKE ? OR jmbg LIKE ? OR telefon LIKE ? ORDER BY prezime, ime",
            (q, q, q, q)
        ).fetchall()
        conn.close()
        return [Kandidat._from_row(r) for r in rows]

    @staticmethod
    def broj_po_statusu():
        conn = get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as broj FROM kandidati GROUP BY status"
        ).fetchall()
        conn.close()
        return {r["status"]: r["broj"] for r in rows}

    def sacuvaj(self):
        conn = get_connection()
        if self.id is None:
            cur = conn.execute(
                "INSERT INTO kandidati (ime, prezime, jmbg, telefon, email, datum_upisa, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.ime, self.prezime, self.jmbg, self.telefon, self.email, self.datum_upisa, self.status)
            )
            self.id = cur.lastrowid
        else:
            conn.execute(
                "UPDATE kandidati SET ime=?, prezime=?, jmbg=?, telefon=?, email=?, datum_upisa=?, status=? WHERE id=?",
                (self.ime, self.prezime, self.jmbg, self.telefon, self.email, self.datum_upisa, self.status, self.id)
            )
        conn.commit()
        conn.close()

    def obrisi(self):
        conn = get_connection()
        conn.execute("DELETE FROM kandidati WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def _from_row(row):
        k = Kandidat()
        k.id = row["id"]
        k.ime = row["ime"]
        k.prezime = row["prezime"]
        k.jmbg = row["jmbg"]
        k.telefon = row["telefon"]
        k.email = row["email"]
        k.datum_upisa = row["datum_upisa"]
        k.status = row["status"]
        return k
