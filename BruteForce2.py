"""
CNC211 การบ้านครั้งที่ 2: Suspicious Login Detection
วิธีที่ใช้: Selection Sort (Brute Force) + Sequential Scan

ขั้นตอน
  1. อ่านไฟล์ login
  2. เรียงด้วย Selection Sort ตาม (username, เวลา) -> slide03 สไลด์ 4-7
  3. ไล่ตรวจทีละบรรทัด หา FAILED >= 3 ครั้ง ภายใน 5 นาที
     และเริ่มนับใหม่เมื่อเจอ SUCCESS
  4. แสดง Username, จำนวนครั้งที่ผิด, ช่วงเวลาที่ตรวจพบ

วิธีรัน: python3 bruteforce_login.py login.txt
"""
import csv
import sys
from datetime import datetime, timedelta

WINDOW = timedelta(minutes=5)   # ไม่เกิน 5 นาที
THRESHOLD = 3                   # อย่างน้อย 3 ครั้ง


# ---------------------------------------------------------------
# 1) อ่านไฟล์
# ---------------------------------------------------------------
def read_log(path):
    records = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)                                    # ข้ามหัวตาราง
        for row in reader:
            if not row:
                continue
            ts, user, ip, status = [c.strip() for c in row]
            t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            records.append((user, t, ip, status))
    return records


def key(r):
    """คีย์ที่ใช้เรียง: ชื่อก่อน แล้วค่อยเวลา"""
    return (r[0], r[1])


# ---------------------------------------------------------------
# 2) Selection Sort ตาม ALGORITHM ในสไลด์ (Brute Force)
# ---------------------------------------------------------------
comparisons = 0                         # นับ Basic Operation (slide03 สไลด์ 7)

def selection_sort(A):
    """ALGORITHM SelectionSort(A[0..n-1]) (slide03 สไลด์ 6) เรียงใน A เลย"""
    global comparisons
    n = len(A)
    for i in range(0, n - 1):           # for i = 0 to n-2
        min_ = i
        for j in range(i + 1, n):       # for j = i+1 to n-1
            comparisons += 1
            if key(A[j]) < key(A[min_]):    # A[j] < A[min]
                min_ = j
        A[i], A[min_] = A[min_], A[i]   # swap(A[i], A[min])


# ---------------------------------------------------------------
# 3) Sequential Scan: ไล่ตรวจข้อมูลที่เรียงแล้ว
# ---------------------------------------------------------------
def check_run(user, run, alerts):
    """run = เวลาของ FAILED ที่ติดกันของบัญชีเดียว"""
    i = 0
    while i < len(run):
        j = i
        while j + 1 < len(run) and run[j + 1] - run[i] <= WINDOW:
            j += 1
        if j - i + 1 >= THRESHOLD:
            alerts.append((user, j - i + 1, run[i], run[j]))
            i = j + 1
        else:
            i += 1


def scan(records):
    alerts = []
    prev_user, run = None, []
    for user, t, ip, status in records:
        if user != prev_user:                   # เปลี่ยนบัญชี -> ปิดชุดของคนเดิม
            check_run(prev_user, run, alerts)
            prev_user, run = user, []
        if status == "FAILED":
            run.append(t)
        else:                                   # SUCCESS -> เริ่มนับใหม่
            check_run(user, run, alerts)
            run = []
    check_run(prev_user, run, alerts)           # ชุดสุดท้ายของไฟล์
    return alerts


# ---------------------------------------------------------------
# 4) โปรแกรมหลัก
# ---------------------------------------------------------------
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "login.txt"
    records = read_log(path)
    selection_sort(records)
    alerts = scan(records)

    print(f"ตรวจ {len(records)} รายการจาก {path}")
    print(f"เปรียบเทียบคีย์ {comparisons} ครั้ง (n(n-1)/2 = {len(records)*(len(records)-1)//2})")
    print(f"พบบัญชีน่าสงสัย {len(alerts)} รายการ\n")
    print(f"{'Username':<10}{'FAILED':>8}   ช่วงเวลาที่ตรวจพบ")
    print("-" * 52)
    for user, count, start, end in alerts:
        print(f"{user:<10}{count:>8}   {start:%Y-%m-%d %H:%M:%S} - {end:%H:%M:%S}")


if __name__ == "__main__":
    main()