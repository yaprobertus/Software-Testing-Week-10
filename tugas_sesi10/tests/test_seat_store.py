"""Polimorfisme: satu rangkaian test kontrak dijalankan terhadap semua implementasi SeatStore."""
import sqlite3

import pytest

from sesi10.seat_store import InMemorySeatStore, SeatStore, SegmentRange, SqliteSeatStore

IMPLEMENTASI = [InMemorySeatStore, SqliteSeatStore]
SBY_MN = SegmentRange(0, 1)     # Surabaya-Madiun
MN_YK = SegmentRange(1, 2)      # Madiun-Yogyakarta
SBY_YK = SegmentRange(0, 2)     # Surabaya-Yogyakarta (melewati Madiun)


@pytest.fixture(params=IMPLEMENTASI, ids=lambda k: k.__name__)
def store(request):
    penyimpanan = request.param()
    yield penyimpanan
    penyimpanan.tutup()


def test_kelas_abstrak_tidak_bisa_diinstansiasi():
    with pytest.raises(TypeError):
        SeatStore()


@pytest.mark.parametrize("kelas", IMPLEMENTASI)
def test_implementasi_adalah_subclass_seatstore(kelas):
    objek = kelas()
    assert issubclass(kelas, SeatStore) and isinstance(objek, SeatStore)
    objek.tutup()


def test_klaim_kosong_berhasil(store):
    assert store.klaim("T1", ["EKS1-1A"], SBY_MN, "u1", 1000, 0) == []


def test_kursi_sama_ruas_sama_berkonflik(store):
    store.klaim("T1", ["EKS1-1A"], SBY_MN, "u1", 1000, 0)
    assert store.klaim("T1", ["EKS1-1A"], SBY_MN, "u2", 1000, 0) == [("EKS1-1A", 0)]


def test_kursi_sama_ruas_bersebelahan_tidak_berkonflik(store):
    store.klaim("T1", ["EKS1-1A"], SBY_MN, "u1", 1000, 0)
    assert store.klaim("T1", ["EKS1-1A"], MN_YK, "u2", 1000, 0) == []


def test_ruas_panjang_berkonflik_dengan_ruas_pendek(store):
    store.klaim("T1", ["EKS1-1A"], MN_YK, "u1", 1000, 0)
    assert store.klaim("T1", ["EKS1-1A"], SBY_YK, "u2", 1000, 0) == [("EKS1-1A", 1)]


def test_kursi_atau_trip_berbeda_tidak_berkonflik(store):
    store.klaim("T1", ["EKS1-1A"], SBY_MN, "u1", 1000, 0)
    assert store.klaim("T1", ["EKS1-1B"], SBY_MN, "u2", 1000, 0) == []
    assert store.klaim("T2", ["EKS1-1A"], SBY_MN, "u3", 1000, 0) == []


def test_klaim_atomik_semua_atau_tidak_sama_sekali(store):
    store.klaim("T1", ["EKS1-1B"], SBY_MN, "u1", 1000, 0)
    assert store.klaim("T1", ["EKS1-1A", "EKS1-1B"], SBY_MN, "u2", 1000, 0) == [("EKS1-1B", 0)]
    assert store.klaim("T1", ["EKS1-1A"], SBY_MN, "u3", 1000, 0) == []  # 1A tidak ikut tertahan


def test_klaim_kedaluwarsa_diambil_alih(store):
    store.klaim("T1", ["EKS1-1A"], SBY_MN, "u1", 100, 0)
    assert store.klaim("T1", ["EKS1-1A"], SBY_MN, "u2", 1100, 100) == []
    assert store.klaim("T1", ["EKS1-1A"], SBY_MN, "u3", 1100, 200) == [("EKS1-1A", 0)]


def test_lepas_membebaskan_kursi_dan_mengembalikan_jumlah(store):
    store.klaim("T1", ["EKS1-1A", "EKS1-1B"], SBY_YK, "u1", 1000, 0)
    assert store.lepas("u1") == 4
    assert store.klaim("T1", ["EKS1-1A"], SBY_YK, "u2", 1000, 0) == []


def test_lepas_pemilik_tanpa_klaim_mengembalikan_nol(store):
    assert store.lepas("tidak-ada") == 0


def test_semua_implementasi_memberi_hasil_sama():
    hasil = []
    for kelas in IMPLEMENTASI:
        s = kelas()
        s.klaim("T1", ["A", "B"], SBY_MN, "u1", 1000, 0)
        hasil.append((s.klaim("T1", ["B", "C"], SBY_YK, "u2", 1000, 0), s.lepas("u1")))
        s.tutup()
    assert hasil[0] == hasil[1]


def test_segment_range_tumpang_tindih_dan_segmen():
    assert SBY_MN.tumpang_tindih(SBY_YK) and not SBY_MN.tumpang_tindih(MN_YK)
    assert SBY_YK.segmen() == [0, 1]


@pytest.mark.parametrize("dari, sampai", [(-1, 1), (2, 2), (3, 1)])
def test_segment_range_tidak_valid(dari, sampai):
    with pytest.raises(ValueError):
        SegmentRange(dari, sampai)


def test_tutup_in_memory_aman_dipanggil():
    InMemorySeatStore().tutup()


def test_tutup_sqlite_menutup_koneksi():
    s = SqliteSeatStore()
    s.tutup()
    with pytest.raises(sqlite3.ProgrammingError):
        s.lepas("u1")
