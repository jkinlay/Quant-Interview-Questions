from pathlib import Path
import contextlib, io, json, sys, textwrap
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
Q = []
def add(num, title, difficulty, minutes, intention, buggy, fixed, expected_bad, expected_good,
        explanation, tests, tests_description, hint, followup, senior):
    Q.append(dict(number=num, title=title, difficulty=difficulty, minutes=minutes,
        intention=intention, buggy=textwrap.dedent(buggy).strip(),
        fixed=textwrap.dedent(fixed).strip(), expected_bad=expected_bad,
        expected_good=expected_good, explanation=explanation,
        tests=textwrap.dedent(tests).strip(), tests_description=tests_description,
        hint=hint, followup=followup, senior=senior))

add(1, "Adjacent changes", 1, "3 to 4",
"Return the change between each adjacent pair in a finite list of numbers, in order. An empty or one-element list returns an empty list. Do not change the input.",
'''
def changes(values):
    return [values[i] - values[i - 1]
            for i in range(len(values))]

print(changes([100, 105, 102]))
''',
'''
def changes(values):
    return [values[i] - values[i - 1]
            for i in range(1, len(values))]

print(changes([100, 105, 102]))
''', "[-2, 5, -3]", "[5, -3]",
"At i = 0, negative indexing reads the last element, creating an unintended last-to-first change. Start at index 1. A zip of values with values[1:] is also correct.",
'''
assert changes([]) == []
assert changes([7]) == []
assert changes([4, 4]) == [0]
a = [3, 1, 6]
assert changes(a) == [-2, 5] and a == [3, 1, 6]
''',
"Empty input; a singleton; constant values; negative changes; input unchanged.",
"Trace the first iteration and state what index -1 means.",
"How would you process a stream without storing all observations?",
"A senior candidate explains the boundary error, tests empty input, and can describe a one-pass iterator version. Do not demand that version in the warm-up.")

add(2, "Missing observations and valid zeroes", 1, "3 to 5",
"Calculate the arithmetic mean, excluding only None. Zero is a valid observation. Return None if there are no valid observations. Inputs contain finite numbers or None; NaN is outside this question's contract.",
'''
def mean_valid(values):
    clean = [x for x in values if x]
    return sum(clean) / len(clean) if clean else None

print(mean_valid([0.0, 2.0, None, 4.0]))
''',
'''
def mean_valid(values):
    clean = [x for x in values if x is not None]
    return sum(clean) / len(clean) if clean else None

print(mean_valid([0.0, 2.0, None, 4.0]))
''', "3.0", "2.0",
"The truth-value filter removes both None and numerical zero. An explicit identity check preserves zero. The empty-data policy is part of the specification, so returning None is intentional.",
'''
assert mean_valid([]) is None
assert mean_valid([None, None]) is None
assert mean_valid([0, 0]) == 0
assert mean_valid([-2, 0, 2]) == 0
assert mean_valid([None, 6]) == 6
''',
"All missing; empty; all zero; mixed positive and negative; one valid observation.",
"Which different input values evaluate as false?",
"If NaN becomes an accepted missing value, how would you change the contract and tests?",
"Preserves economically meaningful zeroes and distinguishes a missing observation from an observed zero. A one-pass implementation is welcome but not required.")

add(3, "Unexpected state between calls", 2, "5 to 7",
"When bucket is omitted, start a new list for that call. If the caller supplies a list, append to that same list and return it.",
'''
def record(value, bucket=[]):
    bucket.append(value)
    return bucket

a = record(10)
b = record(20)
print(a, b, a is b)
''',
'''
def record(value, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket

a = record(10)
b = record(20)
print(a, b, a is b)
''', "[10, 20] [10, 20] True", "[10] [20] False",
"The default list is created once at function definition. Both calls mutate and return the same object; a changes when the second call runs. Use None as a sentinel and create a new list inside the function. Do not use bucket or []: that would replace an explicitly supplied empty list.",
'''
a, b = record(1), record(2)
assert a == [1] and b == [2] and a is not b
provided = []
assert record(3, provided) is provided and provided == [3]
provided = [4]
assert record(5, provided) is provided and provided == [4, 5]
assert record(0) == [0]
''',
"Repeated omitted-argument calls; object identity; explicitly supplied empty and nonempty lists.",
"When is the default expression evaluated? Are a and b the same object?",
"What changes if the API must never mutate a supplied list?",
"Explains aliasing, preserves the specified ownership contract, and tests identity as well as equality.")

add(4, "A stream counted twice", 2, "5 to 7",
"Return (total, count) for a finite iterable of integers. It may be a single-use generator too large to materialise. Use one pass and constant auxiliary memory. Empty input returns (0, 0).",
'''
def summarise(values):
    total = sum(values)
    count = sum(1 for _ in values)
    return total, count

print(summarise(x for x in [2, 4, 6]))
''',
'''
def summarise(values):
    total = count = 0
    for value in values:
        total += value
        count += 1
    return total, count

print(summarise(x for x in [2, 4, 6]))
''', "(12, 0)", "(12, 3)",
"The first sum exhausts the generator. The second traversal sees no values. Accumulate total and count in one loop. list(values) fixes this fixture but violates the memory requirement; tee may buffer the stream if its branches are consumed separately.",
'''
assert summarise(iter([])) == (0, 0)
assert summarise([1, -1, 0]) == (0, 3)
assert summarise(iter([5])) == (5, 1)
class SinglePass:
    def __init__(self): self.used = False
    def __iter__(self):
        if self.used: raise AssertionError("second traversal")
        self.used = True
        yield from [3, 8]
assert summarise(SinglePass()) == (11, 2)
''',
"List and generator agree; empty and singleton streams; a source that rejects a second traversal.",
"Can this particular object be traversed a second time?",
"How would you handle malformed rows without silently losing information?",
"Distinguishes iterable from iterator, respects the memory constraint, and states O(n) time and O(1) auxiliary space.")

add(5, "Labels lost during assignment", 3, "6 to 8",
"Attach each score to the row with the matching id, preserving row order. Score labels are unique and every row id is present in scores; repeated ids in the rows are permitted.",
'''
import pandas as pd

def attach_scores(rows, scores):
    return rows.assign(score=scores.to_numpy())

rows = pd.DataFrame({"id": ["B", "A"]})
scores = pd.Series([0.1, 0.9], index=["A", "B"])
print(attach_scores(rows, scores).to_dict("records"))
''',
'''
import pandas as pd

def attach_scores(rows, scores):
    return rows.assign(score=rows["id"].map(scores))

rows = pd.DataFrame({"id": ["B", "A"]})
scores = pd.Series([0.1, 0.9], index=["A", "B"])
print(attach_scores(rows, scores).to_dict("records"))
''',
"[{'id': 'B', 'score': 0.1}, {'id': 'A', 'score': 0.9}]",
"[{'id': 'B', 'score': 0.9}, {'id': 'A', 'score': 0.1}]",
"Converting to an array discards the labels and assigns by position. Match on id using map, or use a validated join. Merely assigning the labelled Series directly also fails here because rows has an integer index rather than an id index.",
'''
before = rows.copy(deep=True)
assert attach_scores(rows, scores)["score"].tolist() == [0.9, 0.1]
other = pd.DataFrame({"id": ["A", "B", "A"]}, index=[9, 3, 7])
out = attach_scores(other, scores.iloc[::-1])
assert out["score"].tolist() == [0.1, 0.9, 0.1]
assert out.index.tolist() == [9, 3, 7]
pd.testing.assert_frame_equal(rows, before)
assert len(attach_scores(rows.iloc[:0], scores)) == 0
''',
"Shuffle score order; reorder rows; repeated row ids; nondefault row index; empty rows; input unchanged.",
"Which labels survive to_numpy, and which labels should determine the match?",
"What policy would you choose for missing scores or duplicate score labels?",
"Separates position, index, and business key. Proposes explicit duplicate and unmatched-key checks when the contract broadens.")

add(6, "A join inflates the total", 3, "8 to 10",
"Attach one category to each sale without changing the number of sales or their total quantity. The lookup may contain exact repeated rows, which may be collapsed. Conflicting categories for a sku and unmatched sale skus must raise an error. Sale rows are legitimate separate records. All keys and categories are nonmissing strings.",
'''
import pandas as pd

def enrich(sales, lookup):
    return sales.merge(lookup, on="sku")

sales = pd.DataFrame({
    "sale_id": [1, 2], "sku": ["A", "B"], "qty": [10, 20]
})
lookup = pd.DataFrame({
    "sku": ["A", "A", "B"], "category": ["X", "X", "Y"]
})
out = enrich(sales, lookup)
print(len(out), int(out["qty"].sum()))
''',
'''
import pandas as pd

def enrich(sales, lookup):
    unique = lookup.drop_duplicates()
    out = sales.merge(
        unique, on="sku", how="left",
        validate="many_to_one", indicator=True
    )
    if out["_merge"].ne("both").any():
        raise ValueError("Unmatched sku")
    return out.drop(columns="_merge")

sales = pd.DataFrame({
    "sale_id": [1, 2], "sku": ["A", "B"], "qty": [10, 20]
})
lookup = pd.DataFrame({
    "sku": ["A", "A", "B"], "category": ["X", "X", "Y"]
})
out = enrich(sales, lookup)
print(len(out), int(out["qty"].sum()))
''', "3 40", "2 30",
"The two A lookup rows each match the same sale, multiplying it. Collapse exact lookup duplicates only; a many-to-one validation then rejects conflicting mappings. A left join preserves sales and the merge indicator detects missing matches. Deduplicating the merged facts or arbitrarily keeping one category can hide a real problem.",
'''
assert enrich(sales, lookup)["qty"].sum() == sales["qty"].sum()
assert enrich(sales, lookup)["sale_id"].tolist() == [1, 2]
repeated = pd.concat([sales, sales.iloc[[0]]], ignore_index=True)
assert len(enrich(repeated, lookup)) == 3
for bad in [
    pd.DataFrame({"sku": ["A", "A", "B"],
                  "category": ["X", "Z", "Y"]}),
    lookup[lookup["sku"].eq("A")]
]:
    try:
        enrich(sales, bad)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid lookup accepted")
assert len(enrich(sales.iloc[:0], lookup)) == 0
''',
"Row count and total conserved; legitimate repeated sales retained; conflicting lookup rejected; unmatched sku rejected; empty sales accepted.",
"How many output rows can one A sale produce?",
"What checks would you put before and after a production join?",
"Reasons about table grain and join cardinality, does not delete valid facts, and makes invalid states visible.")

add(7, "A square array hides a shape error", 3, "7 to 10",
"For a 2D array x with one observation per row and one variable per column, compute the weighted sum of variables for each row. w is a column vector of shape (number of variables, 1). Reject incompatible shapes. Inputs are finite real numbers.",
'''
import numpy as np

def weighted_rows(x, w):
    return (x * w).sum(axis=1)

x = np.array([[1., 2.], [3., 4.]])
w = np.array([[0.25], [0.75]])
print(weighted_rows(x, w).tolist())
''',
'''
import numpy as np

def weighted_rows(x, w):
    x, w = np.asarray(x), np.asarray(w)
    if x.ndim != 2 or w.shape != (x.shape[1], 1):
        raise ValueError("Incompatible shapes")
    return x @ w[:, 0]

x = np.array([[1., 2.], [3., 4.]])
w = np.array([[0.25], [0.75]])
print(weighted_rows(x, w).tolist())
''', "[0.75, 5.25]", "[1.75, 3.75]",
"With these square inputs, broadcasting applies the weights down the rows rather than across the variables. The valid shape masks the wrong calculation. A matrix-vector product expresses the intended reduction. (x * w.T).sum(axis=1) also works under the stated shape contract.",
'''
np.testing.assert_allclose(weighted_rows(x, w), [1.75, 3.75])
z = np.array([[1., 2.], [3., 4.], [5., 6.]])
np.testing.assert_allclose(weighted_rows(z, w), [1.75, 3.75, 5.75])
np.testing.assert_allclose(weighted_rows(z, np.array([[1.], [0.]])),
                           z[:, 0])
assert weighted_rows(np.empty((0, 2)), w).shape == (0,)
try:
    weighted_rows(z, np.ones((3, 1)))
except ValueError:
    pass
else:
    raise AssertionError("Bad shape accepted")
''',
"Non-square inputs; single active variable; output shape; no rows; incompatible weights.",
"Write the shapes next to the multiplication. Which axis does each weight vary along?",
"What could go wrong if you simply flatten every incoming array?",
"Explains broadcasting using dimensions and deliberately tests a non-square case. Flattening is acceptable only when justified by the input contract.")

add(8, "A rolling feature crosses an entity boundary", 4, "10 to 12",
"For each entity and day, return the mean of that entity's previous two observations, excluding the current observation. Return missing until two previous observations exist. Sort the output by entity and day. Keys are unique; each entity is observed daily without gaps in this fixture.",
'''
import pandas as pd

def prior_means(df):
    out = df.sort_values(["entity", "day"]).copy()
    out["prior_mean"] = (
        out.groupby("entity")["qty"]
        .transform(lambda s: s.rolling(2, min_periods=2).mean())
        .shift(1)
    )
    return out

df = pd.DataFrame({
    "entity": ["B", "A", "A", "B", "A", "B"],
    "day": [2, 3, 1, 1, 2, 3],
    "qty": [200, 30, 10, 100, 20, 300]
})
out = prior_means(df)
print(out[["entity", "day", "prior_mean"]]
      .to_csv(index=False, na_rep="NA"), end="")
''',
'''
import pandas as pd

def prior_means(df):
    out = df.sort_values(["entity", "day"]).copy()
    out["prior_mean"] = (
        out.groupby("entity")["qty"]
        .transform(
            lambda s: s.shift(1).rolling(2, min_periods=2).mean()
        )
    )
    return out

df = pd.DataFrame({
    "entity": ["B", "A", "A", "B", "A", "B"],
    "day": [2, 3, 1, 1, 2, 3],
    "qty": [200, 30, 10, 100, 20, 300]
})
out = prior_means(df)
print(out[["entity", "day", "prior_mean"]]
      .to_csv(index=False, na_rep="NA"), end="")
''',
"entity,day,prior_mean\nA,1,NA\nA,2,NA\nA,3,15.0\nB,1,25.0\nB,2,NA\nB,3,150.0",
"entity,day,prior_mean\nA,1,NA\nA,2,NA\nA,3,15.0\nB,1,NA\nB,2,NA\nB,3,150.0",
"The rolling calculation is grouped, but the final shift acts on the entire concatenated Series. It moves A's final value into B's first row. Put the shift inside each group. A global shift before grouping can create a similar boundary problem.",
'''
import numpy as np
out = prior_means(df)
np.testing.assert_allclose(out["prior_mean"],
    [np.nan, np.nan, 15, np.nan, np.nan, 150], equal_nan=True)
pd.testing.assert_frame_equal(
    out, prior_means(df.sample(frac=1, random_state=2))
)
changed = df.copy()
changed.loc[(changed.entity == "A") & (changed.day == 3), "qty"] = 9999
assert prior_means(changed).query("entity == 'A' and day == 3")[
    "prior_mean"].iloc[0] == 15
assert prior_means(df[df.entity == "B"])["prior_mean"].isna().sum() == 2
assert prior_means(df.iloc[:0]).empty
''',
"First two rows of every entity missing; shuffled input invariant; changing the current observation does not change its feature; groups independent; empty input.",
"Is the final shift still inside a group operation?",
"How does 'two observations' differ from 'two calendar days' if dates are missing?",
"Tests the information boundary and group independence, not just the displayed middle rows. Identifies how missing dates would change the specification.")

add(9, "Variance disappears through cancellation", 4, "10 to 15",
"Compute population variance (divide by n) for a finite, possibly single-use iterable of finite floats. Use one pass and constant auxiliary memory. Empty input raises ValueError; a singleton has variance zero. The fixture has a large level and small spread.",
'''
def population_variance(values):
    n = 0
    total = total_sq = 0.0
    for x in values:
        n += 1
        total += x
        total_sq += x * x
    if n == 0:
        raise ValueError("Empty input")
    return total_sq / n - (total / n) ** 2

values = [1e9 + 1, 1e9 + 2, 1e9 + 3]
print(f"{population_variance(iter(values)):.6f}")
''',
'''
def population_variance(values):
    n = 0
    mean = m2 = 0.0
    for x in values:
        n += 1
        delta = x - mean
        mean += delta / n
        m2 += delta * (x - mean)
    if n == 0:
        raise ValueError("Empty input")
    return m2 / n

values = [1e9 + 1, 1e9 + 2, 1e9 + 3]
print(f"{population_variance(iter(values)):.6f}")
''', "0.000000", "0.666667",
"The two terms in E[x squared] minus E[x] squared are large and nearly equal. Floating-point rounding destroys the small difference. The repair uses an online mean and a sum of squared deviations (Welford's recurrence). Clipping a negative result to zero would not recover lost accuracy. This method improves stability; it does not make floating-point arithmetic exact.",
'''
import math, statistics
for vals in ([1., 2., 3.], [1e9+1, 1e9+2, 1e9+3],
             [-4., 0., 8.], [7.], [7., 7., 7.]):
    assert math.isclose(population_variance(iter(vals)),
                        statistics.pvariance(vals),
                        rel_tol=1e-12, abs_tol=1e-12)
try:
    population_variance(iter([]))
except ValueError:
    pass
else:
    raise AssertionError("Empty input accepted")
''',
"Compare with an independent reference; translate small data by a large constant; constant values; singleton; empty; one-use iterator.",
"The mathematical identity is correct. What happens when two rounded numbers near 10^18 are subtracted?",
"Explain the update for m2, or propose a centred two-pass calculation and explain why it misses the streaming requirement.",
"Recognises numerical cancellation. Full repair credit requires meeting the one-pass contract; an accurate two-pass proposal earns partial credit. Do not make recall of the algorithm's name a requirement.")

add(10, "Historical records that were not yet available", 5, "15 to 20",
"Attach a price to each decision, preserving decision order. Times are integer minutes from a common origin. For the same symbol, eligible quotes have event_min <= decision_min, available_min <= decision_min, and event age at most 5 minutes inclusive. Choose the greatest event_min, then the greatest available_min for revisions of that event. A late older event must not replace a newer event. Return missing if none qualifies. Decision ids are unique. Quote (symbol, event_min, available_min) keys are unique. Inputs contain no missing fields and available_min >= event_min. A clear reference implementation is sufficient; discuss scaling separately.",
'''
import pandas as pd

def attach_prices(decisions, quotes):
    out = pd.merge_asof(
        decisions.sort_values("decision_min"),
        quotes.sort_values("event_min", kind="stable"),
        by="symbol",
        left_on="decision_min", right_on="event_min",
        direction="backward", tolerance=5
    )
    return out.set_index("id").reindex(decisions["id"])

decisions = pd.DataFrame({
    "id": [0, 1, 2, 3, 4, 5],
    "symbol": ["A", "B", "A", "A", "C", "A"],
    "decision_min": [3, 3, 1, 7, 3, 8]
})
quotes = pd.DataFrame({
    "symbol": ["A", "A", "B", "A", "B", "A", "A"],
    "event_min": [0, 1, 1, 2, 2, 2, -1],
    "available_min": [0, 1, 2, 4, 5, 6, 7],
    "price": [100., 101., 200., 102., 202., 103., 99.]
})
out = attach_prices(decisions, quotes)
print([None if pd.isna(v) else float(v) for v in out["price"]])
''',
'''
import pandas as pd

def attach_prices(decisions, quotes):
    prices = []
    for d in decisions.itertuples(index=False):
        eligible = quotes.loc[
            quotes["symbol"].eq(d.symbol)
            & quotes["available_min"].le(d.decision_min)
            & quotes["event_min"].between(
                d.decision_min - 5, d.decision_min
            )
        ]
        if eligible.empty:
            prices.append(float("nan"))
        else:
            latest = eligible.sort_values(
                ["event_min", "available_min"]
            ).iloc[-1]
            prices.append(float(latest["price"]))
    return decisions.assign(price=prices).set_index("id")

decisions = pd.DataFrame({
    "id": [0, 1, 2, 3, 4, 5],
    "symbol": ["A", "B", "A", "A", "C", "A"],
    "decision_min": [3, 3, 1, 7, 3, 8]
})
quotes = pd.DataFrame({
    "symbol": ["A", "A", "B", "A", "B", "A", "A"],
    "event_min": [0, 1, 1, 2, 2, 2, -1],
    "available_min": [0, 1, 2, 4, 5, 6, 7],
    "price": [100., 101., 200., 102., 202., 103., 99.]
})
out = attach_prices(decisions, quotes)
print([None if pd.isna(v) else float(v) for v in out["price"]])
''',
"[103.0, 202.0, 101.0, 103.0, None, None]",
"[101.0, 200.0, 101.0, 103.0, None, None]",
"The event-time join uses records and revisions that arrived after the decision. Sorting by event time cannot enforce availability. Joining only on availability is also insufficient: the old event arriving at minute 7 must not override event 2. Filter both clocks, then rank by event and revision availability. The fixture's corrections are material: at minute 3, A's price is 101 and B's is 200. This reference is intentionally small-data code.",
'''
import numpy as np
expected = [101., 200., 101., 103., np.nan, np.nan]
np.testing.assert_allclose(attach_prices(decisions, quotes)["price"],
                           expected, equal_nan=True)
np.testing.assert_allclose(
    attach_prices(decisions, quotes.sample(frac=1, random_state=7))["price"],
    expected, equal_nan=True
)
without_future = quotes[quotes.available_min <= 3]
early = decisions[decisions.decision_min <= 3]
np.testing.assert_allclose(attach_prices(early, quotes)["price"],
    attach_prices(early, without_future)["price"], equal_nan=True)
probe = pd.DataFrame({"id": [10, 11], "symbol": ["A", "A"],
                      "decision_min": [4, 6]})
assert attach_prices(probe, quotes)["price"].tolist() == [102., 103.]
assert attach_prices(decisions.iloc[:0], quotes).empty
assert attach_prices(decisions, quotes.iloc[:0])["price"].isna().all()
''',
"Future arrivals cannot change earlier answers; revision before and after release; shuffled quotes invariant; exact boundary ages; late older record; missing symbol; stale quote; empty inputs.",
"Which timestamp says when a record describes the world, and which says when it became usable?",
"How would you implement this for millions of decisions without scanning all quotes for each decision?",
"Handles both time axes and revisions, preserves identity and order, and recognises reference-code cost. A possible scale-up is a sweep in availability order, maintaining each symbol's newest eligible event and revision; explain expiry and tie rules. Under available_min >= event_min, the newest event also determines whether any quote passes the age limit.")

def execute(code):
    ns = {}
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        exec(compile(code, "<interview-question>", "exec"), ns)
    return capture.getvalue().replace("\r\n", "\n").rstrip(), ns

def validate():
    report = []
    for q in Q:
        bad, _ = execute(q["buggy"])
        good, ns = execute(q["fixed"])
        assert bad == q["expected_bad"], (q["number"], "buggy", bad)
        assert good == q["expected_good"], (q["number"], "fixed", good)
        exec(compile(q["tests"], "<regression-tests>", "exec"), ns)
        q["observed_bad"], q["observed_good"] = bad, good
        report.append(f'Q{q["number"]:02d}: faulty output, repaired output and regression checks PASS')
    return report

if __name__ == "__main__":
    report = validate()
    (ROOT / "question_bank.json").write_text(
        json.dumps(Q, indent=2), encoding="utf-8")
    (ROOT / "verification.txt").write_text(
        f"Python {sys.version.split()[0]}; pandas {pd.__version__}; NumPy {np.__version__}\n"
        + "\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
