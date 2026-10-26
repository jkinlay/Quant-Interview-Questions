from pathlib import Path
import ast, html, json, textwrap
ROOT=Path(__file__).resolve().parent
Q=json.loads((ROOT/"question_bank.json").read_text(encoding="utf-8"))
original=ast.parse((ROOT/"baseline_v1"/"_build_pack.py").read_text(encoding="utf-8"))
CSS=next(ast.literal_eval(n.value) for n in original.body
         if isinstance(n,ast.Assign) and any(
             isinstance(t,ast.Name) and t.id=="CSS" for t in n.targets))
def p(s): return "<p>"+html.escape(s)+"</p>"
def code(s): return "<pre><code>"+html.escape(textwrap.dedent(s).strip())+"</code></pre>"
def ul(items): return "<ul>"+"".join("<li>"+html.escape(s)+"</li>" for s in items)+"</ul>"
def table(head,rows):
    return "<table><thead><tr>"+"".join("<th>"+html.escape(str(x))+"</th>" for x in head)+"</tr></thead><tbody>"+"".join("<tr>"+"".join("<td>"+html.escape(str(x))+"</td>" for x in row)+"</tr>" for row in rows)+"</tbody></table>"
def doc(title,body,audience):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body><div class="toolbar">Advanced revision 2 | 26 October 2026 | '+audience+'</div><main><h1>'+html.escape(title)+'</h1>'+body+'<footer>Senior Quantitative Analysis | Advanced revision 2 | 26 October 2026</footer></main></body></html>'
rating={"Senior baseline":3,"Strong senior":4,"Advanced":4,
        "Specialist stretch":5,"Expert stretch":5}
intro=p("This bank is designed for a senior quantitative analyst with 10 to 15 years of substantial quantitative and Python experience. It tests whether a candidate can diagnose a plausible wrong result, recover the intended mathematical or software contract, implement a repair, and justify it under adversarial inputs.")
intro+=p("There are no elementary warm-ups. Even the baseline numerical question contains three independent defects. The harder problems require a derivation, an algorithmic invariant, or precise reasoning about state and time. Some include requirements that a small code patch cannot satisfy without a design change.")
intro+=p("Use two substantial questions and one case. A 90-minute interview allows a meaningful implementation and follow-up; for 75 minutes, choose two questions from the 15 to 25 minute tier and shorten the case. Difficulty and timings are proposed calibration values, not validated hiring thresholds.")
intro+='<nav><a href="#format">Interview format</a><a href="#bank">Ten questions</a><a href="#cases">Advanced cases</a><a href="#original">Supplied forecasting case</a><a href="#scoring">Scoring</a><a href="#verification">Verification</a></nav>'
intro+='<h2 id="format">Interview format</h2>'+table(["Minutes","Activity","What to require"],[
("0 to 5","Set the contract","Explain available tools, role focus and the distinction between reference and production code."),
("5 to 50","Two substantial problems","Trace the failure, repair at least one executable component, then derive or test its invariant."),
("50 to 75","One case discussion","Clarify the numerical and data contract, choose an implementation, and examine a failure scenario."),
("75 to 85","Stress the solution","Introduce a changed partition, data revision, cancellation or conditioning problem."),
("85 to 90","Candidate questions and close","Record evidence and assistance immediately after the interview.")
])
intro+=p("For 75 minutes: 5 minutes introduction, 40 minutes on two selected problems, 20 minutes on one case, 5 minutes on an extension, and 5 minutes for candidate questions. Q8 and Q10 can each use most of a 35-minute technical slot; do not force them into a 15-minute slot.")
intro+='<h3>Choose a route appropriate to the actual role</h3>'+table(["Role emphasis","Suggested questions","Case"],[
("Numerical research","Q1 and Q6","Case B on Monte Carlo sensitivities"),
("Research data and analytics","Q3 and Q9","Case A on a covariance service"),
("Python platforms and services","Q4 and Q8","Case C on replay and revisions"),
("Numerical algorithm specialist","Q2 and Q10 with extra time","A shorter discussion of Case A")
])
intro+=ul([
"Use a supervised company laptop, a prepared local environment and the same offline documentation access for every candidate. Ask the candidate to make and run a repair, not merely describe a library call.",
"State the mathematical objective and input contract. Provide the rank-one inverse identity in Q10 as written. The aim is to assess derivation and implementation rather than recall of a named formula.",
"Ask for a counterexample before a rewrite. Then ask which invariant the repair establishes, how it can be falsified, and what remains outside the guarantee.",
"Use a tiny independent oracle, metamorphic tests such as repartitioning or translation, and numerical residuals where appropriate. A passing example is insufficient evidence.",
"Ask for both arithmetic complexity and peak memory. An elegant vectorised expression can be inappropriate at the production scale.",
"Record hints. Use the same selected questions within a cohort and distinguish independent progress from work completed after a targeted prompt.",
"Do not require asynchronous-service expertise from a numerical researcher. Q8 is a specialist probe; Q10 is a numerical specialist probe. Depth in the role's core areas matters more than coverage of all ten.",
"Keep finance conventions, model economics and broad ML methodology for round two. All mathematical objects needed for these first-round tasks are defined in the prompt."
])
intro+='<h3>Make the follow-up diagnostic</h3>'+p("After a working repair, introduce one condition that invalidates a convenient assumption: a nested interval, a changed partition, a tied timestamp crossing a chunk boundary, a withdrawn observation, or cancellation of every waiter. Ask the candidate to predict the result and design a test before running it.")
intro+=p("Accept a simple correct reference implementation when the question allows it, but require an honest production complexity assessment. For Q3 and Q10, the stated complexity is part of the task; a brute-force repair earns partial credit and provides a starting point for the next step.")

bank='<h2 id="bank">Ten advanced debugging questions</h2>'
bank+=table(["Question","Subject","Rating","Time"],[(f'Q{q["number"]}',q["title"],f'{rating[q["level"]]}/5 {q["level"]}',q["minutes"]+" min") for q in Q])
bank+=p("Ratings are relative to this experienced cohort: 3 is a senior baseline, 4 is demanding senior work, and 5 is an expert or specialist stretch. The questions are a selection bank; completing all ten is not an interview objective. The model answers illustrate one defensible implementation under the stated contract.")
for q in Q:
    bank+=f'<section class="question" id="q{q["number"]}"><h2>Question {q["number"]} {html.escape(q["title"])}</h2>'
    bank+=p(f'{rating[q["level"]]}/5 | {q["level"]} | {q["track"]} | {q["minutes"]} minutes')
    bank+='<h3>Candidate contract</h3>'+p(q["intention"])
    bank+=code(q["buggy"])+'<p class="label">Observed faulty output</p>'+code(q["observed_bad"])
    bank+=p("Identify the mechanisms that violate the contract. Repair the implementation, explain why it is correct, and propose adversarial tests and relevant performance checks.")
    bank+='<h3>Interviewer model answer</h3>'+p(q["explanation"])+code(q["fixed"])
    bank+='<p class="label">Corrected output</p>'+code(q["observed_good"])
    bank+='<h3>What earns full credit</h3>'+p(q["criteria"])
    bank+='<h4>A staged hint</h4>'+p(q["hint"])
    bank+='<h4>Extension after a successful repair</h4>'+p(q["extension"])
    bank+='<p class="small">Executable regression checks for this question are included in interview_checks.py. Equivalent repairs that satisfy the same contract earn the same credit.</p></section>'

cov_prompt="A Python service calculates a covariance matrix for 4,000 variables and evaluates q = v.T @ C @ v for user-supplied vectors. Data has missing observations, a changing variable universe and occasional corrections. The process has a 2 GB working-memory budget. A pairwise-deletion implementation returns the following three-variable diagnostic matrix and a negative value of q. Diagnose the numerical and data issues, define a coherent contract, and design an implementation and validation strategy. A short prototype of one component is sufficient."
cov_fixture="C = [[1.0, 0.9, 0.9],\n     [0.9, 1.0, -0.9],\n     [0.9, -0.9, 1.0]]\nv = [-1.0, 1.0, 1.0]\nreported q = -2.4"
mc_prompt="A simulation estimates F(theta) = E[exp(theta*Z)] for standard normal Z, then differentiates it numerically. You are given F(theta) = exp(theta^2/2) and F'(theta) = theta*exp(theta^2/2) as check identities. The estimate becomes unstable as h becomes small. Diagnose whether the implementation is incorrect, statistically inefficient or both. Propose a trustworthy streaming and parallel implementation, its uncertainty estimate and a reproducibility contract. Use theta = 0.2; no finance knowledge is required."
mc_bad='''
import numpy as np

def sensitivity(theta,h,n,seed):
    rng=np.random.default_rng(seed)
    plus=np.exp((theta+h)*rng.standard_normal(n))
    minus=np.exp((theta-h)*rng.standard_normal(n))
    differences=(plus-minus)/(2*h)
    return differences.mean(),differences.std(ddof=1)/np.sqrt(n)
'''
stream_prompt="Design a service that emits entity-level features from event-time windows. Records have entity_id, event_id, event_time, available_time, revision and value; a revision can withdraw an event. Deliveries can repeat. Normal arrivals are at most two minutes late, but administrative corrections can refer to any historical date. The process can crash between writing output and checkpointing state. Explain the state model, publication contract, replay behaviour and tests, and implement one agreed component."
original_prompt="Review the supplied bullet-sales forecasting challenge as the prospective owner of its Python pipeline. Establish which requested outputs the source data identifies, define the information available at each forecast origin, and design a reproducible process that supports corrections and historical evaluation. After the first data-contract issues are discussed, the interviewer will supply assumptions so you can proceed to design and one small implementation. Fitting a forecasting model is not required."

cases='<section class="case" id="cases"><h2>Three cases for an experienced quant</h2>'
cases+=p("Use one case for about 25 minutes. These are open-ended engineering reviews with a narrow coding step; a complete production implementation is not expected. Clarify which decision or component the candidate should implement after the first five minutes. The interviewer notes below contain the model discussion and staged reveals.")
cases+='<h3>Case A A covariance service with credible but impossible outputs</h3>'+p(cov_prompt)+code(cov_fixture)
cases+='<h4>Staged discussion</h4>'+ul([
"First ask for a diagnosis of the supplied matrix and a test that would establish it.",
"Reveal that each pair used its own available observations, its own means and its own sample count. Ask what guarantees are lost.",
"Ask the candidate to choose an explicit missingness and weighting contract, and write one component such as a common-sample covariance calculation or a matrix-validation function.",
"Introduce 4,000 variables, the memory limit and data corrections. Ask what must be retained, recomputed, versioned and monitored."
])
cases+='<h4>Model discussion</h4>'+p("The example has eigenvalues approximately -0.8, 1.9 and 1.9. Its quadratic form for the supplied vector is -2.4. Symmetry and a positive diagonal do not establish that a matrix is a valid covariance. Pairwise estimates on different samples need not form one positive semidefinite covariance matrix.")
cases+=p("A candidate should define the estimand before choosing a repair. A common complete-observation sample with common nonnegative weights yields a Gram-form positive semidefinite estimate, but may discard too much data. An explicit factor, imputation or shrinkage model can provide another coherent estimator; each introduces assumptions. Deleting the negative eigenvalue produces a different estimate and must be treated as a documented change, not a recovery of the missing source information.")
cases+=p("For this diagnostic matrix, blending C with the identity as (1-alpha)*C + alpha*I makes the smallest eigenvalue -0.8 + 1.8*alpha. Positive semidefiniteness requires alpha >= 4/9, and positive definiteness requires a strict inequality. This is a mathematical illustration; it does not select a statistically appropriate shrinkage strength.")
cases+=p("A dense 4,000 by 4,000 float64 matrix alone is 128,000,000 bytes, approximately 122 MiB. Raw observations, multiple matrix copies and decompositions add materially to that footprint. Compute memory before proposing a vectorised method. Distinguish a requirement to materialise the covariance from a requirement only to apply it to vectors; a factor representation or matrix operator may change the appropriate design.")
cases+=p("Tests should cover symmetry, finite entries, dimensions and variable ordering, a Gram-form oracle, translation invariance of centred covariance, selected quadratic forms, and behaviour under a changing universe. Random nonnegative quadratic forms alone do not prove PSD. An eigenvalue or factorisation check needs a documented numerical tolerance and an explicit distinction between semidefinite and strictly positive definite.")
cases+=p("Strong performance includes a defensible data policy, an implementation consistent with it, realistic memory accounting, and the ability to explain what a numerical repair changes. Round two can examine covariance modelling, shrinkage selection and portfolio implications.")
cases+='<h3>Case B Monte Carlo sensitivities that get worse as the step shrinks</h3>'+p(mc_prompt)+code(mc_bad)
cases+='<h4>Staged discussion</h4>'+ul([
"Ask what random quantity the reported standard error describes and what happens to its variance as h tends to zero.",
"Request a common-random-number implementation and a comparison with the supplied analytic derivative.",
"Introduce streaming blocks, parallel scheduling and worker retries; ask how the estimate and its error bar are aggregated.",
"Ask for a test strategy that distinguishes finite-difference bias, Monte Carlo error and floating-point error."
])
cases+='<h4>Model discussion</h4>'+p("Independent plus and minus samples give a valid but noisy central-difference estimator of the difference of expectations. The displayed standard error is for the sampled differences; it is not automatically incorrect. Its variance grows roughly as 1/h^2 when the two sides are sampled independently. A strong candidate separates statistical inefficiency from a software defect.")
cases+=p("Use the same Z for the plus and minus evaluations and compute a per-draw difference before estimating its uncertainty. For this smooth example, the pathwise derivative Z*exp(theta*Z) is another check and estimator. The exact central-difference expectation can be computed from the given F; its bias relative to F' is of order h^2. Reducing h indefinitely eventually introduces floating-point cancellation.")
cases+=code('''
def paired_sensitivity(z,theta,h):
    differences=(
        np.exp((theta+h)*z)-np.exp((theta-h)*z)
    )/(2*h)
    return differences.mean(),differences.std(ddof=1)/np.sqrt(len(z))
''')
cases+=p("A more stable evaluation for this particular function can use exp(theta*z) * sinh(h*z) / h, with attention to scaling and overflow for a broader parameter range. If antithetic sampling is added, form independent pair-level derivative contributions before estimating variance. Do not divide a path-level standard deviation by the square root of an inappropriate count.")
cases+=p("Assign random streams to logical block ids and maintain a versioned experiment specification. Retry the same block with the same stream and deduplicate the returned block result; otherwise a successful retry can be counted twice. Merge (count, mean, centred sum of squares), and use a fixed reduction order if bitwise scheduling invariance is required under the same runtime.")
cases+=p("Test fixed-draw algebra, paired-versus-pathwise convergence as h decreases, unequal block sizes, task-order invariance, retry deduplication and the exact expectation as a statistical check. Do not make a single random confidence interval covering the truth a deterministic test requirement. Strong performance explains all three error sources and chooses a reproducibility scope that can actually be delivered.")
cases+='<h3>Case C Features that survive revisions and process failure</h3>'+p(stream_prompt)
cases+='<h4>Staged discussion</h4>'+ul([
"Ask for the identities and time axes, including what a withdrawal changes.",
"Require precise window endpoints, equal-timestamp rules and a watermark contract for normal arrivals.",
"Place a crash after output publication but before checkpoint persistence. Ask the candidate to walk through a replay and propose a test.",
"Finally ask for exact correction of every historical output with bounded memory and no durable event archive. See whether the candidate recognises that the requirements are incompatible."
])
cases+='<h4>Model discussion</h4>'+p("Separate event identity, event time, availability time and revision order. Maintain an authoritative version history or equivalent source capable of reconstructing it. Decide whether outputs are provisional or final and how later revisions are represented. A watermark for normal lateness does not make arbitrary historical administrative corrections disappear.")
cases+=p("A workable design can keep bounded online window state for normal arrivals, durable source history for backfill, and versioned output identities for corrections. Replays must be idempotent. Output publication and checkpoint advancement need an atomic transaction when they share a transactional store, or a suitable commit protocol and idempotent sink otherwise. Persisting a processed-id set separately from effects is insufficient.")
cases+=p("After a crash between publication and checkpoint, replay may re-emit the same logical output. Its id or version must make the effect idempotent. A changed input revision must produce a deliberate new output version, not be discarded as an identical retry. Record the input watermark or source offset, code version, configuration and state version together.")
cases+=p("Exact unbounded historical correction with bounded memory and no durable archive cannot generally be achieved: the information needed to revise an old window has been discarded. The candidate should identify which constraint must change. Reward a precise impossibility argument and a feasible revised contract.")
cases+=p("A suitable coding step is the version-selection rule, a pure state transition for a timestamp group, or an idempotent publication-key function with tests. Tests should include duplicate deliveries, conflicting reuse of ids, withdrawals, equal timestamps, correction of a prior window, checkpoint restoration, and injected crashes on both sides of the publication boundary.")
cases+=p("Strong performance includes explicit ownership of every guarantee, a failure trace and an implementation consistent with the trace. A promise of exactly-once processing without a storage or protocol explanation is insufficient.")
cases+='</section>'

orig='<section class="case" id="original"><h2>How to use the supplied forecasting case at this level</h2>'
orig+=p(original_prompt)
orig+=p("At this seniority, identifying missing maker/model values is an opening observation, not a successful conclusion to the case. Use it to establish the data contract, then supply a hypothetical corrected series-id mapping and proceed. State clearly that the mapping is an interview assumption; it is not recoverable from row order in the supplied CSV.")
orig+=table(["Source observation","What a senior candidate should do with it"],[
("Both files cover 1810-01-01 to 1816-12-31, seven years rather than the six described.","Set the forecast origin and full monthly horizon explicitly; reconcile the specification with the data."),
("All 15,342 RS rows lack Maker and Model. A maps to three maker/model combinations in TF, B to two, C to one.","Explain why a compatibility mapping does not allocate pooled replacement demand. Ask for source series identity and authoritative lineage."),
("There are 14 exact repeated visible RS records, and each date has three A rows, two B rows and one C row.","Distinguish legitimate observations with lost identifiers from delivery duplicates. Specify an identity-based ingestion policy."),
("Neither file includes publication timestamps or revision history.","Explain what a historical as-of evaluation can and cannot establish from a current extract. Do not invent data vintages."),
("The task asks for a 12-month replacement-sales forecast and model-level aggregates.","Define the output grain, information set, coherent aggregation and conditions under which each output is supportable.")
])
orig+='<h3>Senior follow-on tasks</h3>'+ul([
"Define a data contract with stable series identity, maker/model mapping validity, event month, available-at time, revision semantics and Quantity units.",
"Design the transformation boundaries: ingest and validate, resolve versions as of a forecast origin, aggregate, construct permissible features, fit, predict, reconcile and publish a versioned result.",
"Specify what an immutable run manifest contains and how a historical run is reproduced after source corrections or code changes.",
"Explain the information available for every one of the 12 forecast months. Historical handgun sales or known TF estimates do not by themselves establish future realised handgun covariates.",
"Implement or repair one difficult component: a point-in-time join, a chunk-invariant lag feature, a validated mapping join with effective dates, or a rolling-origin generator with correctly timed inputs.",
"Choose an invariant and an adversarial test: no future publication changes an earlier as-of result, reordering or chunking cannot change totals, revisions do not double count, and aggregate forecasts reconcile to their defined components."
])
orig+=p("Use a simple baseline only to define the evaluation pipeline. Reserve model families, installed-base dynamics, replacement hazards, hierarchical forecasting, finance and ML depth for round two. A candidate should explain which outputs are blocked by missing data and how they would still deliver a clearly scoped, reproducible result.")
orig+='</section>'

score='<section class="case" id="scoring"><h2>Scoring the senior evidence</h2>'
score+=p("For two selected questions, score each out of 20. Score the case out of 20, for 60 possible points. Do not compare totals across different specialist routes without calibration. Pilot the questions with experienced colleagues and agree what independent versus prompted work looks like before using a cutoff.")
score+=table(["Per question","Points","Full credit"],[
("Diagnosis",4,"Finds interacting mechanisms and explains the observed output."),
("Repair",6,"Executable implementation meets the stated numerical, timing, ownership and complexity contract."),
("Reasoning",4,"Derives the update or invariant and states what it guarantees."),
("Validation",4,"Uses counterexamples, an independent oracle or residual checks, and relevant adversarial cases."),
("Trade-offs",2,"Explains memory, stability, reproducibility and realistic limitations.")
])
score+=table(["Case dimension","Points","Full credit"],[
("Specification and assumptions",4,"Separates supported requirements, assumptions and incompatible guarantees."),
("Numerical and data design",5,"Chooses a coherent information set, estimand and state model."),
("Python implementation",5,"Implements an agreed component correctly and explains its costs."),
("Verification and failure reasoning",4,"Tests meaningful failure scenarios and identifies observable invariants."),
("Prioritisation",2,"Explains what to deliver first and what remains unresolved.")
])
score+=p("For each dimension, distinguish no useful evidence, partial progress with substantial help, mostly correct work with a small omission, and independent complete reasoning. Record the actual assistance rather than applying an automatic double penalty for hints.")
score+='<h3>What separates a capable senior from a very strong one</h3>'+ul([
"A capable senior repairs the specified defect and writes useful tests. A very strong candidate identifies the invariant, anticipates the next failure mode, and can explain when an apparently faster repair changes the problem.",
"Naming QR, Welford, a heap, a watermark or an idempotency key is not sufficient. Ask for the actual transformation or failure trace.",
"An accurate slower reference implementation is valuable evidence. Where the prompt requires a complexity bound, record that the full requirement remains unmet and invite an optimisation with an equivalence test.",
"Treat Q8 and Q10 as expertise-specific evidence. Do not let unfamiliarity with one specialised API dominate the assessment of a different role.",
"Do not award a senior pass solely for finding the missing identifiers in the supplied dataset or for repeating generic advice about leakage, vectorisation or unit tests."
])
score+='<h3>Interviewer record</h3>'+p("Candidate ____________________   Route ____________________   Date ____________________")
score+=table(["Question","Diagnosis /4","Repair /6","Reasoning /4","Tests /4","Trade-offs /2"],[("Q____","","","","",""),("Q____","","","","","")])
score+=p("Case selected ____________________   Case score /20 ____________________")
score+=p("Independent evidence ______________________________________________________________")
score+=p("Hints and assistance ______________________________________________________________")
score+=p("Unresolved concern and round two probe ______________________________________________")
score+='</section>'

verify='<section id="verification"><h2>Verification and sources</h2>'
verify+=p("All ten faulty snippets and model repairs were executed in isolated namespaces. Displayed outputs were recorded and checked against fixed expected outputs; repaired implementations passed targeted numerical and behavioural regressions. Checks include random interval-oracle comparisons, repeated matrix updates, cancellation interleavings, changes of partition and point-in-time noninterference.")
verify+=p("Runtime: Python 3.12.14, pandas 3.0.1, NumPy 2.3.5. These are verified examples under that runtime, not benchmark results or proof of production readiness. Random scheduling contracts apply to the same logical blocks and runtime. The async example uses the ordinary asyncio task factory.")
verify+='<p>The runnable companion <a href="interview_checks.py">interview_checks.py</a> contains the complete question bank and checks. <a href="advanced_case_checks.py">advanced_case_checks.py</a> checks the numerical illustrations in the advanced cases. The original materials are preserved in the baseline_v1 folder for reference.</p>'
verify+=p("The existing forecasting discussion is grounded in Data science challenge.docx, bullets_sales.csv and handgun_sales.csv from source_materials. The document was treated as source material; its request to produce forecasts was not treated as a separate instruction. Source observations were verified during preparation of the original pack and retained here.")
verify+='<h3>API references</h3>'
verify+='<p>The least-squares interface and numerical rank behaviour are documented in <a href="https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html">NumPy lstsq</a>. Interval boundary semantics are documented in <a href="https://numpy.org/doc/2.3/reference/generated/numpy.searchsorted.html">NumPy searchsorted</a>.</p>'
verify+='<p>The cache interface is described in <a href="https://docs.python.org/3.12/library/functools.html#functools.lru_cache">Python functools</a>; cancellation shielding in <a href="https://docs.python.org/3.12/library/asyncio-task.html#shielding-from-cancellation">Python asyncio</a>. Random-stream construction is covered by <a href="https://numpy.org/doc/stable/reference/random/parallel.html">NumPy parallel random generation</a>. These sources support API semantics; the interview design and ratings are proposed for this role.</p>'
verify+=p("The files are self-contained HTML with print styling. The content, code, internal links and candidate-answer separation have been checked. Rendered print layout has not been visually verified because the in-app browser rejected local-file preview.")
verify+='</section>'

(ROOT/"interviewer_guide.html").write_text(
    doc("Advanced Senior Quant Python Interview",intro+bank+cases+orig+score+verify,"Interviewer answers"),encoding="utf-8")
candidate=p("This interview is intended for an experienced quantitative Python practitioner. You will receive selected questions, not the full bank as a timed examination. Each includes a contract, code and its actual output.")
candidate+=p("Explain the mechanisms that violate the contract, implement a repair, and establish why it is correct. Discuss numerical stability, memory and time costs where relevant. You may use the reference material supplied by the interviewer; equivalent correct implementations are welcome.")
candidate+=p("The code was run with Python 3.12, pandas 3.0 and NumPy 2.3. Assume the stated input contract. Request clarification if a production guarantee requires information that is not supplied.")
candidate+='<nav>'+"".join(f'<a href="#q{q["number"]}">Question {q["number"]}</a>' for q in Q)+'</nav>'
for q in Q:
    candidate+=f'<section class="question" id="q{q["number"]}"><h2>Question {q["number"]}</h2>'
    candidate+=p(q["intention"])+code(q["buggy"])
    candidate+='<p class="label">Actual output</p>'+code(q["observed_bad"])
    candidate+=p("Diagnose, repair and justify the implementation. Propose adversarial tests and discuss its relevant costs and limitations.")
    candidate+='<p class="label">Notes</p><div class="notes"></div></section>'
(ROOT/"candidate_questions.html").write_text(doc(
    "Advanced Quant Python Exercises",candidate,"Candidate copy without answers"),encoding="utf-8")
handout=p("The interviewer will select one case, introduce further constraints and agree one small component to implement. Define the contract, explain your design, and use a concrete example or failure trace to test it.")
handout+='<section class="case"><h2>Case A Covariance service</h2>'+p(cov_prompt)+code(cov_fixture)+'</section>'
handout+='<section class="case"><h2>Case B Monte Carlo sensitivities</h2>'+p(mc_prompt)+code(mc_bad)+'</section>'
handout+='<section class="case"><h2>Case C Event time features</h2>'+p(stream_prompt)+'</section>'
handout+='<section class="case"><h2>Case D Review the forecasting pipeline</h2>'+p(original_prompt)
handout+=table(["Input","Columns"],[
("bullets_sales.csv","Date, Maker, Model, Bullets, Channel, Quantity"),
("handgun_sales.csv","Date, Maker, Model, Quantity")])
handout+=p("TF denotes sales together with firearms and RS denotes replacement sales. The original requested output is a 12-month replacement-sales forecast by bullet type and aggregated by handgun maker and model.")+'</section>'
(ROOT/"candidate_cases.html").write_text(doc(
    "Advanced Quant Case Discussions",handout,"Candidate copy without answers"),encoding="utf-8")
print("Replaced interviewer guide, candidate questions and candidate cases with advanced revision 2.")
