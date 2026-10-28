
import csv
import sys
from datetime import datetime, timedelta

WINDOW = timedelta(minutes=5)   # ไม่เกิน 5 นาที
THRESHOLD = 3                   # อย่างน้อย 3 ครั้ง


def read_log(path):
    records = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)                                    
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


def merge(B, C, A):
    """ALGORITHM Merge(B[0..p-1], C[0..q-1], A[0..p+q-1])"""
    p, q = len(B), len(C)
    i = j = k = 0
    while i < p and j < q:
        if key(B[i]) <= key(C[j]):
            A[k] = B[i]; i += 1
        else:
            A[k] = C[j]; j += 1
        k += 1
    if i == p:
        A[k:p + q] = C[j:q]                             
    else:
        A[k:p + q] = B[i:p]                            


def merge_sort(A):
    """ALGORITHM MergeSort(A[0..n-1]) (slide04 สไลด์ 14) เรียงใน A เลย"""
    n = len(A)
    if n > 1:
        B = A[0:n // 2]                                 # Divide: ครึ่งซ้าย
        C = A[n // 2:n]                                 #         ครึ่งขวา
        merge_sort(B)                                   # Conquer
        merge_sort(C)
        merge(B, C, A)                                  # Combine


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



def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "login.txt"
    records = read_log(path)
    merge_sort(records)
    alerts = scan(records)

    print(f"ตรวจ {len(records)} รายการจาก {path}")
    print(f"พบบัญชีน่าสงสัย {len(alerts)} รายการ\n")
    print(f"{'Username':<10}{'FAILED':>8}   ช่วงเวลาที่ตรวจพบ")
    print("-" * 52)
    for user, count, start, end in alerts:
        print(f"{user:<10}{count:>8}   {start:%Y-%m-%d %H:%M:%S} - {end:%H:%M:%S}")


if __name__ == "__main__":
    main()