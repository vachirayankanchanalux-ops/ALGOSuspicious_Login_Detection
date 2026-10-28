import csv
import sys
from collections import deque
from datetime import datetime, timedelta
 
WINDOW = timedelta(minutes=5)
THRESHOLD = 3
 
 
# ---------------------------------------------------------------
# 1) อ่านไฟล์
# ---------------------------------------------------------------
 
def read_log(path):
    records = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
 
        for index, row in enumerate(reader):
            if not row:
                continue
 
            ts, user, ip, status = [c.strip() for c in row]
            t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
 
            records.append((user, t, ip, status, index))
 
    return records
 
 
def key(r):
    return (r[0], r[1], r[4])
 
 
# ---------------------------------------------------------------
# 2) Merge Sort
# ---------------------------------------------------------------
 
def merge(B, C, A):
    p, q = len(B), len(C)
 
    i = j = k = 0
 
    while i < p and j < q:
 
        if key(B[i]) <= key(C[j]):
            A[k] = B[i]
            i += 1
 
        else:
            A[k] = C[j]
            j += 1
 
        k += 1
 
    if i == p:
        A[k:p + q] = C[j:q]
 
    else:
        A[k:p + q] = B[i:p]
 
 
def merge_sort(A):
    n = len(A)
 
    if n > 1:
        B = A[0:n // 2]
        C = A[n // 2:n]
 
        merge_sort(B)
        merge_sort(C)
 
        merge(B, C, A)
 
 
# ---------------------------------------------------------------
# 3) Sliding Window Detection
# ---------------------------------------------------------------
 
def sliding_window(records):
    alerts = []
 
    windows = {}
    best = {}
 
    for user, t, ip, status, index in records:
 
        q = windows.setdefault(user, deque())
 
        # เมื่อ SUCCESS ให้จบชุด FAILED เดิม
        if status == "SUCCESS":
 
            if user in best:
                count, start, end = best[user]
 
                alerts.append((user, count, start, end))
                del best[user]
 
            q.clear()
            continue
 
        # เพิ่ม FAILED ใหม่เข้า Queue
        if status == "FAILED":
            q.append(t)
 
            # ลบเหตุการณ์ที่เกิน 5 นาที
            while q and t - q[0] > WINDOW:
                q.popleft()
 
            count = len(q)
 
            # เก็บช่วงที่มี FAILED มากที่สุด
            if count >= THRESHOLD:
 
                if user not in best or count > best[user][0]:
                    best[user] = (count, q[0], q[-1])
 
    # ตรวจสอบชุด FAILED ที่ยังไม่จบด้วย SUCCESS
    for user, (count, start, end) in best.items():
        alerts.append((user, count, start, end))
 
    return alerts
 
 
# ---------------------------------------------------------------
# 4) โปรแกรมหลัก
# ---------------------------------------------------------------
 
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "login.txt"
 
    records = read_log(path)
 
    merge_sort(records)
 
    alerts = sliding_window(records)
 
    print(f"ตรวจ {len(records)} รายการจาก {path}")
    print(f"พบการแจ้งเตือน {len(alerts)} รายการ\n")
 
    print(f"{'Username':<10}{'FAILED':>8}   ช่วงเวลาที่ตรวจพบ")
    print("-" * 65)
 
    for user, count, start, end in alerts:
        print(
            f"{user:<10}{count:>8}   "
            f"{start:%Y-%m-%d %H:%M:%S} - {end:%H:%M:%S}"
        )
 
 
if __name__ == "__main__":
    main()