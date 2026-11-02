"""State-based testing untuk class Pesanan: 5 state x 4 event = 20 pasangan."""
import pytest

from sesi10.pesanan import Pesanan, StatusPesanan as S, TransisiTidakValidError

# Jalur terpendek dari state awal ke setiap state.
JALUR = {
    S.MENUNGGU_PEMBAYARAN: [],
    S.DIKONFIRMASI: ["bayar"],
    S.CHECK_IN: ["bayar", "check_in"],
    S.DIBATALKAN: ["batalkan"],
    S.KEDALUWARSA: ["kedaluwarsa"],
}

EVENT = ["bayar", "check_in", "batalkan", "kedaluwarsa"]

VALID = {
    (S.MENUNGGU_PEMBAYARAN, "bayar"): S.DIKONFIRMASI,
    (S.MENUNGGU_PEMBAYARAN, "batalkan"): S.DIBATALKAN,
    (S.MENUNGGU_PEMBAYARAN, "kedaluwarsa"): S.KEDALUWARSA,
    (S.DIKONFIRMASI, "check_in"): S.CHECK_IN,
    (S.DIKONFIRMASI, "batalkan"): S.DIBATALKAN,
}

TIDAK_VALID = [(s, e) for s in S for e in EVENT if (s, e) not in VALID]


def pesanan_di(status):
    p = Pesanan()
    for event in JALUR[status]:
        getattr(p, event)()
    assert p.status == status
    return p


def test_state_awal_menunggu_pembayaran():
    assert Pesanan().status == S.MENUNGGU_PEMBAYARAN


@pytest.mark.parametrize("awal, event", list(VALID))
def test_transisi_valid(awal, event):
    p = pesanan_di(awal)
    getattr(p, event)()
    assert p.status == VALID[(awal, event)]


@pytest.mark.parametrize("awal, event", TIDAK_VALID)
def test_transisi_tidak_valid_ditolak_dan_state_tetap(awal, event):
    p = pesanan_di(awal)
    with pytest.raises(TransisiTidakValidError):
        getattr(p, event)()
    assert p.status == awal


def test_jumlah_pasangan_lengkap():
    assert len(VALID) + len(TIDAK_VALID) == 20 and len(TIDAK_VALID) == 15


def test_bayar_ganda_ditolak():
    p = pesanan_di(S.DIKONFIRMASI)
    with pytest.raises(TransisiTidakValidError):
        p.bayar()


def test_urutan_penuh_sampai_check_in():
    p = Pesanan()
    p.bayar()
    p.check_in()
    assert p.status == S.CHECK_IN and p.sudah_final()


@pytest.mark.parametrize("status, dapat", [
    (S.MENUNGGU_PEMBAYARAN, True), (S.DIKONFIRMASI, True),
    (S.CHECK_IN, False), (S.DIBATALKAN, False), (S.KEDALUWARSA, False),
])
def test_dapat_dibatalkan_dan_status_final(status, dapat):
    p = pesanan_di(status)
    assert p.dapat_dibatalkan() is dapat
    assert p.sudah_final() is (status not in (S.MENUNGGU_PEMBAYARAN, S.DIKONFIRMASI))
