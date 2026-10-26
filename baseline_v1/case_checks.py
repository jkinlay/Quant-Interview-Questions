"""Reference implementations and tests for the interview cases.
Run without arguments for fixtures, or pass --source-dir for the supplied CSVs.
"""

import pandas as pd

def monthly_rs(bullets):
    # Contract: the owner has confirmed all RS rows are additive.
    rs = bullets.loc[bullets["Channel"].eq("RS")].copy()
    if rs["Bullets"].isna().any():
        raise ValueError("Missing bullet label")
    rs["Date"] = pd.to_datetime(
        rs["Date"], format="%Y-%m-%d", errors="raise"
    )
    rs["Month"] = rs["Date"].dt.to_period("M").dt.to_timestamp()
    return (
        rs.groupby(["Month", "Bullets"], as_index=False)["Quantity"]
        .sum(min_count=1)
        .sort_values(["Month", "Bullets"])
        .reset_index(drop=True)
    )

def net_quantities(events):
    seen = {}
    totals = {}
    for event in events:
        eid = event["event_id"]
        payload = (event["sku"], event["delta"])
        if eid in seen:
            if seen[eid] != payload:
                raise ValueError("Conflicting event payload")
            continue
        seen[eid] = payload
        sku, delta = payload
        totals[sku] = totals.get(sku, 0) + delta
    return totals

from collections import deque

class RollingMean:
    def __init__(self):
        self.windows = {}
        self.totals = {}

    def update(self, entity, value):
        window = self.windows.setdefault(entity, deque())
        total = self.totals.get(entity, 0)
        if len(window) == 3:
            total -= window.popleft()
        window.append(value)
        total += value
        self.totals[entity] = total
        return total / 3 if len(window) == 3 else None

def slow_features(rows):
    result = []
    for row in rows:
        history = [
            r["value"] for r in rows
            if r["entity"] == row["entity"]
            and row["minute"] - 3 <= r["minute"] < row["minute"]
        ]
        result.append(
            sum(history) / len(history)
            if len(history) >= 2 else None
        )
    return result

from collections import deque

def fast_features(rows):
    ordered = sorted(
        enumerate(rows),
        key=lambda pair: (pair[1]["entity"], pair[1]["minute"])
    )
    result = [None] * len(rows)
    active_entity = None
    window = deque()
    total = 0
    for original_pos, row in ordered:
        if row["entity"] != active_entity:
            active_entity = row["entity"]
            window.clear()
            total = 0
        cutoff = row["minute"] - 3
        while window and window[0][0] < cutoff:
            _, old = window.popleft()
            total -= old
        if len(window) >= 2:
            result[original_pos] = total / len(window)
        window.append((row["minute"], row["value"]))
        total += row["value"]
    return result

def verify_cases(source_dir=None):
    import math, random
    import numpy as np
    import pandas as pd
    from pathlib import Path

    events = [
        {"event_id": e, "sku": s, "delta": d}
        for e, s, d in [
            ("e1","X",10), ("e2","X",-3), ("e1","X",10),
            ("e3","Y",5), ("e4","X",-7), ("e5","Y",-2)
        ]
    ]
    assert net_quantities(events) == {"X": 0, "Y": 3}
    assert net_quantities(events + events) == {"X": 0, "Y": 3}
    assert net_quantities([]) == {}
    for payload in [dict(event_id="e1",sku="Y",delta=10),
                    dict(event_id="e1",sku="X",delta=11)]:
        try:
            net_quantities(events + [payload])
        except ValueError:
            pass
        else:
            raise AssertionError("Conflicting event accepted")
    print("Alternative A: fixture, replay, empty and conflicts PASS")

    updates = [("A",10),("B",100),("A",20),("A",30),
               ("B",200),("A",40),("B",300)]
    service=RollingMean()
    assert [service.update(k,v) for k,v in updates] == [
        None,None,None,20.,None,30.,200.]
    separate=RollingMean()
    assert separate.update("A",0) is None
    assert separate.update("A",0) is None
    assert separate.update("A",0) == 0
    assert separate.update("A",-3) == -1
    assert len(service.windows["A"]) == 3
    print("Alternative B: interleaving, warm-up, eviction and separate state PASS")

    rows = [dict(entity=e,minute=m,value=v) for e,m,v in [
        ("A",1,10),("A",2,20),("B",1,100),
        ("A",4,40),("A",5,50),("B",4,400)]]
    expected=[None,None,None,15.,30.,None]
    assert slow_features(rows) == expected
    assert fast_features(rows) == expected
    assert fast_features([]) == []
    rng=random.Random(19)
    for _ in range(100):
        trial=[]
        for entity in ("A","B","C"):
            for minute in rng.sample(range(30),rng.randint(0,16)):
                trial.append(dict(entity=entity,minute=minute,
                                  value=rng.randint(-20,20)))
        rng.shuffle(trial)
        assert fast_features(trial) == slow_features(trial)
    print("Alternative C: fixture, empty and 100 random oracle comparisons PASS")

    fixture=pd.DataFrame({
        "Date":["2024-01-31","2024-01-31","2024-02-01",
                "2024-02-03","2024-04-01"],
        "Bullets":["A","A","A","B","A"],
        "Channel":["RS","TF","RS","RS","RS"],
        "Quantity":[2,100,3,0,4]
    })
    before=fixture.copy(deep=True)
    monthly=monthly_rs(fixture)
    assert monthly.Quantity.tolist() == [2,3,0,4]
    assert monthly.Month.dt.strftime("%Y-%m").tolist() == [
        "2024-01","2024-02","2024-02","2024-04"]
    assert monthly.Quantity.sum() == fixture.loc[
        fixture.Channel.eq("RS"),"Quantity"].sum()
    pd.testing.assert_frame_equal(fixture,before)
    pd.testing.assert_frame_equal(
        monthly,monthly_rs(fixture.sample(frac=1,random_state=2)))
    assert monthly_rs(fixture.iloc[:0]).empty
    print("Adapted case: channel, month boundary, zero, gap and nonmutation PASS")

    if source_dir is not None:
        source_dir=Path(source_dir)
        b=pd.read_csv(source_dir/"bullets_sales.csv")
        h=pd.read_csv(source_dir/"handgun_sales.csv")
        assert b.shape == (30684,6) and h.shape == (15342,4)
        rs=b[b.Channel.eq("RS")]
        tf=b[b.Channel.eq("TF")]
        assert len(rs) == len(tf) == 15342
        assert rs[["Maker","Model"]].isna().all().all()
        assert tf[["Maker","Model"]].notna().all().all()
        assert rs.duplicated().sum() == 14
        assert rs.groupby(["Date","Bullets"]).size().groupby(
            "Bullets").unique().map(list).to_dict() == {
                "bullets_A":[3],"bullets_B":[2],"bullets_C":[1]}
        mapping=tf[["Maker","Model","Bullets"]].drop_duplicates()
        assert mapping.groupby("Bullets").size().to_dict() == {
            "bullets_A":3,"bullets_B":2,"bullets_C":1}
        for frame in [b,h]:
            assert frame.Date.min()=="1810-01-01"
            assert frame.Date.max()=="1816-12-31"
            assert frame.Date.nunique()==2557
            assert not frame.Quantity.lt(0).any()
        assert not h.duplicated(["Date","Maker","Model"]).any()
        result=monthly_rs(b)
        assert len(result)==252 and result.Month.nunique()==84
        assert result.Quantity.sum()==rs.Quantity.sum()
        assert not result.duplicated(["Month","Bullets"]).any()
        print("Supplied sources: profile and pooled aggregation assertions PASS")

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir")
    args=parser.parse_args()
    verify_cases(args.source_dir)
