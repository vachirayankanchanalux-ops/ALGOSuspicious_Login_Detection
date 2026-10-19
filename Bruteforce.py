from datetime import datetime, timedelta

WINDOW = timedelta(minutes=5)
THRESHOLD = 3

def load(path):
    rows=[]
    with open(path, encoding="utf-8") as f:
        next(f)
        for i in f:
            if not i.strip():
                continue
            ts, user, ip, status = [x.strip() for x in i.split(",")]
            rows.append((datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"), user, ip, status)) 
    return rows
    
def BruteForce(rows):
    result = {}
    for t1, u, ip, status in rows:
        if status == "SUCCESS":
            continue
        window = []
        for t2, u2, ip2, status2 in rows:
            if u2==u and t1 <= t2 <= t1+WINDOW:
                window.append((t2, status2))
        window.sort()
   
        cnt, last = 0, t1
        for  t, status2 in window:
            if status2!="FAILED":
               break
            cnt, last = cnt+1, t
        
        if cnt >= THRESHOLD and cnt > result.get(u, (0,))[0]:
            result[u]=(cnt, t1, last)
    return result

if __name__ == "__main__":
    rows = load("login.txt")
    alerts = BruteForce(rows)
    print("--- Suspicious Login Alerts ---")
    for u, (cnt, start, end) in sorted(alerts.items()):
        print(f"{u:<8} FAILED {cnt} ครั้ง ช่วง {start:%H:%M:%S}-{end:%H:%M:%S}")
        
        
#output:

#--- Suspicious Login Alerts ---
#david    FAILED 3 ครั้ง ช่วง 09:10:00-09:11:00
#frank    FAILED 3 ครั้ง ช่วง 09:22:00-09:23:00
    