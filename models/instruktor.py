from database.db_manager import get_connection


class Instruktor:
    def __init__(self):
        self.id = None
        self.ime = ""
        self.prezime = ""
        self.telefon = None
        self.kategorija = "B"
        self.aktivan = 1

    @staticmethod
    def get_all(samo_aktivni=True):
        conn = get_connection()
        if samo_aktivni:
            rows = conn.execute(
                "SELECT * FROM instruktori WHERE aktivan = 1 ORDER BY prezime, ime"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM instruktori ORDER BY prezime, ime"
            ).fetchall()
        conn.close()
        return [Instruktor._from_row(r) for r in rows]

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM instruktori WHERE id = ?", (id,)
        ).fetchone()
        conn.close()
        return Instruktor._from_row(row) if row else None

    def sacuvaj(self):
        conn = get_connection()
        if self.id is None:
            cur = conn.execute(
                "INSERT INTO instruktori (ime, prezime, telefon, kategorija, aktivan) VALUES (?, ?, ?, ?, ?)",
                (self.ime, self.prezime, self.telefon, self.kategorija, self.aktivan)
            )
            self.id = cur.lastrowid
        else:
            conn.execute(
                "UPDATE instruktori SET ime=?, prezime=?, telefon=?, kategorija=?, aktivan=? WHERE id=?",
                (self.ime, self.prezime, self.telefon, self.kategorija, self.aktivan, self.id)
            )
        conn.commit()
        conn.close()

    def obrisi(self):
        conn = get_connection()
        conn.execute("DELETE FROM instruktori WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def _from_row(row):
        i = Instruktor()
        i.id = row["id"]
        i.ime = row["ime"]
        i.prezime = row["prezime"]
        i.telefon = row["telefon"]
        i.kategorija = row["kategorija"]
        i.aktivan = row["aktivan"]
        return i
