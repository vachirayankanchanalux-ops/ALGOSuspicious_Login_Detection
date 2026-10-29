"""
CNC211 การบ้านครั้งที่ 2: การทดลองวัดเวลาเมื่อข้อมูลมากขึ้น
เปรียบเทียบ 3 วิธี
  A = BruteForce2.py      (Selection Sort + Sequential Scan)
  B = SequentialScan.py   (Mergesort + Sequential Scan)
  C = SlidingWindow.py    (Mergesort ตามเวลา + Sliding Window)

วิธีรัน: วางไฟล์นี้ไว้โฟลเดอร์เดียวกับ 3 ไฟล์ข้างบน แล้วรัน
    python3 experiment.py
ผลลัพธ์: ตารางบนหน้าจอ + results.csv + graph.png
"""
import csv
import random
import statistics
import time
from datetime import datetime, timedelta

import BruteForce2 as A
import SequentialScan as B
import SlidingWindow as C

SIZES = [1000, 2000, 4000, 8000]   # จำนวนแถวของ Log จำลอง
REPEAT = 3                          # รันซ้ำกี่รอบ แล้วใช้ค่ากลาง (median)
SEED = 42                           # ตั้งค่า seed ให้สุ่มได้ผลเดิมทุกครั้ง


# ---------- 1) สร้าง Log จำลอง ----------
def make_log(n, seed=SEED):
    """สุ่ม Log n แถว: บัญชี n/20 บัญชี เวลาใน 1 วัน FAILED 60% / SUCCESS 40%"""
    rnd = random.Random(seed)
    base = datetime(2026, 10, 1)
    users = max(5, n // 20)
    log = []
    for _ in range(n):
        user = f"user{rnd.randrange(users)}"
        t = base + timedelta(seconds=rnd.randrange(86400))
        status = "FAILED" if rnd.random() < 0.6 else "SUCCESS"
        log.append((user, t, "10.0.0.1", status))
    return log


# ---------- 2) ฟังก์ชันรันแต่ละวิธี (เรียงบนสำเนา ไม่แก้ข้อมูลต้นฉบับ) ----------
def run_A(log):
    R = log[:]
    A.comparisons = 0
    A.selection_sort(R)
    return A.scan(R)

def run_B(log):
    R = log[:]
    B.merge_sort(R)
    return B.scan(R)

def run_C(log):
    R = log[:]
    C.merge_sort(R)
    return C.sliding_window(R)

METHODS = [("A", "Brute Force", run_A), ("B", "Mergesort + Scan", run_B), ("C", "Sliding Window", run_C)]


def measure(func, log):
    """จับเวลา REPEAT รอบ คืนค่ากลางเป็นมิลลิวินาที"""
    times = []
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        func(log)
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.median(times)


def main():
    # ตรวจความถูกต้องก่อนวัดเวลา: ทุกวิธีต้องได้ชื่อบัญชีตรงกัน
    real = A.read_log("login.txt")
    names = [sorted({a[0] for a in f(real)}) for _, _, f in METHODS]
    assert names[0] == names[1] == names[2] == ["david", "frank"], names
    print("ตรวจกับ login.txt: ทั้ง 3 วิธีได้", names[0])

    results = {k: [] for k, _, _ in METHODS}
    for n in SIZES:
        log = make_log(n)
        for k, _, f in METHODS:
            results[k].append(measure(f, log))
        print(f"  n = {n:>5}  เสร็จ")

    # ---------- 3) ตาราง ----------
    print(f"\n{'n':>6} | {'A (ms)':>10} {'B (ms)':>8} {'C (ms)':>8} | {'A โต':>6} {'B โต':>6} {'C โต':>6} | A/B")
    rows = []
    for i, n in enumerate(SIZES):
        a, b, c = (results[k][i] for k in "ABC")
        g = ["-"] * 3 if i == 0 else [f"{results[k][i] / results[k][i-1]:.1f}x" for k in "ABC"]
        print(f"{n:>6} | {a:>10.1f} {b:>8.1f} {c:>8.1f} | {g[0]:>6} {g[1]:>6} {g[2]:>6} | {a/b:.0f}x")
        rows.append([n, round(a, 1), round(b, 1), round(c, 1)])

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "A_ms", "B_ms", "C_ms"])
        w.writerows(rows)
    print("\nบันทึก results.csv แล้ว")

    # ---------- 4) กราฟ ----------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("ไม่มี matplotlib: ติดตั้งด้วย pip install matplotlib แล้วรันใหม่เพื่อสร้างกราฟ")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.4))
    style = {"A": dict(color="#2f5bd3", lw=2.5), "B": dict(color="#555b66", lw=2), "C": dict(color="#9aa0ab", lw=2, ls="--")}
    for k, name, _ in METHODS:
        ax1.plot(SIZES, results[k], marker="o", label=f"{k}. {name}", **style[k])
        if k != "A":
            ax2.plot(SIZES, results[k], marker="o", label=f"{k}. {name}", **style[k])
    ax1.set_title("(a) All 3 methods")
    ax2.set_title("(b) Zoom: B and C only")
    for ax in (ax1, ax2):
        ax.set_xlabel("Number of log rows (n)")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(SIZES)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig("graph.png", dpi=200)
    print("บันทึก graph.png แล้ว")


if __name__ == "__main__":
    main()
