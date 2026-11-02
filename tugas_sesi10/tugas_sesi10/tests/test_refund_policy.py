"""Basis path testing untuk persen_refund (V(G) = 5) dan hitung_refund."""
import pytest

from sesi10.refund_policy import JAM_MS, TripSudahBerangkatError, hitung_refund, persen_refund

BERANGKAT = 1_000 * JAM_MS


def sisa_jam(jam):
    """Waktu 'sekarang' yang membuat sisa waktu tepat sebanyak jam (boleh pecahan)."""
    return BERANGKAT - int(jam * JAM_MS)


# Lima jalur independen dari control flow graph persen_refund.
def test_jalur1_sudah_berangkat_ditolak():
    with pytest.raises(TripSudahBerangkatError):
        persen_refund(BERANGKAT, sisa_jam(-1))


def test_jalur2_72_jam_atau_lebih_refund_90():
    assert persen_refund(BERANGKAT, sisa_jam(100)) == 90


def test_jalur3_24_sampai_kurang_72_jam_refund_75():
    assert persen_refund(BERANGKAT, sisa_jam(48)) == 75


def test_jalur4_3_sampai_kurang_24_jam_refund_50():
    assert persen_refund(BERANGKAT, sisa_jam(10)) == 50


def test_jalur5_kurang_dari_3_jam_refund_0():
    assert persen_refund(BERANGKAT, sisa_jam(1)) == 0


# Nilai batas (BVA) pada setiap keputusan.
@pytest.mark.parametrize("sisa_ms, diharapkan", [
    (0, "ditolak"),
    (1, 0),
    (3 * JAM_MS - 1, 0),
    (3 * JAM_MS, 50),
    (24 * JAM_MS - 1, 50),
    (24 * JAM_MS, 75),
    (72 * JAM_MS - 1, 75),
    (72 * JAM_MS, 90),
])
def test_batas_sisa_waktu(sisa_ms, diharapkan):
    sekarang = BERANGKAT - sisa_ms
    if diharapkan == "ditolak":
        with pytest.raises(TripSudahBerangkatError):
            persen_refund(BERANGKAT, sekarang)
    else:
        assert persen_refund(BERANGKAT, sekarang) == diharapkan


@pytest.mark.parametrize("nominal, persen, hasil", [
    (100_000, 90, 90_000),
    (100_000, 0, 0),
    (100_000, 100, 100_000),
    (0, 50, 0),
    (999, 50, 499),
])
def test_hitung_refund_valid(nominal, persen, hasil):
    assert hitung_refund(nominal, persen) == hasil


@pytest.mark.parametrize("nominal, persen", [(-1, 50), (1000, -1), (1000, 101)])
def test_hitung_refund_tidak_valid(nominal, persen):
    with pytest.raises(ValueError):
        hitung_refund(nominal, persen)
