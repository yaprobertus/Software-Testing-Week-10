"""Modul prosedural: kebijakan pengembalian dana (port sederhana dari RefundPolicy.java di Rangkai)."""

JAM_MS = 3_600_000  # satu jam dalam milidetik


class TripSudahBerangkatError(Exception):
    """Kereta sudah berangkat sehingga pesanan tidak bisa dibatalkan (kode TRIP_DEPARTED)."""


def persen_refund(waktu_berangkat, sekarang):
    """Menentukan persentase refund berdasarkan sisa waktu sebelum berangkat (milidetik).

    Empat keputusan, jadi V(G) = 4 + 1 = 5.
    """
    sisa = waktu_berangkat - sekarang
    if sisa <= 0:                    # keputusan 1: kereta sudah berangkat
        raise TripSudahBerangkatError("Kereta sudah berangkat, pesanan tidak bisa dibatalkan.")
    if sisa >= 72 * JAM_MS:          # keputusan 2: 72 jam atau lebih
        return 90
    if sisa >= 24 * JAM_MS:          # keputusan 3: 24 jam sampai kurang dari 72 jam
        return 75
    if sisa >= 3 * JAM_MS:           # keputusan 4: 3 jam sampai kurang dari 24 jam
        return 50
    return 0                         # kurang dari 3 jam


def hitung_refund(nominal, persen):
    """Nominal refund dalam rupiah: nominal x persen / 100 (pembagian bulat ke bawah)."""
    if nominal < 0:
        raise ValueError("Nominal tidak boleh negatif")
    if persen < 0 or persen > 100:
        raise ValueError("Persentase harus 0 sampai 100")
    return nominal * persen // 100
