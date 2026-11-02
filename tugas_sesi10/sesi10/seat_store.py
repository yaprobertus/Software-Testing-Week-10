"""Polimorfisme: penyimpanan klaim kursi per segmen (port sederhana dari SeatStore di Rangkai).

SeatStore adalah kontrak abstrak. InMemorySeatStore dan SqliteSeatStore adalah dua implementasinya.
"""
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SegmentRange:
    """Rentang segmen [dari, sampai). Surabaya-Madiun dan Madiun-Yogyakarta tidak tumpang tindih."""
    dari: int
    sampai: int

    def __post_init__(self):
        if self.dari < 0:
            raise ValueError("Indeks awal tidak boleh negatif")
        if self.sampai <= self.dari:
            raise ValueError("Stasiun tujuan harus setelah stasiun asal")

    def tumpang_tindih(self, lain):
        return self.dari < lain.sampai and lain.dari < self.sampai

    def segmen(self):
        return list(range(self.dari, self.sampai))


class SeatStore(ABC):
    @abstractmethod
    def klaim(self, trip, kursi, rentang, pemilik, kedaluwarsa_pada, sekarang):
        """Klaim semua segmen semua kursi secara atomik. Mengembalikan daftar konflik (kursi, segmen).

        Daftar kosong berarti berhasil. Klaim yang sudah kedaluwarsa dianggap kosong dan diambil alih.
        """

    @abstractmethod
    def lepas(self, pemilik):
        """Melepas semua klaim milik pemilik. Mengembalikan jumlah klaim yang dilepas."""

    def tutup(self):
        """Melepas sumber daya penyimpanan. Bawaan: tidak ada yang perlu dilepas."""


class InMemorySeatStore(SeatStore):
    def __init__(self):
        self._klaim = {}  # (trip, kursi, segmen) -> (pemilik, kedaluwarsa_pada)

    def klaim(self, trip, kursi, rentang, pemilik, kedaluwarsa_pada, sekarang):
        kunci = [(trip, k, s) for k in kursi for s in rentang.segmen()]
        konflik = [
            (k, s) for (t, k, s) in kunci
            if (t, k, s) in self._klaim and self._klaim[(t, k, s)][1] > sekarang
        ]
        if konflik:
            return konflik
        for kunci_klaim in kunci:
            self._klaim[kunci_klaim] = (pemilik, kedaluwarsa_pada)
        return []

    def lepas(self, pemilik):
        milik = [k for k, (p, _) in self._klaim.items() if p == pemilik]
        for k in milik:
            del self._klaim[k]
        return len(milik)


class SqliteSeatStore(SeatStore):
    def __init__(self):
        self._db = sqlite3.connect(":memory:")
        self._db.execute(
            "CREATE TABLE klaim (trip TEXT, kursi TEXT, segmen INTEGER, pemilik TEXT, "
            "kedaluwarsa_pada INTEGER, PRIMARY KEY (trip, kursi, segmen))"
        )

    def klaim(self, trip, kursi, rentang, pemilik, kedaluwarsa_pada, sekarang):
        konflik = []
        for k in kursi:
            for s in rentang.segmen():
                baris = self._db.execute(
                    "SELECT kedaluwarsa_pada FROM klaim WHERE trip=? AND kursi=? AND segmen=?",
                    (trip, k, s),
                ).fetchone()
                if baris is not None and baris[0] > sekarang:
                    konflik.append((k, s))
        if konflik:
            return konflik
        with self._db:
            for k in kursi:
                for s in rentang.segmen():
                    self._db.execute(
                        "INSERT OR REPLACE INTO klaim VALUES (?, ?, ?, ?, ?)",
                        (trip, k, s, pemilik, kedaluwarsa_pada),
                    )
        return []

    def lepas(self, pemilik):
        with self._db:
            return self._db.execute("DELETE FROM klaim WHERE pemilik=?", (pemilik,)).rowcount

    def tutup(self):
        self._db.close()
