"""Class OO berbasis state: pesanan tiket (port sederhana dari BookingStatus.java di Rangkai)."""
from enum import Enum


class StatusPesanan(Enum):
    MENUNGGU_PEMBAYARAN = "MENUNGGU_PEMBAYARAN"  # PENDING_PAYMENT
    DIKONFIRMASI = "DIKONFIRMASI"                # CONFIRMED
    CHECK_IN = "CHECK_IN"                        # CHECKED_IN
    DIBATALKAN = "DIBATALKAN"                    # CANCELLED
    KEDALUWARSA = "KEDALUWARSA"                  # EXPIRED


class TransisiTidakValidError(Exception):
    """Perubahan status yang tidak diizinkan (kode INVALID_STATE_TRANSITION)."""


# Tabel transisi valid. Status yang tidak punya baris di sini adalah status akhir.
_TRANSISI = {
    StatusPesanan.MENUNGGU_PEMBAYARAN: {
        "bayar": StatusPesanan.DIKONFIRMASI,
        "batalkan": StatusPesanan.DIBATALKAN,
        "kedaluwarsa": StatusPesanan.KEDALUWARSA,
    },
    StatusPesanan.DIKONFIRMASI: {
        "check_in": StatusPesanan.CHECK_IN,
        "batalkan": StatusPesanan.DIBATALKAN,
    },
}


class Pesanan:
    def __init__(self):
        self.status = StatusPesanan.MENUNGGU_PEMBAYARAN

    def _pindah(self, event):
        tujuan = _TRANSISI.get(self.status, {}).get(event)
        if tujuan is None:
            raise TransisiTidakValidError(
                f"Pesanan berstatus {self.status.name} tidak bisa diproses dengan {event}()."
            )
        self.status = tujuan

    def bayar(self):
        self._pindah("bayar")

    def check_in(self):
        self._pindah("check_in")

    def batalkan(self):
        self._pindah("batalkan")

    def kedaluwarsa(self):
        self._pindah("kedaluwarsa")

    def dapat_dibatalkan(self):
        return "batalkan" in _TRANSISI.get(self.status, {})

    def sudah_final(self):
        return self.status not in _TRANSISI
