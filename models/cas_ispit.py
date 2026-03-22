from database.db_manager import get_connection


class Cas:
    def __init__(self):
        self.id = None
        self.kandidat_id = None
        self.instruktor_id = None
        self.datum = None
        self.vreme = None
        self.status = "zakazan"
        self.napomena = None
        self.kandidat_ime = None
        self.kandidat_prezime = None
        self.instruktor_ime = None
        self.instruktor_prezime = None

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.*, 
                   k.ime as kandidat_ime, k.prezime as kandidat_prezime,
                   i.ime as instruktor_ime, i.prezime as instruktor_prezime
            FROM casovi c
            LEFT JOIN kandidati k ON c.kandidat_id = k.id
            LEFT JOIN instruktori i ON c.instruktor_id = i.id
            ORDER BY c.datum DESC, c.vreme
        """).fetchall()
        conn.close()
        return [Cas._from_row(r) for r in rows]

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute("""
            SELECT c.*,
                   k.ime as kandidat_ime, k.prezime as kandidat_prezime,
                   i.ime as instruktor_ime, i.prezime as instruktor_prezime
            FROM casovi c
            LEFT JOIN kandidati k ON c.kandidat_id = k.id
            LEFT JOIN instruktori i ON c.instruktor_id = i.id
            WHERE c.id = ?
        """, (id,)).fetchone()
        conn.close()
        return Cas._from_row(row) if row else None

    @staticmethod
    def get_by_kandidat(kandidat_id):
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.*,
                   k.ime as kandidat_ime, k.prezime as kandidat_prezime,
                   i.ime as instruktor_ime, i.prezime as instruktor_prezime
            FROM casovi c
            LEFT JOIN kandidati k ON c.kandidat_id = k.id
            LEFT JOIN instruktori i ON c.instruktor_id = i.id
            WHERE c.kandidat_id = ?
            ORDER BY c.datum DESC
        """, (kandidat_id,)).fetchall()
        conn.close()
        return [Cas._from_row(r) for r in rows]

    @staticmethod
    def ukupno_casova(kandidat_id):
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as broj FROM casovi WHERE kandidat_id = ? AND status = 'odrzan'",
            (kandidat_id,)
        ).fetchone()
        conn.close()
        return row["broj"] if row else 0

    def sacuvaj(self):
        conn = get_connection()
        if self.id is None:
            cur = conn.execute(
                "INSERT INTO casovi (kandidat_id, instruktor_id, datum, vreme, status, napomena) VALUES (?, ?, ?, ?, ?, ?)",
                (self.kandidat_id, self.instruktor_id, self.datum, self.vreme, self.status, self.napomena)
            )
            self.id = cur.lastrowid
        else:
            conn.execute(
                "UPDATE casovi SET kandidat_id=?, instruktor_id=?, datum=?, vreme=?, status=?, napomena=? WHERE id=?",
                (self.kandidat_id, self.instruktor_id, self.datum, self.vreme, self.status, self.napomena, self.id)
            )
        conn.commit()
        conn.close()

    def obrisi(self):
        conn = get_connection()
        conn.execute("DELETE FROM casovi WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def _from_row(row):
        c = Cas()
        c.id = row["id"]
        c.kandidat_id = row["kandidat_id"]
        c.instruktor_id = row["instruktor_id"]
        c.datum = row["datum"]
        c.vreme = row["vreme"]
        c.status = row["status"]
        c.napomena = row["napomena"]
        c.kandidat_ime = row["kandidat_ime"]
        c.kandidat_prezime = row["kandidat_prezime"]
        c.instruktor_ime = row["instruktor_ime"]
        c.instruktor_prezime = row["instruktor_prezime"]
        return c


class Ispit:
    def __init__(self):
        self.id = None
        self.kandidat_id = None
        self.tip = "teorija"
        self.datum = None
        self.rezultat = "ceka"
        self.napomena = None
        self.kandidat_ime = None
        self.kandidat_prezime = None

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT i.*, k.ime as kandidat_ime, k.prezime as kandidat_prezime
            FROM ispiti i
            LEFT JOIN kandidati k ON i.kandidat_id = k.id
            ORDER BY i.datum DESC
        """).fetchall()
        conn.close()
        return [Ispit._from_row(r) for r in rows]

    @staticmethod
    def get_by_id(id):
        conn = get_connection()
        row = conn.execute("""
            SELECT i.*, k.ime as kandidat_ime, k.prezime as kandidat_prezime
            FROM ispiti i
            LEFT JOIN kandidati k ON i.kandidat_id = k.id
            WHERE i.id = ?
        """, (id,)).fetchone()
        conn.close()
        return Ispit._from_row(row) if row else None

    @staticmethod
    def get_by_kandidat(kandidat_id):
        conn = get_connection()
        rows = conn.execute("""
            SELECT i.*, k.ime as kandidat_ime, k.prezime as kandidat_prezime
            FROM ispiti i
            LEFT JOIN kandidati k ON i.kandidat_id = k.id
            WHERE i.kandidat_id = ?
            ORDER BY i.datum DESC
        """, (kandidat_id,)).fetchall()
        conn.close()
        return [Ispit._from_row(r) for r in rows]

    def sacuvaj(self):
        conn = get_connection()
        if self.id is None:
            cur = conn.execute(
                "INSERT INTO ispiti (kandidat_id, tip, datum, rezultat, napomena) VALUES (?, ?, ?, ?, ?)",
                (self.kandidat_id, self.tip, self.datum, self.rezultat, self.napomena)
            )
            self.id = cur.lastrowid
        else:
            conn.execute(
                "UPDATE ispiti SET kandidat_id=?, tip=?, datum=?, rezultat=?, napomena=? WHERE id=?",
                (self.kandidat_id, self.tip, self.datum, self.rezultat, self.napomena, self.id)
            )
        conn.commit()
        conn.close()

    def obrisi(self):
        conn = get_connection()
        conn.execute("DELETE FROM ispiti WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    @staticmethod
    def _from_row(row):
        i = Ispit()
        i.id = row["id"]
        i.kandidat_id = row["kandidat_id"]
        i.tip = row["tip"]
        i.datum = row["datum"]
        i.rezultat = row["rezultat"]
        i.napomena = row["napomena"]
        i.kandidat_ime = row["kandidat_ime"]
        i.kandidat_prezime = row["kandidat_prezime"]
        return i
