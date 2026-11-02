import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = ["Liberation Serif", "DejaVu Serif"]
plt.rcParams["font.size"] = 12


def panah(ax, a, b, rad=0.0, label=None, lpos=(0, 0), shrinkA=0, shrinkB=0, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, color="black", lw=1.1,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=shrinkA, shrinkB=shrinkB, linestyle=ls))
    if label:
        ax.text((a[0] + b[0]) / 2 + lpos[0], (a[1] + b[1]) / 2 + lpos[1], label, ha="center", va="center",
                fontsize=9.3, color="black", bbox=dict(fc="white", ec="none", pad=0.6))


def garis(ax, a, b):
    ax.plot([a[0], b[0]], [a[1], b[1]], color="black", lw=1.1, solid_capstyle="butt")


# ---------- Gambar 1: CFG persen_refund ----------
fig, ax = plt.subplots(figsize=(5.4, 6.2))
ax.set_xlim(-1.2, 6.0); ax.set_ylim(-1.2, 9.2); ax.axis("off"); ax.set_aspect("equal")
R = 0.38
pos = {1: (0, 8), 2: (3, 8), 3: (0, 6), 4: (3, 6), 5: (0, 4), 6: (3, 4), 7: (0, 2), 8: (3, 2), 9: (0, 0), 10: (5, 0)}
for n, (x, y) in pos.items():
    ax.add_patch(Circle((x, y), R, fc="white", ec="black", lw=1.4))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=13)
ax.add_patch(Circle(pos[10], R + 0.12, fc="none", ec="black", lw=1.0))
# keputusan: ya ke kanan, tidak ke bawah
for d, nxt, leaf in [(1, 3, 2), (3, 5, 4), (5, 7, 6), (7, 9, 8)]:
    x, y = pos[d]
    panah(ax, (x + R, y), (pos[leaf][0] - R, pos[leaf][1]), label="ya", lpos=(0, 0.28), shrinkA=1, shrinkB=1)
    panah(ax, (x, y - R), (pos[nxt][0], pos[nxt][1] + R), label="tidak", lpos=(0.45, 0), shrinkA=1, shrinkB=1)
# daun menuju simpul keluar lewat jalur vertikal x = 5
for leaf in (2, 4, 6, 8):
    x, y = pos[leaf]
    garis(ax, (x + R, y), (5, y))
garis(ax, (5, 8), (5, 1.25))
panah(ax, (5, 1.25), (5, 0.52), shrinkA=0, shrinkB=0)
panah(ax, (pos[9][0] + R, 0), (pos[10][0] - R - 0.12, 0), shrinkA=1, shrinkB=1)
fig.savefig("laporan/cfg_persen_refund.png", dpi=220, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------- Gambar 2: state machine Pesanan ----------
fig, ax = plt.subplots(figsize=(6.4, 3.9))
ax.set_xlim(-1.4, 16.6); ax.set_ylim(-3.4, 3.9); ax.axis("off"); ax.set_aspect("equal")
W, H = 3.6, 1.3
st = {"MENUNGGU\nPEMBAYARAN": (1.9, 1.7, False), "DIKONFIRMASI": (8.1, 1.7, False), "CHECK_IN": (14.3, 1.7, True),
      "KEDALUWARSA": (1.9, -2.0, True), "DIBATALKAN": (8.1, -2.0, True)}
for nama, (x, y, akhir) in st.items():
    ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.02,rounding_size=0.25", fc="white", ec="black", lw=1.4))
    if akhir:
        ax.add_patch(FancyBboxPatch((x - W / 2 - 0.13, y - H / 2 - 0.13), W + 0.26, H + 0.26, boxstyle="round,pad=0.02,rounding_size=0.3", fc="none", ec="black", lw=1.0))
    ax.text(x, y, nama, ha="center", va="center", fontsize=8.2, linespacing=1.1)
ax.add_patch(Circle((-0.6, 3.4), 0.2, fc="black", ec="black"))
panah(ax, (-0.45, 3.25), (0.7, 2.4), shrinkB=1)
M, D, C, K, B = (1.9, 1.7), (8.1, 1.7), (14.3, 1.7), (1.9, -2.0), (8.1, -2.0)
panah(ax, (M[0] + W / 2, M[1]), (D[0] - W / 2, D[1]), label="bayar()", lpos=(0, 0.45), shrinkA=1, shrinkB=1)
panah(ax, (D[0] + W / 2, D[1]), (C[0] - W / 2 - 0.13, C[1]), label="check_in()", lpos=(0, 0.45), shrinkA=1, shrinkB=1)
panah(ax, (M[0], M[1] - H / 2), (K[0], K[1] + H / 2 + 0.13), label="kedaluwarsa()", lpos=(-1.4, 0), shrinkA=1, shrinkB=1)
panah(ax, (M[0] + 1.1, M[1] - H / 2), (B[0] - 1.3, B[1] + H / 2 + 0.13), label="batalkan()", lpos=(-0.4, -0.6), shrinkA=1, shrinkB=1)
panah(ax, (D[0], D[1] - H / 2), (B[0], B[1] + H / 2 + 0.13), label="batalkan()", lpos=(1.3, 0), shrinkA=1, shrinkB=1)
fig.savefig("laporan/state_pesanan.png", dpi=220, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------- Gambar 3: keluaran coverage ----------
teks = open("laporan/hasil_coverage.txt", encoding="utf-8").read().rstrip().splitlines()
teks = [t for t in teks if t.strip()]
i = next(n for n, t in enumerate(teks) if "tests coverage" in t)
teks = teks[i:]
fig = plt.figure(figsize=(7.4, 0.2 * len(teks) + 0.35))
fig.text(0.015, 0.97, "\n".join(teks), family="DejaVu Sans Mono", fontsize=7.4, va="top", ha="left", color="black", linespacing=1.35)
fig.savefig("laporan/bukti_coverage.png", dpi=220, bbox_inches="tight", facecolor="white", pad_inches=0.12)
plt.close(fig)
print("gambar selesai")
