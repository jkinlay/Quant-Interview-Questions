from pathlib import Path
import html, json, textwrap
from datetime import date
ROOT = Path(__file__).resolve().parent
Q = json.loads((ROOT / "question_bank.json").read_text(encoding="utf-8"))
def p(text): return "<p>" + html.escape(text) + "</p>"
def code(text): return "<pre><code>" + html.escape(textwrap.dedent(text).strip()) + "</code></pre>"
def ul(items): return "<ul>" + "".join("<li>"+html.escape(i)+"</li>" for i in items) + "</ul>"
def table(headers, rows):
    return "<table><thead><tr>"+"".join("<th>"+html.escape(str(x))+"</th>" for x in headers)+"</tr></thead><tbody>"+ "".join("<tr>"+"".join("<td>"+html.escape(str(x))+"</td>" for x in r)+"</tr>" for r in rows)+"</tbody></table>"
CSS = """
:root{color-scheme:light;--ink:#182332;--muted:#526171;--line:#ccd5df;}
*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:var(--ink);background:#f3f5f7;margin:0;line-height:1.6}
main{max-width:1000px;margin:32px auto;padding:52px 64px;background:white;border:1px solid #e0e5eb}
h1,h2,h3,h4{color:#000;line-height:1.2;break-after:avoid}h1{font-size:34px;margin:0 0 18px}h2{font-size:25px;margin:46px 0 17px}h3{font-size:19px;margin:26px 0 12px}h4{font-size:15px;margin:20px 0 8px}
p{margin:10px 0 15px}li{margin:6px 0}ul,ol{padding-left:24px}a{color:#24548c;text-underline-offset:3px}nav{margin:24px 0 32px}nav a{display:inline-block;margin:3px 16px 3px 0}
.meta{color:var(--muted);font-size:14px}.label{font-weight:700;margin-bottom:6px}
pre{font-family:Consolas,"Courier New",monospace;font-size:13px;line-height:1.48;white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7f9;border:1px solid #dce2e9;padding:16px;margin:10px 0 18px;tab-size:4}
code{font-family:inherit}table{width:100%;border-collapse:collapse;margin:18px 0 26px;font-size:14px;break-inside:auto}
th,td{border:1px solid var(--line);padding:10px 12px;vertical-align:middle;text-align:left}th{background:#223951;color:#fff;font-weight:600}tbody tr:nth-child(even){background:#f5f8fb}tr{break-inside:avoid}thead{display:table-header-group}
.question{margin-top:48px;padding-top:1px}.answer{margin-top:25px}.small{font-size:13px}.rule{margin-top:22px;font-weight:700}
footer{margin-top:44px;color:var(--muted);font-size:12px}.toolbar{max-width:1000px;margin:20px auto 0;font-size:14px}
@media(max-width:720px){main{margin:0;padding:24px 20px;border:0}h1{font-size:29px}pre{font-size:12px;padding:12px}table{font-size:12px}th,td{padding:7px}.toolbar{padding:0 20px}}
@media print{@page{size:A4;margin:17mm}body{background:white;font-size:10.5pt;line-height:1.4}main{max-width:none;margin:0;padding:0;border:0}h1{font-size:25pt}h2{font-size:18pt;margin-top:24pt}h3{font-size:14pt}h4{font-size:11pt}pre{font-size:9pt;line-height:1.3;padding:9pt;break-inside:avoid}table{font-size:9pt}th,td{padding:6pt}a{color:inherit;text-decoration:none}.toolbar,nav{display:none}.question,.case{break-before:page}.meta{font-size:9pt}footer{font-size:8pt}.notes{height:32mm;border-bottom:1px solid #ccc}.print-break{break-before:page}}
"""
def doc(title, content, audience):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body><div class="toolbar">Printable interview materials · 26 October 2026 · '+audience+'</div><main><h1>'+html.escape(title)+'</h1>'+content+'<footer>Senior Quantitative Analysis recruitment · Round 1 · Prepared 26 October 2026</footer></main></body></html>'

schedule = [
("0 to 5", "Introduction", "Explain the format and allow a short silent reading period."),
("5 to 35", "Four debugging exercises", "Suggested route Q2, Q3, Q6 and Q8. Ask for a repair and a test."),
("35 to 60", "One structured case", "Use the adapted attachment or one alternative; include a small supervised coding step."),
("60 to 70", "Extension and evidence gaps", "Deepen one earlier task, test an edge case, or discuss scale."),
("70 to 75", "Candidate questions", "Finish consistently and record evidence immediately afterwards.")
]
intro = p("Use a structured, supervised work sample: ask the candidate to explain a failure, repair it, and demonstrate how they know the repair works. Combine that with one short case in which requirements and data limitations emerge in stages.")
intro += p("The ten questions form a bank, not a single interview. Four selected questions plus one case are enough for a 75-minute round. This pack assumes practical Python, pandas and NumPy are relevant to the role. Difficulty and timing are proposed calibration levels, not measured hiring thresholds.")
intro += p("LLM access weakens an unsupervised test as evidence of independent coding ability. It does not remove the value of coding in an interview. A supervised repair and an unannounced change of requirement make the candidate's reasoning and implementation visible.")
intro += '<nav><a href="#format">Interview format</a><a href="#bank">Question bank</a><a href="#attachment">Adapted case</a><a href="#alternatives">Alternative cases</a><a href="#score">Scoring</a><a href="#sources">Sources and verification</a></nav>'
intro += '<h2 id="format">How to run round one</h2>' + table(["Minutes","Activity","Interviewer action"], schedule)
intro += ul([
"Use a company laptop with a prepared local editor or notebook. The interviewer stays present. Keep external assistants and communication tools unavailable for this exercise; a short printed or offline API reference is reasonable if offered consistently.",
"Give the intention, code and actual output together. Ask: what causes this result, what would you change, and what test would catch it? Let the candidate read silently before explaining.",
"Require at least one runnable repair. A whiteboard or spoken outline alone can miss whether someone can translate an idea into Python. If necessary, the interviewer can type under the candidate's explicit direction.",
"Tell candidates that library syntax can be looked up in the provided reference. Score their choice of operations and tests, rather than exact recall of parameter names.",
"Use the same core route and staged hints for a hiring cohort. Record which hints were used. Rotate equivalent variants between cohorts after checking them.",
"Keep finance conventions, model selection theory and ML depth for round two. In round one, score Python correctness, data handling, testing, information timing and engineering judgement.",
"Q9 and Q10 are stretch items. Do not require every senior candidate to finish them, and do not let one memorised trick compensate for weak performance on core tasks.",
"For a 60-minute interview, use 5 minutes introduction, 25 minutes debugging, 20 minutes for one case, 5 minutes follow-up and 5 minutes candidate questions."
])
intro += '<h3>Consistent hints and follow-ups</h3>' + p("Start with no hint. If the candidate stalls, ask them to trace the smallest failing example. Next offer the question-specific hint below. Finally, identify the relevant area if needed and see whether they can complete the repair. Record the help given; do not silently compare a heavily prompted solution with an independent one.")
intro += p("Once a repair works, change one condition: shuffle input, add an empty group, repeat a key, or introduce a delayed record. Ask the candidate to predict the result before running it. One well-chosen change usually provides more evidence than rushing to another puzzle.")

bank = '<h2 id="bank">Ten debugging questions</h2>'
bank += table(["Question","Focus","Difficulty","Minutes"], [(f'Q{q["number"]}',q["title"],f'{q["difficulty"]} of 5',q["minutes"]) for q in Q])
bank += p("Scale: 1 easy, 2 straightforward, 3 intermediate, 4 hard, 5 very hard. These are reference solutions; accept equivalent implementations that meet the stated contract. Inputs outside the contract are follow-up material, not hidden requirements.")
for q in Q:
    bank += f'<section class="question" id="q{q["number"]}"><h2>Question {q["number"]} {html.escape(q["title"])}</h2>'
    bank += p(f'Difficulty {q["difficulty"]} of 5 · Suggested time {q["minutes"]} minutes')
    bank += '<h3>Candidate brief</h3>' + p(q["intention"]) + code(q["buggy"])
    bank += '<p class="label">Actual output from the faulty code</p>'+code(q["observed_bad"])
    bank += p("Explain the result, repair the code, and propose tests that would detect the defect.")
    bank += '<div class="answer"><h3>Interviewer model answer</h3>'+p(q["explanation"])+code(q["fixed"])
    bank += '<p class="label">Corrected output</p>'+code(q["observed_good"])
    bank += '<h4>Tests to expect</h4>'+p(q["tests_description"])
    bank += '<h4>Hint</h4>'+p(q["hint"])+'<h4>Follow-up</h4>'+p(q["followup"])
    bank += '<h4>Evidence of senior ability</h4>'+p(q["senior"])+'</div></section>'

case_prompt = (
"You are designing a Python process to forecast monthly replacement sales for the next 12 months. "
"Two files contain historical bullet sales and handgun sales. Bullet sales have two channels: TF, sold together with firearms, and RS, replacements. "
"The requested outputs are replacement sales by bullet type and by handgun maker and model. "
"Explain the data checks and transformations you would implement, sketch the process, and write one small transformation with tests. "
"You do not need to fit a forecasting model during this interview. State any output you cannot support from the supplied information."
)
schemas = table(["File","Columns"],[
("bullets_sales.csv","Date, Maker, Model, Bullets, Channel, Quantity"),
("handgun_sales.csv","Date, Maker, Model, Quantity")
])
evidence_rows = [
("Date coverage in both files","1 January 1810 to 31 December 1816; 2,557 daily dates and 84 calendar months.","The brief's six-year description is inconsistent with the files."),
("Bullet sales","30,684 rows: 15,342 TF and 15,342 RS.","Filter the intended channel explicitly."),
("Missing identifiers","Every RS row has missing Maker and Model; TF rows have both.","The requested model-level RS target is not fully identified."),
("Shared bullet types","A occurs with three maker/model pairs; B with two; C with one in TF.","Compatibility does not provide a unique allocation for A or B."),
("Repeated visible RS keys","Each date has three A rows, two B rows and one C row.","A date and bullet label do not identify a unique underlying series."),
("Exact repeated RS records","14 rows repeat all visible fields beyond their first occurrence.","They may be legitimate different series with lost identifiers; do not blindly delete them."),
("Handgun sales","15,342 rows across six maker/model pairs; composite date/maker/model keys are unique.","Model labels are reused across makers; Model alone is not a safe join key.")
]
attachment = '<section class="case" id="attachment"><h2>Adapt the supplied forecasting case</h2>'
attachment += p("The supplied exercise is useful, but its original deliverable is too broad for a short first-round interview. It asks for a 12-month forecast and code in Python or R. Reframe it as a Python data-engineering and specification discussion, then retain the modelling depth for round two.")
attachment += '<h3>What the actual files reveal</h3>'+table(["Observation","Verified evidence","Interview implication"], evidence_rows)
attachment += p("All three bullet labels have records for every date, and the observed quantities are nonnegative. There are no missing dates at that pooled label level. These checks do not prove that the underlying series identities or business meaning are correct.")
attachment += p("The main limitation is identifiability. The TF compatibility table is one-to-many for A and B; joining it to pooled RS totals would duplicate quantities or impose an unsupported allocation. The apparent order of rows is not a documented business key. Forward-filling maker/model or assigning consecutive blocks to models would require authoritative confirmation.")
attachment += p("The C label has one observed TF association, but inferring its RS attribution still assumes that compatibility is exhaustive, stable and encoded consistently across channels. That does not resolve A or B. For full model-level forecasts, request a stable source series id on every RS record and an authoritative mapping to maker/model, or explicitly agree an allocation model and label its estimates as assumption-dependent.")
attachment += '<h3>Candidate prompt</h3>'+p(case_prompt)+schemas
attachment += '<h3>A 25 minute staged discussion</h3>'+table(["Time","Interviewer action","Evidence to look for"],[
("0 to 4 minutes","Give the prompt, schemas and a few rows.","Clarifies monthly frequency, target grain, forecast origin and meaning of Quantity."),
("4 to 10 minutes","Reveal the profile and compatibility counts above.","Recognises missing identity, distinguishes legitimate repeated rows from ingestion duplicates, asks for source keys."),
("10 to 17 minutes","Confirm for this exercise that RS rows are distinct additive sales. Ask for monthly pooled RS aggregation by bullet label.","Writes a clear, testable transformation; preserves quantities; does not fabricate a maker/model allocation."),
("17 to 22 minutes","Ask for two tests and an evaluation outline. State that future realised handgun sales are unavailable.","Tests channel, totals and time boundaries; uses only information available at the forecast origin."),
("22 to 25 minutes","Ask what they would deliver today and what is blocked.","Can deliver conditional pooled outputs and a data-quality note; gives a precise request for the unresolved model-level target.")
])
attachment += '<h3>Model discussion</h3>'+ul([
"Clarify whether '12 months ahead' means a monthly path for months 1 through 12, a single month-12 value, or a 12-month total. Set the forecast origin explicitly. A sensible exercise convention is a monthly January to December 1817 path from 31 December 1816.",
"Identify the raw and target grains. Use Maker plus Model for handgun keys. Treat missing RS identity as a source issue and do not use forward-fill, row order or a many-to-many join as an undocumented repair.",
"Parse dates explicitly, verify accepted channels and bullet labels, inspect Quantity units and missingness, and check calendar coverage. Keep missing observations distinct from true zero sales.",
"Once the interviewer confirms additive RS rows, aggregate by calendar month and bullet label. Compare row-level and aggregated totals. Keep the original data and the assumptions used.",
"Start with a seasonal-naive monthly baseline: forecast a month using the same month of the previous year. Its value is as a benchmark, not a presumed best model. Do not promise accuracy without evaluation.",
"Use whole future time blocks across all series, with an actual 12-month forecast from each historical origin. An example is training through 1813 to predict 1814, through 1814 to predict 1815, and holding 1816 for final evaluation using data through 1815.",
"Any transformations learned from data, feature selection and parameter tuning must use the training period at each origin. Do not populate later forecast-month lags with realised target values unless the evaluation explicitly represents an updating one-step process.",
"Only use future covariates available at that historical origin. Historical handgun sales and a statement about reliable TF estimates do not establish that future handgun sales are known. Use separate covariate forecasts or scenarios when necessary.",
"Evaluate monthly absolute error by bullet label and aggregate, with an explicit weighting rule if scale varies. Be wary of percentage errors when actuals are zero and of aggregate errors hiding offsetting mistakes. Discuss uncertainty and stockout costs in round two.",
"Return an output with forecast_origin, target_month, horizon, level, bullet or model key, forecast and model_version, plus data-quality findings and assumptions. If intervals are included, evaluate their coverage separately."
])
monthly_code = '''
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
'''
attachment += '<h3>A suitable supervised coding step</h3>'+p("Ask the candidate to implement monthly_rs after confirming the additive-row assumption. For this small transformation, state that Quantity is already a validated nonnegative integer and Channel has already been validated. Keep source validation in a separate step.")
attachment += code(monthly_code)
attachment += p("Test with an RS row and a TF row on the same date, records on the last and first days of adjacent months, several RS rows for the same label, an observed zero, and shuffled input. Assert one row per month/label, conservation of the RS total, and no input mutation. Do not fill unobserved months with zero without a business rule.")
attachment += p("On the supplied files, this transformation produces 252 observed month/label rows, conditional on that additive-row assumption. It does not solve the missing maker/model allocation. A candidate who explicitly explains that distinction is showing useful judgement.")
attachment += '<h3>What belongs in round two</h3>'+p("Extend the same case into stock-versus-flow reasoning, replacement demand lags, installed-base and survival models, seasonality, structural change, pooled versus separate estimation, forecast reconciliation and uncertainty. Discuss ML only after agreeing the information set and evaluation design. Remove the historical narrative or rename the products as equipment and replacement components if that makes the brief clearer.")
attachment += '</section>'

alt_a_prompt = "Design a function that computes net quantity by sku from event deliveries. delta is a signed change. The same event_id may be delivered repeatedly; identical business payloads count once. Reuse of an event_id with a different sku or delta is an error. Keep skus with a zero net result. Delivery time is metadata, not part of the business payload. Start with the rows below, then explain how the design changes across daily batches."
alt_a_rows = [("e1","X",10),("e2","X",-3),("e1","X",10),("e3","Y",5),("e4","X",-7),("e5","Y",-2)]
alt_a_code = '''
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
'''
alt_b_prompt = "Implement an object with update(entity, value). For each entity, retain its latest three accepted observations and return their mean once three exist; otherwise return None. The mean includes the current observation. Events initially arrive in order for each entity. Entity keys are strings and values are finite numbers. State the memory cost, then discuss how duplicate deliveries and late events would change the contract."
alt_b_rows = [("A",10,None),("B",100,None),("A",20,None),("A",30,20),("B",200,None),("A",40,30),("B",300,200)]
alt_b_code = '''
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
'''
alt_c_prompt = "A feature job computes the mean of earlier values from the same entity in the interval [minute - 3, minute). It requires at least two earlier observations. Keys (entity, minute) are unique and input order is arbitrary. The current implementation scans the complete table for each row. Explain its cost, design a faster implementation, and show how you would prove the result is unchanged. Do not replace a time interval with a fixed number of rows."
alt_c_rows = [(0,"A",1,10),(1,"A",2,20),(2,"B",1,100),(3,"A",4,40),(4,"A",5,50),(5,"B",4,400)]
alt_c_code = '''
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
'''
alt_c_fix = '''
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
'''
alts = '<section class="case" id="alternatives"><h2>Three alternative case discussions</h2>'
alts += p("For a first round whose main objective is Python proficiency, Alternative A is my preferred default. It tests a small implementable contract and then exposes production design judgement. B is best for stateful services; C is best for research data pipelines. Each fits about 25 minutes with one 8 to 10 minute supervised coding step. Use one case per interview.")
alts += '<h3>Alternative A Reliable event ingestion</h3>'+p(alt_a_prompt)+table(["event_id","sku","delta"],alt_a_rows)
alts += '<h4>Staged prompts</h4>'+ul([
"First five minutes: ask for the data contract, including missing ids, invalid quantities and the meaning of a repeated id.",
"Next ten minutes: implement the in-memory reference function and test an exact replay, a conflicting replay and a zero net result.",
"Next five minutes: reveal that the next file overlaps yesterday's events and the process can fail between writing totals and recording processed ids.",
"Final five minutes: ask for a durable state design, replay behaviour and an observable failure report."
])
alts += '<h4>Model answer</h4>'+p("The fixture returns {'X': 0, 'Y': 3}. Count each logical event once, retain zero-valued results, and reject conflicting payloads instead of keeping the first or last silently. The local reference below is O(n) expected time with O(u + s) state for u distinct event ids and s skus.")
alts += code(alt_a_code)
alts += p("Across batches, the processed-event registry must persist. Recording an accepted event and applying its quantity change must happen atomically, for example within one database transaction with a unique event-id constraint. Retrying then becomes idempotent. Define whether corrections are new reversing events or versioned replacements. A fingerprint alone must not silently ignore a changed payload under the same id.")
alts += p("Tests: exact replay within and across batches; conflicting sku or delta; empty input; negative and zero deltas; independent skus; simulated failure and retry. Reject or quarantine invalid records according to a stated policy; do not count them as successful.")
alts += '<h4>Strong evidence and round two extension</h4>'+p("Strong candidates distinguish event identity from row equality, keep the implementation simple, and understand why persistent deduplication and total updates must agree. In round two, adapt this to trade corrections, positions and P&L reconciliation after explicitly teaching any required domain conventions.")
alts += '<h3>Alternative B A small rolling statistics service</h3>'+p(alt_b_prompt)
alts += table(["Entity","Value","Expected returned mean"],[(a,b,"None" if c is None else c) for a,b,c in alt_b_rows])
alts += '<h4>Staged prompts</h4>'+ul([
"Ask the candidate to sketch the state and walk through interleaved entities.",
"Implement update and test warm-up, the fourth observation, and independence between entities.",
"Reveal duplicate request ids. Ask what makes an update idempotent and what happens if the same id carries a different value.",
"Reveal out-of-order timestamps. Ask whether 'latest' means arrival order or event time, and whether published results must be corrected."
])
alts += '<h4>Model answer</h4>'+code(alt_b_code)
alts += p("The reference stores a deque and running total per entity, taking O(1) work per accepted update and O(3s) value storage for s active entities, plus dictionary overhead. On the fourth update for an entity, subtract the outgoing value before adding the new one. State grows with the number of active entities; an eviction policy needs an explicit business contract.")
alts += p("Tests: no output until the third value; correct removal on the fourth; interleaved entities; all zero; negative values; two independent service instances. For long floating-point streams, discuss rounding drift and periodic recalculation or compensated accumulation.")
alts += p("Do not treat duplicate ids or late timestamps as implementation details with an obvious answer. They change the contract. A strong candidate asks about retention, allowed lateness, replay and corrections before selecting a data structure. In round two, extend this to rolling volatility, event time versus clock time and irregular sampling.")
alts += '<h3>Alternative C Make a feature pipeline scale safely</h3>'+p(alt_c_prompt)
alts += table(["Row","Entity","Minute","Value"],alt_c_rows)+code(alt_c_code)
alts += '<h4>Staged prompts</h4>'+ul([
"Ask for the correct output by hand and the exact interval boundaries.",
"Reveal that the input has two million rows. Ask where the time and memory will go.",
"Ask for a faster outline or implementation, preserving original row order.",
"Introduce missing minutes, then require a comparison against the slow implementation on small random examples."
])
alts += '<h4>Model answer</h4>'+p("The expected result in original row order is [None, None, None, 15.0, 30.0, None]. The nested scan is O(n squared). Sort by entity and minute, maintain a deque of prior observations and a running sum, remove entries strictly older than minute minus 3, compute the feature, then insert the current observation. The order of those last two steps excludes the current row.")
alts += code(alt_c_fix)
alts += p("Sorting costs O(n log n); the sweep costs O(n) because each observation enters and leaves the deque once. This in-memory reference also retains the sorted input and output, so total auxiliary memory is O(n), not constant. Its active window size depends on observation density, not simply the number 3.")
alts += p("Compare against the slow reference on small random, shuffled datasets; test the inclusive lower boundary, exclusive upper boundary, single-observation windows and independent entities. Profile representative data and check peak memory. Chunking needs ordered input and window state carried across chunks. A vectorised pandas time-based rolling solution is also acceptable if its closed interval and row alignment are correct.")
alts += p("In round two, discuss how these features enter a forecasting or trading decision, how their information timestamps are established, and how to avoid leakage in evaluation.")
alts += '</section>'

rubric = '<section class="case" id="score"><h2>Scoring and calibration</h2>'
rubric += p("Score the observable evidence, including the candidate's response to a test or counterexample. Use the same question route within a cohort. The following is a proposed rubric to pilot with your own staff; it is not a validated hiring threshold.")
rubric += table(["Per debugging question","Points","Full credit evidence"],[
("Diagnosis",3,"Explains the causal mechanism and the observed output."),
("Repair",3,"Meets the whole stated contract and avoids introducing a new error."),
("Tests",3,"Chooses discriminating tests including a boundary, invariant or counterexample."),
("Explanation",1,"Explains assumptions and the consequence of the change clearly.")
])
rubric += p("For each three-point dimension: 0 = absent or materially wrong; 1 = partial and requires substantial direction; 2 = mostly correct with a small prompt or omission; 3 = independent and complete. Use the separate hint record as context, without deducting points twice for the same assistance. A correct alternative solution earns the same credit as the model answer.")
rubric += table(["Case dimension","Points","What to assess"],[
("Problem and contract",4,"Defines the output, assumptions, boundaries and failure policy."),
("Data and state",4,"Finds key, identity, timing or state issues in the chosen case."),
("Python design and implementation",5,"Produces a coherent small implementation and sensible complexity analysis."),
("Validation",5,"Tests meaningful cases, uses an oracle or invariants, and investigates failures."),
("Trade-offs and communication",2,"Explains unresolved issues and a feasible next step.")
])
rubric += p("For the suggested route of four debugging questions, the maximum is 40 plus 20 for the case. Record the raw scores and the pattern of strengths; do not compare totals across different routes as though their difficulty were equal. Treat the optional extension as additional evidence, not an unannounced extra pass requirement.")
rubric += '<h3>Suggested decision anchors</h3>'+ul([
"Strong evidence: repairs intermediate tasks mostly independently, writes meaningful tests, and recognises the main identity or time constraint in the case. Can explain both the implementation and its limits.",
"Mixed evidence: spots familiar mistakes but needs help to finish or test the repair, or gives a plausible design without translating it into code. Record exactly what remains uncertain.",
"Weak evidence for this round: cannot explain basic state or data handling after prompts, changes code without checking the specified behaviour, or repeatedly hides invalid inputs and missing information.",
"Do not interpret polished vocabulary, speed, or prior knowledge of one trick as sufficient evidence. A candidate can perform well while looking up syntax and working carefully.",
"Pilot the timings and rubric with several current colleagues. Review where competent people need clarification, remove accidental ambiguities, and agree evidence standards before interviewing candidates. Arrange reasonable accommodations and consistent reference access."
])
rubric += '<h3>Reusable interviewer score sheet</h3>'
rubric += p("Candidate ____________________   Interviewer ____________________   Date ____________________")
rubric += table(["Question","Diagnosis /3","Repair /3","Tests /3","Explanation /1","Hints and evidence"],[("Q____","","","","","") for _ in range(4)])
rubric += table(["Case","Contract /4","Data /4","Python /5","Validation /5","Trade-offs /2"],[("____________","","","","","")])
rubric += p("Strongest evidence __________________________________________________________________")
rubric += p("Unresolved evidence _________________________________________________________________")
rubric += p("Suggested round two probe ____________________________________________________________")
rubric += '</section>'

sources = '<section id="sources"><h2>Sources and verification</h2>'
sources += p("The three supplied files were treated as source material for framing an interview. The original document's request to fit a model and submit forecasts was not carried out as a separate instruction.")
sources += ul([
"Data science challenge.docx — the original task wording and requested forecast outputs.",
"bullets_sales.csv — channel, identity, date coverage and repeated-row checks; pooled monthly transformation.",
"handgun_sales.csv — maker/model coverage and composite-key checks."
])
sources += p("Source folder: ../source_materials. Counts and schema findings were checked directly on 26 October 2026. No claim is made about how the supplied data was generated or what the missing identifiers were intended to encode.")
sources += p("All ten faulty snippets and reference repairs were executed in separate namespaces. Their displayed outputs were checked, then the repaired functions were exercised with targeted regressions. Runtime: Python 3.12.14, pandas 3.0.1, NumPy 2.3.5. Newline conventions are normalised for display. The question bank deliberately avoids relying on version-dependent chained-assignment behaviour.")
sources += '<p>The runnable companion <a href="interview_checks.py">interview_checks.py</a> contains every snippet and regression check. <a href="case_checks.py">case_checks.py</a> checks the case reference functions and source observations. Recheck the pack in the actual interview environment before use.</p>'
sources += '<h3>Technical references</h3>'
sources += '<p>Python object defaults and iterator behaviour are documented in the <a href="https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects">Python FAQ</a> and <a href="https://docs.python.org/3/library/stdtypes.html#iterator-types">iterator documentation</a>. The relevant shape rules are in the <a href="https://numpy.org/doc/stable/user/basics.broadcasting.html">NumPy broadcasting guide</a>.</p>'
sources += '<p>Join validation is described in <a href="https://pandas.pydata.org/docs/reference/api/pandas.merge.html">pandas merge</a>; time-distance joins in <a href="https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html">pandas merge_asof</a>. The independent population-variance reference is <a href="https://docs.python.org/3/library/statistics.html#statistics.pvariance">statistics.pvariance</a>. These references support API semantics; the interview questions, timing and scoring are proposed materials for this role.</p></section>'

guide = doc("Senior Quantitative Analysis interview guide", intro+bank+attachment+alts+rubric+sources, "Interviewer copy with answers")
(ROOT / "interviewer_guide.html").write_text(guide, encoding="utf-8")

cand = p("You will work through selected Python questions with the interviewer, followed by one case discussion. The supplied output is from the faulty code. Explain why it occurs, propose a correction, and show how you would test it. State assumptions when needed.")
cand += p("You are not expected to complete this entire bank. Each selected question is self-contained. You may use the reference material supplied by the interviewer. Ask for clarification and take a short period to read before talking through your answer.")
cand += p("The inputs meet the stated contracts unless the interviewer explicitly changes them. The examples use Python 3.12, pandas 3.0 and NumPy 2.3. Equivalent correct approaches are welcome.")
cand += '<nav>'+ "".join(f'<a href="#q{q["number"]}">Question {q["number"]}</a>' for q in Q)+'</nav>'
for q in Q:
    cand += f'<section class="question" id="q{q["number"]}"><h2>Question {q["number"]}</h2>'
    cand += p(q["intention"])+code(q["buggy"])
    cand += '<p class="label">Actual output</p>'+code(q["observed_bad"])
    cand += p("Explain the result, repair the code, and propose tests that would detect the defect.")
    cand += '<p class="label">Notes</p><div class="notes"></div></section>'
(ROOT / "candidate_questions.html").write_text(doc("Python debugging exercises",cand,"Candidate copy without answers"),encoding="utf-8")

cases = p("The interviewer will select one case and introduce additional information during the discussion. Explain your assumptions, sketch an implementation, and write or direct a short piece of Python when asked. A complete production system or fitted forecasting model is not required.")
cases += '<section class="case"><h2>Case one Replacement sales process</h2>'+p(case_prompt)+schemas
cases += '<h3>Questions to consider</h3>'+ul(["What do you need to clarify about the output and the source data?","What checks and transformations would you implement?","What can you deliver from the available information?","How would you test the process and evaluate a future forecast?"])+'</section>'
cases += '<section class="case"><h2>Case two Reliable event ingestion</h2>'+p(alt_a_prompt)+table(["event_id","sku","delta"],alt_a_rows)
cases += p("Write a function for this batch and choose tests. Then explain what must change when later batches overlap earlier ones.")+'</section>'
cases += '<section class="case"><h2>Case three Rolling statistics service</h2>'+p(alt_b_prompt)+table(["Entity","Value"],[(a,b) for a,b,c in alt_b_rows])
cases += p("Walk through the updates, implement the state, and choose tests. Then discuss duplicate deliveries and late events with the interviewer.")+'</section>'
cases += '<section class="case"><h2>Case four Faster historical features</h2>'+p(alt_c_prompt)+table(["Row","Entity","Minute","Value"],alt_c_rows)+code(alt_c_code)
cases += p("Work out the result for the example, propose a faster approach, and explain how you would compare the two implementations.")+'</section>'
(ROOT / "candidate_cases.html").write_text(doc("Python case discussions",cases,"Candidate copy without answers"),encoding="utf-8")

# Share exact reference code with the verification companion.
(ROOT / "_case_reference.json").write_text(json.dumps({
"monthly":textwrap.dedent(monthly_code).strip(),
"a":textwrap.dedent(alt_a_code).strip(),
"b":textwrap.dedent(alt_b_code).strip(),
"c_slow":textwrap.dedent(alt_c_code).strip(),
"c_fast":textwrap.dedent(alt_c_fix).strip()
},indent=2),encoding="utf-8")
print("Created interviewer guide and two candidate handouts.")
