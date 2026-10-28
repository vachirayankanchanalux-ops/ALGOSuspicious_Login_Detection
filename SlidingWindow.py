import csv
import sys
from collections import deque
from datetime import datetime, timedelta

WINDOW = timedelta(minutes=5)
THRESHOLD = 3


def read_log(path):
    records = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            ts, user, ip, status = [c.strip() for c in row]
            records.append((user, datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"), ip, status))
    return records


def merge(B, C, A):
    p, q = len(B), len(C)
    i = j = k = 0
    while i < p and j < q:
        if B[i][1] <= C[j][1]:                  # เทียบเวลา
            A[k] = B[i]; i += 1
        else:
            A[k] = C[j]; j += 1
        k += 1
    if i == p:
        A[k:p + q] = C[j:q]
    else:
        A[k:p + q] = B[i:p]


def merge_sort(A):
    n = len(A)
    if n > 1:
        B, C = A[0:n // 2], A[n // 2:n]
        merge_sort(B)
        merge_sort(C)
        merge(B, C, A)


def sliding_window(records):
    alerts = []
    windows = {}                                
    for user, t, ip, status in records:         
        q = windows.setdefault(user, deque())   
        if status == "SUCCESS":
            q.clear()                           
            continue
        q.append(t)                             
        while t - q[0] > WINDOW:                
            q.popleft()
        if len(q) == THRESHOLD:                 
            alerts.append((user, len(q), q[0], q[-1]))
            q.clear()                           
    return alerts


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "login.txt"
    records = read_log(path)
    merge_sort(records)
    alerts = sliding_window(records)
    print(f"ตรวจ {len(records)} รายการจาก {path}")
    print(f"พบบัญชีน่าสงสัย {len(alerts)} รายการ\n")
    print(f"{'Username':<10}{'FAILED':>8}   ช่วงเวลาที่ตรวจพบ")
    print("-" * 52)
    for user, count, start, end in alerts:
        print(f"{user:<10}{count:>8}   {start:%Y-%m-%d %H:%M:%S} - {end:%H:%M:%S}")


if __name__ == "__main__":
    main()