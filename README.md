# Senior Quantitative Analysis interview materials

The current pack is **advanced revision 2**, designed for candidates with 10 to 15 years of substantial quantitative and Python experience. It contains ten debugging challenges, difficulty ratings, observed outputs, model repairs, regression checks, scoring guidance and advanced case discussions.

## Start here

- [Interviewer guide and model answers](interviewer_guide.html)
- [Candidate debugging questions without answers](candidate_questions.html)
- [Candidate case discussions without answers](candidate_cases.html)
- [Structured question bank](question_bank.json)

Download or clone the repository and open the HTML files in a browser. GitHub's file view shows HTML source. Print styles are included; print layout has not been visually verified. No GitHub Pages site has been configured.

Use two substantial questions and one case over approximately 75 to 90 minutes. The guide distinguishes numerical-research, research-data and Python-platform routes. Specialist asynchronous and numerical-algorithm questions should be selected to match the role.

The interviewer guide, question-bank JSON and verification scripts contain answers. Provide candidates with the candidate handouts and selected source material, rather than the full repository.

## Current question bank

| Question | Subject |
| --- | --- |
| 1 | Weighted regularisation and a nearly singular design |
| 2 | Accurate nearest neighbours with large offsets and limited memory |
| 3 | Interval exclusion with nesting and endpoint rules |
| 4 | Numerical caching, semantic keys and mutable ownership |
| 5 | Streaming windows across chunks and tied timestamps |
| 6 | Covariance aggregation across unequal partitions |
| 7 | Parallel Monte Carlo streams and antithetic standard errors |
| 8 | Shared asynchronous computation under cancellation |
| 9 | Point-in-time reconstruction with revisions and withdrawals |
| 10 | Rolling precision-matrix updates with changing means |

The three advanced cases cover a covariance service, Monte Carlo sensitivities, and event-time features with revisions and crash recovery. The guide also adapts the supplied forecasting challenge to a senior pipeline-design discussion.

## Original source materials

The following files are included unchanged from the supplied originals:

- [Bullet sales CSV](source_materials/bullets_sales.csv)
- [Handgun sales CSV](source_materials/handgun_sales.csv)
- [Original data science challenge](source_materials/Data%20science%20challenge.docx)

The CSVs cover 1810-01-01 through 1816-12-31. Replacement-sales maker/model identifiers are absent, and the guide discusses the implications. The original document is source material; a completed forecast is not part of this repository.

## Run the checks

Verified with Python 3.12.14, NumPy 2.3.5 and pandas 3.0.1.

```console
python -m pip install -r requirements.txt
python interview_checks.py
python advanced_case_checks.py
python case_checks.py --source-dir source_materials
```

The first command after installation executes all ten faulty examples and reference repairs, checks the recorded outputs, and runs numerical and behavioural regressions. It regenerates `question_bank.json` and `verification.txt`.

`advanced_case_checks.py` verifies the advanced case-study numerical illustrations. `case_checks.py` contains the original case reference functions and the source-data audit; it is retained for completeness.

To regenerate the current handouts after changing the question bank or guide source:

```console
python _build_pack.py
```

The builder reads the retained style definition from `baseline_v1/_build_pack.py`; keep that folder in place.

## Earlier version

[baseline_v1](baseline_v1) preserves the original, easier pack and its supporting code. It was superseded after the target level was clarified. The root-level HTML files and question bank are the current materials. `_case_reference.json` and `case_checks.py` at the root are also retained original-case supporting materials.

## Integrity and limitations

- `MANIFEST.sha256` records the packaged file hashes, excluding itself and Git metadata. Regenerating files may change the corresponding hashes.
- `verification.txt` records the current question-check results.
- `UPLOAD_VERIFICATION.txt` records the checks run on the repository upload bundle, including both CSVs.
- Difficulty and timings are proposed calibration values, not validated hiring thresholds. Pilot the selected route with experienced colleagues.
- Passing regression checks does not establish production readiness or benchmark performance.

Prepared 26 October 2026.
