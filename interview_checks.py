"""Advanced senior quant interview bank, runnable references and regressions."""
from pathlib import Path
import contextlib, io, json, sys, textwrap
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parent
Q = []
def add(number, title, level, minutes, track, intention, setup, bad, good, demo,
        explanation, tests, criteria, hint, extension):
    clean = lambda s: textwrap.dedent(s).strip()
    setup, bad, good, demo = map(clean, (setup,bad,good,demo))
    Q.append(dict(number=number,title=title,level=level,minutes=minutes,track=track,
        intention=intention,buggy="\n\n".join([setup,bad,demo]),
        fixed="\n\n".join([setup,good,demo]),explanation=explanation,
        tests=clean(tests),criteria=criteria,hint=hint,extension=extension))

add(1,"Weighted regularisation and a nearly singular design","Senior baseline", "15 to 20","Numerical",
"Minimise sum_i w_i (y_i - X_i beta)^2 + lam * sum_{j>=1} beta_j^2. The first column of X is the intercept and must not be penalised. Nonnegative finite weights are precisions; lam >= 0. Inputs are finite real arrays with compatible shapes. If lam is zero and the design is rank deficient, return the minimum Euclidean norm minimiser. Explain the numerical implications as well as repairing the fixture.",
'''
import numpy as np
X = np.array([[1., 0.], [1., 1.], [1., 2.]])
y = np.array([1., 2., 2.])
w = np.array([1., 4., 1.])
''',
'''
def fit(X, y, w, lam):
    A = X * w[:, None]
    b = y * w
    return np.linalg.solve(
        A.T @ A + lam * np.eye(X.shape[1]), A.T @ b
    )
''',
'''
def fit(X, y, w, lam):
    X, y, w = map(lambda a: np.asarray(a, dtype=float), (X,y,w))
    if lam < 0 or np.any(w < 0):
        raise ValueError("Negative weight or penalty")
    penalty = np.eye(X.shape[1])
    penalty[0, 0] = 0
    A = np.vstack([
        X * np.sqrt(w)[:, None], np.sqrt(lam) * penalty
    ])
    b = np.concatenate([y * np.sqrt(w), np.zeros(X.shape[1])])
    return np.linalg.lstsq(A, b, rcond=None)[0]
''',
'''print(np.round(fit(X, y, w, 1.), 6).tolist())''',
"The implementation squares the precision weights, penalises the intercept, and forms normal equations. The first two change the objective; the third squares the design condition number in the full-rank case and does not implement the required singular-case solution. Use square-root weights and augment the design with the penalty rows, then solve the least-squares problem directly. The singular-value cutoff is a numerical rank policy, not a claim that every mathematically nonzero singular value should be inverted.",
'''
np.testing.assert_allclose(fit(X,y,w,1), [1.5,1/3], atol=1e-12)
beta=fit(X,y,w,1)
gradient=X.T@(w*(X@beta-y))+np.diag([0.,1.])@beta
np.testing.assert_allclose(gradient,0,atol=1e-12)
np.testing.assert_allclose(fit(np.ones((2,1)),[0,10],[1,9],100),[9])
R=np.column_stack([np.ones(4),np.arange(4),np.arange(4)])
np.testing.assert_allclose(fit(R,1+2*np.arange(4),np.ones(4),0),
                           [1,1,1],atol=1e-12)
np.testing.assert_allclose(fit(X,y,w*10,10),fit(X,y,w,1))
np.testing.assert_allclose(fit(X,y,np.zeros(3),0),[0,0])
t=np.arange(-2,3)*1e-8
ill=np.column_stack([np.ones(5),1+t])
np.testing.assert_allclose(fit(ill,ill@np.array([1.,2.]),np.ones(5),0),
                           [1,2],atol=1e-7)
''',
"Finds all three defects; derives the augmented system; distinguishes objective error from conditioning; tests first-order optimality, rank deficiency and joint rescaling of weights and penalty.",
"Write the objective actually solved by the existing A and b.",
"Supply two almost collinear columns. Ask which residuals, singular values and coefficient sensitivities to inspect, and how feature scaling interacts with the stated penalty.")

add(2,"Nearest neighbours with large offsets and limited memory","Strong senior","15 to 25","Numerical and performance",
"Return each row's nearest OTHER row in Euclidean distance, breaking ties by the smallest original row index. x is a finite float64 matrix with at least two rows; squared coordinate differences fit float64. Coordinates can have a large common offset. Preserve x. The production input does not fit an n by n distance matrix in memory. Provide a correct bounded-block implementation and explain its time and memory costs.",
'''
import numpy as np
x = np.array([[1e9,1e9], [1e9+1,1e9],
              [1e9+3,1e9], [1e9+8,1e9]])
''',
'''
def nearest(x, block=2):
    norms = np.einsum("ij,ij->i", x, x)
    d2 = norms[:,None] + norms[None,:] - 2 * (x @ x.T)
    d2 = np.maximum(d2, 0)
    np.fill_diagonal(d2, np.inf)
    return d2.argmin(axis=1)
''',
'''
def nearest(x, block=2):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2 or block < 1:
        raise ValueError("Invalid size")
    result = np.empty(n, dtype=int)
    for start in range(0, n, block):
        stop = min(start + block, n)
        delta = x[start:stop,None,:] - x[None,:,:]
        d2 = np.einsum("ijk,ijk->ij", delta, delta)
        d2[np.arange(stop-start), np.arange(start,stop)] = np.inf
        result[start:stop] = d2.argmin(axis=1)
    return result
''',
'''print(nearest(x).tolist())''',
"The norm identity subtracts nearly equal numbers near 10^18, losing the small squared distances. Clipping negative distances cannot reconstruct them. The code also allocates a dense quadratic matrix and ignores block. Direct coordinate differences preserve the represented offsets in this fixture. Block the queries, mask self using GLOBAL indices, and retain original column order for deterministic ties. This exact brute-force reference costs O(n^2 d) time and O(B n d + n d) storage with fixed block size B, not O(n^2) storage.",
'''
np.testing.assert_array_equal(nearest(x),[1,0,1,2])
for b in [1,2,3]:
    np.testing.assert_array_equal(nearest(x,b),[1,0,1,2])
np.testing.assert_array_equal(nearest(x-x[0],1),nearest(x,1))
ties=np.array([[0.,0.],[0.,0.],[1.,0.]])
np.testing.assert_array_equal(nearest(ties,1),[1,0,0])
before=x.copy()
nearest(x)
np.testing.assert_array_equal(x,before)
rng=np.random.default_rng(7)
for n in [2,7,13]:
    a=rng.normal(size=(n,3))
    oracle=np.sum((a[:,None,:]-a[None,:,:])**2,axis=2)
    np.fill_diagonal(oracle,np.inf)
    np.testing.assert_array_equal(nearest(a,3),oracle.argmin(axis=1))
''',
"Explains cancellation rather than just clipping; removes the dense allocation; handles the block diagonal and ties; checks translation invariance and a direct small-data oracle.",
"Compare the size of the true distance with the terms being subtracted.",
"Discuss reference-side blocking when even B*n*d is too large, running minima with deterministic ties, and when a tree or approximate search changes the performance or accuracy contract.")

add(3,"Interval exclusion with nesting and endpoint rules","Strong senior","15 to 25","Algorithms",
"keep_intervals returns True exactly when a query interval overlaps no blocked interval. All intervals are nonempty half-open [start,end), with finite numeric endpoints and start < end. Inputs can be unsorted, nested or duplicated. Touching endpoints do not overlap. Preserve query order. Avoid an n by m overlap matrix; target O(m log m + n log m) time and O(m+n) auxiliary space.",
'''
import numpy as np
queries = np.array([[50,51],[100,101],[10,11],[11,12]])
blocked = np.array([[0,100],[10,11]])
''',
'''
def keep_intervals(queries, blocked):
    if len(blocked) == 0:
        return np.ones(len(queries), dtype=bool)
    b = blocked[np.argsort(blocked[:,0])]
    j = np.searchsorted(b[:,0], queries[:,1], side="right") - 1
    overlaps = (j >= 0) & (b[np.maximum(j,0),1] >= queries[:,0])
    return ~overlaps
''',
'''
def keep_intervals(queries, blocked):
    if len(blocked) == 0:
        return np.ones(len(queries), dtype=bool)
    b = blocked[np.argsort(blocked[:,0])]
    furthest_end = np.maximum.accumulate(b[:,1])
    j = np.searchsorted(b[:,0], queries[:,1], side="left") - 1
    overlaps = np.zeros(len(queries), dtype=bool)
    valid = j >= 0
    overlaps[valid] = furthest_end[j[valid]] > queries[valid,0]
    return ~overlaps
''',
'''print(keep_intervals(queries, blocked).tolist())''',
"Looking only at the blocked interval with the greatest start misses an earlier long interval containing it. Among starts strictly before query.end, overlap exists if the maximum end is strictly after query.start. A prefix maximum captures that condition. side='left' and a strict end comparison implement half-open boundaries; the original code incorrectly counts some touching intervals.",
'''
np.testing.assert_array_equal(keep_intervals(queries,blocked),
                              [False,True,False,False])
np.testing.assert_array_equal(
    keep_intervals(np.array([[0,1],[2,3]]),np.array([[1,2]])),
    [True,True])
rng=np.random.default_rng(23)
for _ in range(100):
    q0=rng.integers(-10,30,size=20)
    b0=rng.integers(-10,30,size=15)
    q=np.column_stack([q0,q0+rng.integers(1,20,size=20)])
    b=np.column_stack([b0,b0+rng.integers(1,20,size=15)])
    oracle=~((q[:,None,0]<b[None,:,1]) &
             (b[None,:,0]<q[:,None,1])).any(axis=1)
    np.testing.assert_array_equal(keep_intervals(q,b),oracle)
assert keep_intervals(np.empty((0,2)),blocked).size==0
assert keep_intervals(queries,np.empty((0,2))).all()
''',
"Finds the nesting failure and both endpoint errors; derives the prefix maximum rather than presenting an unexplained searchsorted trick; checks against brute force on random nested inputs.",
"Can the interval with the latest start also have a much earlier end?",
"Require the id of a conflicting blocked interval, then multiple independent groups. Ask how the state and proof change. Event-label overlap and embargo rules can be a round-two application.")

add(4,"A numerical cache that changes the result","Strong senior","15 to 25","Python ownership and caching",
"gram(x, scale) must return scale * x.T @ x as a fresh mutable float64 array, for a finite real 2D input and finite scalar scale. Results must depend on values, shape and scale. Callers may mutate inputs between calls and mutate returned arrays. No caller mutates an input concurrently with the snapshot operation. Cache at most 128 entries. Discuss why a content-key cache may still be a poor performance choice.",
'''
import numpy as np
from functools import lru_cache
x = np.array([[1.,2.],[3.,4.]])
''',
'''
_cache = {}
def gram(x, scale):
    key = x.tobytes()
    if key not in _cache:
        _cache[key] = scale * (x.T @ x)
    return _cache[key]
''',
'''
@lru_cache(maxsize=128)
def _compute(shape, contents, scale):
    snapshot = np.frombuffer(contents, dtype=np.float64).reshape(shape)
    value = scale * (snapshot.T @ snapshot)
    value.setflags(write=False)
    return value

def gram(x, scale):
    snapshot = np.array(x, dtype=np.float64, order="C", copy=True)
    key = (snapshot.shape, snapshot.tobytes(), float(scale))
    return _compute(*key).copy()
''',
'''
a = gram(x, 1.)
a[0,0] = -99.
print(gram(x, 2.).tolist())
print(gram(x.reshape(4,1), 1.).tolist())
''',
"The key omits shape and scale, and the cached object is returned by reference. A caller can poison later answers; identical bytes can represent differently shaped matrices. Canonicalise a detached float64 snapshot, key the complete semantics, calculate from that same snapshot, bound entry count, and return a copy. A read-only return alone does not meet the requested mutable-output contract. Original dtype need not be keyed after deliberate canonicalisation to float64.",
'''
np.testing.assert_allclose(gram(x,2),[[20,28],[28,40]])
np.testing.assert_allclose(gram(x.reshape(4,1),1),[[30]])
a=gram(x,1); a[:]=0
np.testing.assert_allclose(gram(x,1),x.T@x)
z=x.copy(); gram(z,1); z[0,0]=10
np.testing.assert_allclose(gram(z,1),z.T@z)
np.testing.assert_allclose(gram(x[:,::-1],3),
                           3*x[:,::-1].T@x[:,::-1])
for i in range(140): gram(np.array([[float(i)]]),1)
assert _compute.cache_info().currsize <= 128
assert gram(x,1).flags.writeable
''',
"Finds incomplete keys, aliasing and unbounded retention; connects key and calculation to one snapshot; recognises the O(nd) snapshot/hash and O(d^2) output-copy costs.",
"List every fact that determines a result, and every object the caller can mutate.",
"128 entries is not a byte budget. Design a byte-bounded policy, discuss cache stampedes and process boundaries, and explain what an authoritative immutable dataset version would buy.")

add(5,"Streaming windows across chunks and tied timestamps","Advanced","20 to 30","Time-series engineering",
"For each arriving (entity, time, value), report the mean of that entity's earlier observations in [time-3,time), or None if fewer than two exist. All observations at the current timestamp must be excluded, including earlier arrivals with the same timestamp. Per-entity times are nondecreasing across all batches; entities can interleave. Values are integers. Reject an out-of-order timestamp. Results must be invariant to arbitrary batch boundaries, including a boundary inside a tied timestamp. Retain only the time-window state and the current timestamp group per entity.",
'''
from collections import deque
rows = [
    ("A",0,1), ("A",2,3), ("A",2,7), ("A",5,9),
    ("B",1,10), ("B",2,20), ("B",4,30), ("A",6,11)
]
batches = [rows[:5], rows[5:]]
''',
'''
def process(batches):
    output = []
    for batch in batches:
        history = {}
        for entity, t, value in batch:
            q = history.setdefault(entity, deque())
            while q and q[0][0] < t - 3:
                q.popleft()
            output.append(
                sum(v for _,v in q)/len(q) if len(q)>=2 else None
            )
            q.append((t,value))
    return output
''',
'''
class Windows:
    def __init__(self):
        self.state = {}

    def update(self, entity, t, value):
        s = self.state.setdefault(entity, {
            "time": None, "pending_sum": 0, "pending_n": 0,
            "groups": deque(), "total": 0, "n": 0
        })
        if s["time"] is not None and t < s["time"]:
            raise ValueError("Out-of-order timestamp")
        if s["time"] is not None and t > s["time"]:
            s["groups"].append(
                (s["time"], s["pending_sum"], s["pending_n"])
            )
            s["total"] += s["pending_sum"]
            s["n"] += s["pending_n"]
            s["pending_sum"] = s["pending_n"] = 0
        s["time"] = t
        while s["groups"] and s["groups"][0][0] < t - 3:
            _, subtotal, count = s["groups"].popleft()
            s["total"] -= subtotal
            s["n"] -= count
        answer = s["total"]/s["n"] if s["n"] >= 2 else None
        s["pending_sum"] += value
        s["pending_n"] += 1
        return answer

def process(batches):
    engine = Windows()
    return [
        engine.update(*row)
        for batch in batches for row in batch
    ]
''',
'''print(process(batches))''',
"Resetting history per batch loses live state. Appending each current row immediately also exposes earlier rows at the same timestamp, violating the strict upper bound. Keep a pending sum/count for the current timestamp and commit that group only when the entity's time advances. Expire committed groups strictly before the lower boundary. This yields amortised O(1) work per event and stores timestamp groups in the live window plus one pending group per entity. It does not provide a bound on the number of inactive entity keys.",
'''
expected=[None,None,None,5.,None,None,15.,None]
assert process([rows]) == expected
for cut in range(len(rows)+1):
    assert process([rows[:cut],rows[cut:]]) == expected
assert process([[r] for r in rows]) == expected
assert process([[],rows,[]]) == expected
assert process([[("X",0,0),("X",0,0),("X",3,9)]]) == [None,None,0.]
engine=Windows()
engine.update("A",3,2)
try:
    engine.update("A",2,9)
except ValueError:
    pass
else:
    raise AssertionError("Late event accepted")
assert engine.update("A",3,4) is None
assert engine.update("A",4,8) == 3
''',
"Preserves state across chunks, excludes the entire current timestamp group, derives the boundary rules, and tests arbitrary repartitioning rather than a single convenient chunk layout.",
"Should two rows with the same entity and timestamp see each other?",
"Now allow bounded lateness and correction of already emitted features. Ask for a watermark contract, retained history, revision identifiers and state checkpoint semantics. Do not accept sorting each batch as a global solution.")

add(6,"Merging covariance states from unequal partitions","Advanced","20 to 30","Numerical and distributed",
"Each partition returns (n, mean, M2), where M2 is the unnormalised centred cross-product matrix. Combine disjoint partitions to recover the overall mean and unbiased sample covariance M2/(N-1), using only these summaries. Partitions can be unequal or empty. Preserve input states. Require N >= 2 for covariance. Explain and derive the merge formula; do not concatenate raw observations.",
'''
import numpy as np

def summarise(x):
    if len(x) == 0:
        d=x.shape[1]
        return 0, np.zeros(d), np.zeros((d,d))
    mean=x.mean(axis=0)
    centred=x-mean
    return len(x), mean, centred.T@centred

a=np.array([[1.,2.],[3.,4.]])
b=np.array([[10.,2.],[11.,4.],[12.,6.]])
states=[summarise(a),summarise(b)]
''',
'''
def combine(states):
    nonempty=[s for s in states if s[0]]
    n=sum(s[0] for s in nonempty)
    mean=np.mean([s[1] for s in nonempty],axis=0)
    m2=sum(s[2] for s in nonempty)
    return mean,m2/(n-1)
''',
'''
def merge(left, right):
    na, ma, ca = left
    nb, mb, cb = right
    if na == 0:
        return nb, mb.copy(), cb.copy()
    if nb == 0:
        return na, ma.copy(), ca.copy()
    n = na + nb
    delta = mb - ma
    mean = ma + delta * (nb/n)
    m2 = ca + cb + np.outer(delta,delta) * (na*nb/n)
    return n, mean, m2

def combine(states):
    states=list(states)
    if not states:
        raise ValueError("No states")
    n,m,c=states[0]
    acc=(n,m.copy(),c.copy())
    for state in states[1:]:
        acc=merge(acc,state)
    n,mean,m2=acc
    if n < 2:
        raise ValueError("Too few observations")
    return mean,m2/(n-1)
''',
'''
mean,cov=combine(states)
print(np.round(mean,6).tolist())
print(np.round(cov,6).tolist())
''',
"An unweighted mean of partition means is biased toward small partitions. Summing within-partition scatter loses the between-partition mean displacement. For delta = mean_b - mean_a, the missing term is outer(delta,delta) * n_a*n_b/(n_a+n_b). Derive this by expanding each partition's deviations around the combined mean; the within-partition cross terms sum to zero. Divide only once by total N-1. Algebraic associativity is not bitwise floating-point associativity.",
'''
whole=np.vstack([a,b])
mean,cov=combine(states)
np.testing.assert_allclose(mean,[7.4,3.6])
np.testing.assert_allclose(cov,[[25.3,4.2],[4.2,2.8]])
rng=np.random.default_rng(31)
x=rng.normal(size=(53,4))+1e6
parts=[x[:1],x[1:17],x[17:17],x[17:]]
m,c=combine([summarise(p) for p in parts])
np.testing.assert_allclose(m,x.mean(0),atol=1e-9)
np.testing.assert_allclose(c,np.cov(x,rowvar=False),atol=1e-9)
mr,cr=combine([summarise(p) for p in parts[::-1]])
np.testing.assert_allclose(cr,c,atol=1e-9)
copy=states[0][2].copy()
combine(states)
np.testing.assert_array_equal(states[0][2],copy)
assert np.linalg.eigvalsh(c).min() >= -1e-12
try: combine([summarise(np.ones((1,2)))])
except ValueError: pass
else: raise AssertionError("One-row covariance accepted")
''',
"Derives the between-block outer product; handles unequal sizes and empty summaries; tests random repartitioning, translations, symmetry and an independent covariance calculation.",
"Where does the variability between partition means appear?",
"Extend to weighted observations. Ask them to distinguish frequency weights from reliability weights and to state the denominator convention before coding. Discuss merge-tree order and reproducibility.")

add(7,"Parallel Monte Carlo with the wrong experimental unit","Advanced","20 to 30","Numerical simulation",
"Estimate E[exp(0.1 Z)] for standard normal Z using antithetic pairs (Z,-Z). Each logical block specifies a unique nonnegative integer block_id and a positive integer number of pairs. Different blocks require independent random streams. Reordering or rescheduling these same logical blocks must leave the numerical result unchanged; changing the partition into logical blocks is a different experiment. Return estimate and estimated standard error. Aggregate compact block summaries, not all simulated paths. At least two pairs exist overall.",
'''
import numpy as np
tasks=[(0,4),(1,7),(2,5)]
root_seed=123
''',
'''
def simulate(tasks, root_seed):
    values=[]
    for block_id,n in tasks:
        rng=np.random.default_rng(root_seed)
        z=rng.standard_normal(n)
        values.extend(np.exp(0.1*z))
        values.extend(np.exp(-0.1*z))
    values=np.asarray(values)
    return values.mean(),values.std(ddof=1)/np.sqrt(len(values))
''',
'''
def block_summary(block_id, n, root_seed):
    seed=np.random.SeedSequence(root_seed,spawn_key=(block_id,))
    rng=np.random.default_rng(seed)
    z=rng.standard_normal(n)
    pairs=(np.exp(0.1*z)+np.exp(-0.1*z))/2
    mean=float(pairs.mean())
    m2=float(np.sum((pairs-mean)**2))
    return n,mean,m2

def simulate(tasks, root_seed):
    tasks=list(tasks)
    ids=[i for i,_ in tasks]
    if len(ids)!=len(set(ids)) or any(n<=0 for _,n in tasks):
        raise ValueError("Invalid logical blocks")
    summaries={
        i:block_summary(i,n,root_seed) for i,n in tasks
    }
    total=0
    mean=m2=0.
    for i in sorted(summaries):
        n,m,c=summaries[i]
        new_total=total+n
        delta=m-mean
        m2+=c+delta*delta*(total*n/new_total)
        mean+=delta*(n/new_total)
        total=new_total
    if total<2:
        raise ValueError("Too few pairs")
    return mean,np.sqrt(m2/(total-1)/total)
''',
'''
estimate,se=simulate(tasks,root_seed)
print(f"estimate={estimate:.9f} se={se:.9f}")
''',
"Reinitialising the same seed creates overlapping prefixes, not independent blocks. The two members of an antithetic pair are correlated: the independent experimental unit is the pair mean, so its sample variance determines the standard error. Use a random stream indexed by logical block identity, merge the pair-level moments with their counts, and reduce in a fixed order for scheduling invariance. The incorrect standard error is not guaranteed to be biased in one direction. A valid uncertainty formula does not guarantee any particular finite-sample confidence interval covers the true mean.",
'''
est,se=simulate(tasks,root_seed)
pairs=[]
for i,n in tasks:
    rng=np.random.default_rng(
        np.random.SeedSequence(root_seed,spawn_key=(i,)))
    z=rng.standard_normal(n)
    pairs.extend(np.cosh(0.1*z))
pairs=np.asarray(pairs)
np.testing.assert_allclose(est,pairs.mean(),atol=1e-15)
np.testing.assert_allclose(se,pairs.std(ddof=1)/np.sqrt(len(pairs)),
                           atol=1e-15)
assert simulate(tasks[::-1],root_seed)==simulate(tasks,root_seed)
assert simulate(tasks,root_seed)==simulate(tasks,root_seed)
assert simulate(tasks,124)!=simulate(tasks,root_seed)
assert block_summary(0,4,root_seed)!=block_summary(1,4,root_seed)
try: simulate([(0,4),(0,5)],root_seed)
except ValueError: pass
else: raise AssertionError("Duplicate block accepted")
''',
"Identifies stream reuse and dependence within pairs; gets the experimental unit and unequal-block aggregation right; defines the scope of reproducibility precisely.",
"How many independent observations does a pair of antithetic payoffs represent?",
"Ask how common random numbers would be used for a finite-difference sensitivity, where the independent unit becomes a paired difference. Discuss block repartitioning, worker changes and regression tests without demanding a particular random confidence interval.")

add(8,"Single flight computation under waiter cancellation","Specialist stretch","25 to 35","Async Python systems",
"Within one asyncio event loop, concurrent requests for one key must share one computation. Cache successful immutable results. A cancelled waiter must receive cancellation without cancelling the shared work or other waiters; work is allowed to finish even if all waiters leave. Failed or internally cancelled work must be removable so a later call can retry. Do not start speculative duplicate work. Use ordinary task scheduling, not an eager task factory. Repair the class and explain ownership and cleanup.",
'''
import asyncio
''',
'''
class Cache:
    def __init__(self, fetch):
        self.fetch=fetch
        self.tasks={}

    async def get(self, key):
        task=self.tasks.setdefault(
            key, asyncio.create_task(self.fetch(key))
        )
        return await task
''',
'''
class Cache:
    def __init__(self, fetch):
        self.fetch=fetch
        self.tasks={}

    def retire(self, key, task):
        failed=task.cancelled() or task.exception() is not None
        if failed and self.tasks.get(key) is task:
            self.tasks.pop(key)

    async def get(self, key):
        task=self.tasks.get(key)
        if task is not None and task.done():
            self.retire(key,task)
            task=self.tasks.get(key)
        if task is None:
            task=asyncio.create_task(self.fetch(key))
            self.tasks[key]=task
            task.add_done_callback(
                lambda done,k=key: self.retire(k,done)
            )
        return await asyncio.shield(task)
''',
'''
async def demonstration():
    calls=0
    started=asyncio.Event()
    release=asyncio.Event()

    async def fetch(key):
        nonlocal calls
        calls+=1
        started.set()
        await release.wait()
        return 42

    cache=Cache(fetch)
    a=asyncio.create_task(cache.get("x"))
    await started.wait()
    b=asyncio.create_task(cache.get("x"))
    await asyncio.sleep(0)  # allow b to enter get
    a.cancel()
    release.set()
    result=await asyncio.gather(a,b,return_exceptions=True)
    try:
        retry=await cache.get("x")
    except asyncio.CancelledError:
        retry="cancelled"
    await asyncio.sleep(0)
    labels=["cancelled" if isinstance(v,asyncio.CancelledError)
            else v for v in result]
    print(calls,labels,retry)

asyncio.run(demonstration())
''',
"setdefault evaluates its default argument even when the key exists, so it starts unused tasks. Directly awaiting the shared task lets cancellation propagate from a waiter to the computation. Keeping that cancelled task poisons later calls. Separate lookup from task creation, retain a strong task reference, shield the shared task from waiter cancellation, and retire failed tasks. Creation and dictionary insertion have no intervening await under the stated event-loop contract. Identity-checked cleanup prevents an old completion from removing a newer task.",
'''
async def tests():
    calls=0
    async def flaky(key):
        nonlocal calls
        calls+=1
        if calls==1: raise RuntimeError("transient")
        return key
    c=Cache(flaky)
    try: await c.get("A")
    except RuntimeError: pass
    else: raise AssertionError("Failure hidden")
    assert await c.get("A")=="A"
    assert await c.get("A")=="A" and calls==2
    assert await c.get("B")=="B" and calls==3

    count=0
    gate=asyncio.Event()
    async def work(key):
        nonlocal count
        count+=1
        await gate.wait()
        return 7
    c=Cache(work)
    waiters=[asyncio.create_task(c.get("x")) for _ in range(8)]
    await asyncio.sleep(0)
    waiters[0].cancel()
    gate.set()
    outcomes=await asyncio.gather(*waiters,return_exceptions=True)
    assert isinstance(outcomes[0],asyncio.CancelledError)
    assert outcomes[1:]==[7]*7 and count==1
    assert await c.get("x")==7
    c=Cache(work)
    t=asyncio.create_task(c.get("z"))
    await asyncio.sleep(0)
    c.tasks["z"].cancel()
    try: await t
    except asyncio.CancelledError: pass
    assert await c.get("z")==7
    count=0
    gate=asyncio.Event()
    c=Cache(work)
    waiters=[asyncio.create_task(c.get("all")) for _ in range(2)]
    await asyncio.sleep(0)
    for t in waiters: t.cancel()
    await asyncio.gather(*waiters,return_exceptions=True)
    gate.set()
    assert await c.get("all")==7 and count==1
asyncio.run(tests())
''',
"Finds eager default evaluation, cancellation propagation and poisoned-cache retention. Uses events to create an explicit interleaving; explains why a thread lock or broad cancellation catch is not the repair.",
"Which object is cancelled when a task awaiting another Task is cancelled?",
"Add invalidation during in-flight work, a global concurrency limit and bounded cache memory. Ask whether the same design is safe across threads, loops or processes. Treat this as a specialist probe, not a universal numerical-quant prerequisite.")

add(9,"Point in time reconstruction with revisions and withdrawals","Expert stretch","25 to 35","Research data integrity",
"For each decision, choose the newest active event for the same symbol that was available at the decision. Event and availability are different clocks. A revision replaces that event's previous version only once available; DELETE withdraws that event, not the entire symbol. Resolve the latest available version of each event BEFORE selecting the newest active event. Event age must be at most ttl=5 inclusive. Return missing if none qualifies, preserving decision order. (symbol,event_min,available_min) keys and decision ids are unique; available_min>=event_min; a DELETE price is missing. Inputs can be shuffled. Give a correct reference repair and a credible scalable design.",
'''
import numpy as np
import pandas as pd
decisions=pd.DataFrame({
    "id":range(8), "symbol":["A"]*6+["B"]*2,
    "time":[3,5,6,7,8,9,3,4]
})
quotes=pd.DataFrame({
    "symbol":["A","A","A","A","A","A","B"],
    "event_min":[0,2,2,2,1,4,2],
    "available_min":[0,3,5,6,7,8,4],
    "action":["SET","SET","SET","DELETE","SET","SET","SET"],
    "price":[100.,102.,103.,np.nan,101.,104.,202.]
})
''',
'''
def reconstruct(decisions, quotes, ttl=5):
    clean=quotes.loc[quotes.action.eq("SET")]
    clean=clean.sort_values("available_min").drop_duplicates(
        ["symbol","event_min"],keep="last"
    )
    out=pd.merge_asof(
        decisions.sort_values("time"),
        clean.sort_values("event_min"),
        by="symbol",left_on="time",right_on="event_min",
        direction="backward",tolerance=ttl
    )
    return out.set_index("id").reindex(decisions["id"])
''',
'''
def reconstruct(decisions, quotes, ttl=5):
    result=[]
    for d in decisions.itertuples(index=False):
        known=quotes.loc[
            quotes.symbol.eq(d.symbol)
            & quotes.available_min.le(d.time)
            & quotes.event_min.le(d.time)
        ]
        versions=known.sort_values("available_min").drop_duplicates(
            "event_min",keep="last"
        )
        eligible=versions.loc[
            versions.action.eq("SET")
            & versions.event_min.ge(d.time-ttl)
        ]
        if eligible.empty:
            result.append(np.nan)
        else:
            latest=eligible.sort_values("event_min").iloc[-1]
            result.append(float(latest.price))
    return decisions.assign(price=result).set_index("id")
''',
'''
out=reconstruct(decisions,quotes)
print([None if pd.isna(v) else float(v) for v in out.price])
''',
"The global latest-version snapshot leaks later revisions into earlier decisions. Filtering DELETE before resolving versions resurrects withdrawn events. A backwards event-time join alone enforces neither availability nor version history. For each decision, first select known versions, resolve each event's current version, then apply withdrawal and age rules and rank active events. At minute 6, A's newest event is withdrawn and its older available event is stale. At minute 7, the newly arrived event is also too old. No forward fill across these gaps is justified.",
'''
expected=[102.,103.,np.nan,np.nan,104.,104.,np.nan,202.]
np.testing.assert_allclose(reconstruct(decisions,quotes).price,
                           expected,equal_nan=True)
np.testing.assert_allclose(
    reconstruct(decisions,quotes.sample(frac=1,random_state=5)).price,
    expected,equal_nan=True)
early=decisions[decisions.time<=5]
np.testing.assert_allclose(reconstruct(early,quotes).price,
    reconstruct(early,quotes[quotes.available_min<=5]).price,
    equal_nan=True)
d=pd.DataFrame({"id":[10],"symbol":["A"],"time":[6]})
assert reconstruct(d,quotes,ttl=10).price.iloc[0]==100
assert reconstruct(decisions,quotes.iloc[:0]).price.isna().all()
assert reconstruct(decisions.iloc[:0],quotes).empty
restored=pd.concat([quotes,pd.DataFrame([{
    "symbol":"A","event_min":2,"available_min":7,
    "action":"SET","price":105.
}])],ignore_index=True)
d=pd.DataFrame({"id":[11],"symbol":["A"],"time":[7]})
assert reconstruct(d,restored).price.iloc[0]==105.
permuted=decisions.iloc[::-1]
assert reconstruct(permuted,quotes).index.tolist()==permuted.id.tolist()
''',
"Separates both clocks, resolves versions before withdrawals, handles fallback and stale data, and tests that future publications cannot change an earlier reconstruction.",
"What does deleting an event mean for its older published version?",
"Design an availability-ordered sweep with per-event versions and an ordered active-event structure or heap with lazy invalidation. Account for retained revision metadata and stale heap entries; do not claim O(number of symbols) state when an older event can become the fallback.")

add(10,"Updating a rolling precision matrix without changing the statistic","Expert stretch","30 to 40","Numerical algorithms",
"A window of n>=2 vectors has mean m and precision P = inverse(ridge*I + sum_i (x_i-m)(x_i-m).T), with fixed positive ridge. Replace outgoing old with incoming new. Update mean and P in O(d^2) arithmetic given m,P,old,new,n; do not silently switch to uncentred second moments. Preserve inputs. Signal numerically unsafe rank-one steps so the caller can rebuild from the retained window before publishing. You may use (A+c*v*v.T)^-1 = P - c*(P*v)*(P*v).T/(1+c*v.T*P*v). Derive the actual vectors and coefficients.",
'''
import numpy as np
x=np.array([[0.,0.],[1.,0.],[0.,1.],[1.,1.]])
ridge=0.5
mean=x.mean(0)
centred=x-mean
P=np.linalg.solve(
    ridge*np.eye(2)+centred.T@centred,np.eye(2)
)
old=x[0]
new=np.array([2.,2.])
''',
'''
def step(mean, P, old, new, n):
    v=P@old
    removed=P+np.outer(v,v)/(1-old@v)
    v=removed@new
    updated=removed-np.outer(v,v)/(1+new@v)
    return mean+(new-old)/n,updated
''',
'''
def rank_one(P, v, coefficient):
    Pv=P@v
    denominator=1+coefficient*(v@Pv)
    if not np.isfinite(denominator) or denominator<=1e-10:
        raise FloatingPointError("Rebuild from retained window")
    return P-coefficient*np.outer(Pv,Pv)/denominator

def step(mean, P, old, new, n):
    if n<2:
        raise ValueError("Window too short")
    delta_old=old-mean
    reduced_mean=mean-delta_old/(n-1)
    removed=rank_one(P,delta_old,-n/(n-1))
    delta_new=new-reduced_mean
    updated=rank_one(removed,delta_new,(n-1)/n)
    updated=(updated+updated.T)/2
    return reduced_mean+delta_new/n,updated
''',
'''
m,p=step(mean,P,old,new,len(x))
print(np.round(m,6).tolist())
print(np.round(p,6).tolist())
''',
"Raw old*old.T and new*new.T update an uncentred second moment, not scatter around a changing mean. Removal changes scatter by -n/(n-1) outer(old-m,old-m). Addition around the reduced mean changes it by (n-1)/n outer(new-m_reduced,new-m_reduced). Apply the rank-one identity to those two changes. A small positive downdate denominator can amplify rounding severely even if the final replacement window is well conditioned. The threshold is an explicit illustrative rebuild policy, not a universal error bound; symmetry restoration also does not repair inaccurate eigenvalues.",
'''
m,p=step(mean,P,old,new,len(x))
np.testing.assert_allclose(m,[1,1])
np.testing.assert_allclose(p,[[10/21,-4/21],[-4/21,10/21]])
rng=np.random.default_rng(12)
window=rng.normal(size=(12,4))
r=.7
m=window.mean(0)
c=window-m
p=np.linalg.solve(r*np.eye(4)+c.T@c,np.eye(4))
for _ in range(30):
    incoming=rng.normal(size=4)
    m,p=step(m,p,window[0],incoming,len(window))
    window=np.vstack([window[1:],incoming])
    expected_mean=window.mean(0)
    c=window-expected_mean
    a=r*np.eye(4)+c.T@c
    np.testing.assert_allclose(m,expected_mean,atol=1e-12)
    np.testing.assert_allclose(a@p,np.eye(4),atol=1e-11)
    assert np.linalg.eigvalsh(p).min()>0
Pcopy=P.copy()
step(mean,P,old,new,4)
np.testing.assert_array_equal(P,Pcopy)
mt,pt=step(mean+1e5,P,old+1e5,new+1e5,4)
np.testing.assert_allclose(pt,step(mean,P,old,new,4)[1],
                           atol=1e-11)
np.testing.assert_allclose(mt-1e5,[1,1])
try:
    step(np.array([0.]),np.array([[1/(2+1e-14)]]),
         np.array([1.]),np.array([1.]),2)
except FloatingPointError: pass
else: raise AssertionError("Unsafe downdate not detected")
''',
"Derives both centred scatter updates, applies the inverse identity with correct signs and coefficients, and recognises that an algebraically correct update may still require rebuilding. Tests the matrix residual across repeated updates.",
"Removing one observation changes the mean of every remaining deviation. Expand that change before applying the matrix identity.",
"Discuss maintaining a factorisation instead of an explicit inverse, residual-check frequency and cost, accumulated drift, a joint rank-two update, and rebuilding when the intermediate downdate is unstable although the final window is well conditioned.")

GOLDEN = {1: ('[1.16, 0.72]', '[1.5, 0.333333]'), 2: ('[1, 0, 0, 0]', '[1, 0, 1, 2]'), 3: ('[True, True, False, False]', '[False, True, False, False]'), 4: ('[[-99.0, 14.0], [14.0, 20.0]]\n[[-99.0, 14.0], [14.0, 20.0]]', '[[20.0, 28.0], [28.0, 40.0]]\n[[30.0]]'), 5: ('[None, None, 2.0, 5.0, None, None, None, None]', '[None, None, None, 5.0, None, None, 15.0, None]'), 6: ('[6.5, 3.5]\n[[1.0, 1.5], [1.5, 2.5]]', '[7.4, 3.6]\n[[25.3, 4.2], [4.2, 2.8]]'), 7: ('estimate=1.003397672 se=0.014836951', 'estimate=1.003530191 se=0.001573312'), 8: ("3 ['cancelled', 'cancelled'] cancelled", "1 ['cancelled', 42] 42"), 9: ('[103.0, 104.0, 104.0, 104.0, 104.0, 104.0, 202.0, 202.0]', '[102.0, 103.0, None, None, 104.0, 104.0, None, 202.0]'), 10: ('[1.0, 1.0]\n[[0.385965, -0.280702], [-0.280702, 0.385965]]', '[1.0, 1.0]\n[[0.47619, -0.190476], [-0.190476, 0.47619]]')}

def execute(code):
    ns={}
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):
        exec(compile(code,"<interview>","exec"),ns)
    return capture.getvalue().replace("\r\n","\n").rstrip(),ns

def validate():
    report=[]
    for q in Q:
        bad,_=execute(q["buggy"])
        good,ns=execute(q["fixed"])
        exec(compile(q["tests"],"<regressions>","exec"),ns)
        q["observed_bad"]=bad
        q["observed_good"]=good
        assert (bad,good)==GOLDEN[q["number"]],(q["number"],bad,good)
        report.append(f'Q{q["number"]:02d}: faulty run, model run and regressions PASS')
    return report

if __name__=="__main__":
    report=validate()
    (ROOT/"question_bank.json").write_text(
        json.dumps(Q,indent=2),encoding="utf-8")
    (ROOT/"verification.txt").write_text(
        f"Python {sys.version.split()[0]}; pandas {pd.__version__}; NumPy {np.__version__}\n"
        +"\n".join(report)+"\n",encoding="utf-8")
    print("\n".join(report))
    for q in Q:
        print(f'Q{q["number"]}: BAD {q["observed_bad"]!r} GOOD {q["observed_good"]!r}')
