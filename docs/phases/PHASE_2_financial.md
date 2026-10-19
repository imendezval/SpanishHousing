# PHASE 2 — Financial Engine

Implementation guide for an autonomous Codex run. Prepared 7 October 2026.

**Outcome:** a tested, deterministic financial engine that consumes prepared monthly budgets and explicit purchase assumptions, calculates savings and mortgage capacity, and returns the maximum price satisfying both constraints. It runs without market providers, configuration files, geographic lookups or a UI.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), inspected at commit **551cb1715e84ebb50c66b8ecbeac59ac6ef1efe6**. Intended repository location for this guide: **docs/phases/PHASE_2_financial.md**. Inspect the current checkout before implementing; the recorded commit is orientation, not an instruction to reset the repository.

## 0. Start here

1. Inspect the working tree, applicable repository instructions and recent commits. Preserve user changes, including untracked files.
2. Read **docs/PROJECT_BRIEF.md**, **docs/IMPLEMENTATION_PLAN.md**, **docs/ARCHITECTURE.md**, and **docs/progress/PHASE_1.md**. Read the Phase 1 guide selectively when a contract or tooling decision needs context.
3. Inspect **models/base.py**, **models/scenario.py**, **models/results.py**, **models/contracts.py**, the existing tests, **pyproject.toml**, and **scripts/check.sh** under their actual repository paths.
4. If resuming Phase 2, read **docs/progress/PHASE_2.md**, verify its evidence, and continue from the next incomplete milestone.
5. Follow M1–M6 in Section 9. These are verification checkpoints; continue between them without requesting confirmation.
6. Declare completion only against the evidence-backed acceptance criteria in Section 11.

The current user request and applicable repository instructions take precedence. The brief owns product meaning; the implementation plan owns module boundaries; this guide resolves Phase 2 implementation choices and acceptance details. Routine choices are autonomous. Escalate only a genuine blocker or a conflict that materially changes the intended model.

Implement the phase, rather than stopping after a plan or partial scaffolding. Local code, tests, documentation and scoped local commits are authorized. Do not push, merge, deploy, contact providers or purchase data. Do not create an AGENTS.md or a separate agent framework for this task; respect existing applicable instructions. A single Codex workflow is sufficient.

## 1. What Phase 1 actually provides

### 1.1 Existing implementation to build on

| Existing component | Relevant behavior | Phase 2 consequence |
|---|---|---|
| One installable src/spain_housing package | Python 3.12 baseline; uv and uv.lock; Pydantic, PyYAML, Ruff, mypy, pytest and Import Linter | Preserve this setup and dependency direction |
| models/base.py | Frozen records; finite EUR amounts and ratios; first-of-month dates; add_months | Reuse these types and calendar conventions |
| Scenario | Explicit horizon; income/debt paths; saver_ids and borrower_ids; living stages; reserve; mortgage/cost assumptions | Preserve the schema; do not expand scenarios into budgets in this phase |
| LocationPlan | Independent saving/buying bindings; local_local and fixed_saving are representable | Finance must not infer or execute either geographic mode |
| PreparedMonthlyBudget | Dated household net income, rent, nonhousing expenses and other debt, all in EUR/month | This is the savings engine's input boundary |
| SavingsResult | Monthly contributions and balances, ending/usable savings and viability | Populate it with actual calculations |
| PurchaseResult | Two price limits, their minimum, binding constraint and optional target diagnostics | Reuse it, with the small contract refinements in Section 3 |
| PurchaseCostPolicy | costs(price_eur, context) returns separate purchase and mortgage-formalisation costs | Implement the proportional policy against this protocol |
| MarketData and market records | Period/segment-aware access and explicit missing/unsupported status | Leave market access outside finance |
| config.py and CLI | Deterministic YAML/JSON resolution and validate-scenario | Preserve behavior; do not add an evaluation command yet |
| Seven import contracts | Finance cannot depend on markets, ingestion, application, UI, config or CLI | Keep them enforced; do not weaken them to make imports pass |

The finance namespace is currently reserved, not implemented. The existing architecture explicitly assigns income-path expansion, living-stage resolution and market projections to the application/market preparation work in Phase 4.

### 1.2 Verification state and inherited gaps

The committed Phase 1 progress document records incomplete locked installation, Import Linter and wheel checks from its original environment. During this repository inspection, the following succeeded on the recorded commit:

- uv sync --locked.
- bash scripts/check.sh: formatting, lint, strict mypy, all seven import contracts and **46 tests** passed.
- uv build: source distribution and wheel built.
- The wheel installed into a separate environment. Console help and scenario validation worked from /tmp with absolute configuration paths; the imported package came from that environment's site-packages.

These are inspection results, not a replacement for checks in the implementation checkout. M1 must re-establish the baseline and update the stale Phase 1 handoff with actual current evidence. Do not claim a repaired gate merely because this guide says it passed elsewhere. Only change the old incomplete statuses after verifying them.

The data audit still has real coverage, segmentation, identifier and reuse limitations. They affect Phase 3. **They do not block this numerical phase**, which uses explicitly synthetic prepared inputs.

## 2. Scope, ownership and dependencies

### 2.1 Required deliverables

- Monthly savings accumulation with an explainable path, negative contributions, cash-deficit detection and retained reserve.
- Fixed-rate monthly mortgage payments and their inverse maximum-loan calculation.
- Total-debt capacity using borrower income and existing repayments.
- A proportional purchase-cost policy and a common upfront-cash calculation.
- Fixed-financing purchase capacity, including both price limits and their binding constraint.
- Target-price loan, upfront cash, payment and shortfall diagnostics.
- Meaningful numerical, boundary and composition tests; installed-package verification.
- Updated architecture/README guidance and one resumable Phase 2 progress record.

### 2.2 Explicitly deferred

Do not implement:

- Scenario-to-monthly-budget preparation, salary interpolation, participant aggregation or living-stage selection.
- Rent-share application, utility allocation, rental-area conversion, market projection or price-per-m² comparison.
- Real collectors, market repositories, data releases, geometry or expanded source research.
- LocationResult/RunResult production, local/local map evaluation, fixed-saving mode execution or a new evaluate CLI.
- Streamlit, maps, APIs, hosting, Hydra, DVC, databases or provider registries.
- Profession/location salary inference, historical reconstruction, detailed tax tables, variable down-payment optimisation, savings returns or ownership-budget modelling.
- Full mortgage amortisation tables, variable-rate resets, early repayment or bank eligibility assessment.

A staged-rent financial test supplies the already-resolved rent for each month. It does not require a living-stage interpreter. A target financial test supplies an explicit purchase price; deriving it from area and market data belongs to Phase 4.

### 2.3 File ownership

| Path | Responsibility in this phase |
|---|---|
| src/spain_housing/finance/savings.py | Budget sequence validation and savings recurrence |
| src/spain_housing/finance/mortgage.py | Payment, loan and total-debt-capacity formulas |
| src/spain_housing/finance/costs.py | Proportional policy and upfront-cash calculation |
| src/spain_housing/finance/purchase.py | Fixed-financing limits, minimum, binding label and target diagnostics |
| src/spain_housing/models/results.py | Shared result shape and structural validation; no financial implementation |
| src/spain_housing/models/contracts.py | Existing cost protocol/context; change only if genuinely necessary |
| tests/finance/ | Focused numerical and composition tests |
| Existing tests/ | Preserve Phase 1 regression coverage |
| docs/progress/PHASE_2.md | Current execution state, evidence, decisions and next actions |
| README.md, docs/ARCHITECTURE.md | Minimal current API guidance, behavior and handoff updates |

Finance may depend on shared models, the standard library and its own modules. Its internal call direction should remain simple: savings is independent; costs and mortgage are independent; purchase composes costs and mortgage.

Use ordinary typed functions and one small immutable cost-policy implementation. No financial rule belongs in configuration, CLI, UI or a generic utils.py. Do not build a base-class hierarchy, dependency-injection container, calculation graph or plugin system. Add a private helper module only when several implemented functions genuinely share a nontrivial concern.

Retain the current toolchain and dependency lock. Standard-library math and the existing validation/testing tools suffice. No new runtime dependency is needed.

## 3. Contracts and public API

### 3.1 Recommended entry points

Use these names and responsibilities unless an existing implementation in the current checkout already provides a coherent equivalent:

~~~python
# finance/savings.py
simulate_savings(
    monthly_budgets: Sequence[PreparedMonthlyBudget],
    *,
    starting_savings_eur: float,
    retained_reserve_eur: float,
) -> SavingsResult

# finance/mortgage.py
monthly_payment(principal_eur: float, mortgage: MortgageAssumptions) -> float
maximum_loan(monthly_payment_eur: float, mortgage: MortgageAssumptions) -> float
maximum_mortgage_payment(
    net_monthly_income_eur: float,
    other_monthly_debt_eur: float,
    maximum_debt_ratio: float,
) -> float

# finance/costs.py
ProportionalPurchaseCostPolicy(assumptions: PurchaseCostAssumptions)
# Implements costs(price_eur, context) -> PurchaseCostBreakdown.
# Also exposes its baseline upfront_cash_fraction(financed_fraction).

required_upfront_cash(
    price_eur: float,
    *,
    financed_fraction: float,
    cost_policy: PurchaseCostPolicy,
    context: PurchaseContext,
) -> float

# finance/purchase.py
calculate_fixed_financing_capacity(
    *,
    savings_result: SavingsResult,
    borrower_monthly_net_income_eur: float,
    borrower_monthly_other_debt_eur: float,
    mortgage: MortgageAssumptions,
    cost_policy: ProportionalPurchaseCostPolicy,
    purchase_context: PurchaseContext,
    target_price_eur: float | None = None,
) -> PurchaseResult
~~~

These are API specifications, not skeleton bodies to leave in the repository. Implement behavior and document units. Scalar returns are adequate for the three mortgage helpers; do not introduce several near-identical wrappers.

The fixed-financing solver explicitly accepts the implemented proportional policy. The existing costs-only protocol does **not** supply the inverse of an arbitrary cost function. Do not pretend the proportional formula solves nonlinear taxes or fixed fees. Section 12 explains how that later extension stays isolated.

### 3.2 Small necessary result refinements

At the inspected commit, make these focused changes to PurchaseResult:

1. Allow **savings_price_limit_eur: Money | None**. None means the cash constraint is mathematically unbounded, and only that. It never means missing data or failure. Keep the field required; existing finite payloads remain valid.
2. Add **target_loan_eur: Money | None = None**, so a target's financed principal is explicit.
3. Validate target-field coherence: either the target price, loan, upfront cash, payment and both shortfalls are all supplied, or all are None. An absent target does not prevent capacity calculation.

Keep mortgage_price_limit_eur and maximum_price_eur finite, nonnegative numbers. Do not serialize Infinity or an arbitrary huge sentinel. SavingsResult already permits negative closing/ending balances and needs no wholesale redesign.

These output changes are deliberate. Record them in architecture/progress and add round-trip tests, including compatibility with target-free finite Phase 1 payloads. Do not casually change Scenario's schema_version or the shared SchemaVersion alias. Phase 2 does not emit persisted RunResult files; Phase 4 must record the actual financial model version in its run metadata. If the current checkout has persisted target results, inspect their format before tightening validation and document a migration rather than silently rejecting them.

Models own schema/domain validation. Finance owns calculation and operational preconditions. Models must not import finance to recompute results or verify equations.

### 3.3 Boundary behavior

- All money is finite EUR; mortgage rates and debt ratios are decimal fractions. Integer monetary inputs are acceptable where existing numeric conventions allow them; booleans, numeric strings, NaN and infinity are not.
- Starting savings, reserve, monthly budget fields, borrower income/debt, principal and payment capacity are nonnegative. Monthly contributions and closing/ending savings may be negative.
- Use validated assumption/context records. Check public scalar inputs and sequence-level preconditions rather than assuming type annotations enforce them at runtime.
- Do not repeat the entire PreparedMonthlyBudget validator in savings. Check the sequence's order/continuity once in its owning function.
- Invalid input raises a useful ValueError, including Pydantic's validation errors where applicable. A narrowly named ValueError subclass is acceptable if callers need to distinguish an exhausted savings path.
- Expected zero capacity is a valid calculated result. Missing source data is handled upstream and must never become a zero rent, zero price or invented budget here.
- Reject non-finite derived values explicitly. Do not catch arithmetic errors and return a plausible zero.
- Inputs are not mutated. Functions perform no file/network I/O, print no output, and consult no current date, working directory or global scenario state.

## 4. Savings semantics

### 4.1 Prepared-input boundary and calendar

Each PreparedMonthlyBudget already contains the saving household's actual cash amounts:

- net_income_eur: total relevant saving income for that month.
- rent_eur: the household's rent contribution after any sharing.
- nonhousing_expenses_eur: the household's other cash expenses, with utilities allocated upstream.
- other_debt_eur: existing saving-household repayments.

**Do not divide income by 12 or rent by the number of participants here.** Annual-to-monthly income conversion, saver selection and starting-savings aggregation happen once in Phase 4 preparation. Borrower income/debt at purchase are separate inputs to the purchase calculation.

Require a nonempty sequence of consecutive first-of-month dates in ascending order. Reject duplicates, gaps and out-of-order months; do not sort or fill them. In full evaluation it contains exactly N saving months at offsets 0 through N−1. Purchase occurs at offset N, after the last month's contribution. Finance need not receive Scenario to enforce scenario-length alignment; the future caller owns that check.

Accept a Sequence, including an immutable tuple. Use add_months for calendar validation, not fixed 30-day increments. The same function must work across December/January and for historical dates.

### 4.2 Recurrence

For each supplied month:

~~~text
contribution = net_income - rent - nonhousing_expenses - other_debt
closing_savings = previous_savings + contribution
ending_savings = last closing_savings
usable_savings = max(0, ending_savings - retained_reserve)
~~~

starting_savings_eur is the opening balance before the first contribution. Every row records the supplied month, that month's signed contribution, and the closing balance. Do not append a synthetic purchase-month income contribution.

No returns, inflation adjustment or borrowing are implicit. Do not clamp negative monthly contributions, negative balances or ending savings to zero. Use a numerically sensible linear-time accumulation; no quadratic recomputation of every prefix and no premature cents rounding.

The reserve is retained **at purchase**. It is not subtracted every month and is not a separate monthly expense. A reserve larger than ending savings gives zero usable savings. Falling below the reserve during saving is not, by itself, cash exhaustion.

### 4.3 Cash exhaustion

- Set viability to funds_exhausted if any closing balance is materially below zero.
- An exactly zero balance is viable in this monthly model if the required expenses were covered.
- Document one small absolute rounding epsilon, recommended **1e−8 EUR**, for detecting an accidental floating-point negative near zero. Keep reported balances unchanged; the epsilon does not authorize borrowing.
- Once a genuine deficit occurs, viability remains funds_exhausted even if later income restores a positive final balance.
- Continue the diagnostic recurrence through the full sequence; do not stop at the first negative row or assume a loan financing that deficit.
- Calculate ending/usable savings arithmetically even for an exhausted path, but prevent it from being passed off as feasible buying capacity.

The public purchase-capacity function must reject a SavingsResult marked funds_exhausted. Phase 4 will translate that into LocationResult's unviable status. Do not implement that location evaluator now, and do not manufacture a PurchaseResult with ordinary affordability for a recovered-but-exhausted path.

## 5. Mortgage calculations

### 5.1 Units and debt capacity

Let Y be net **monthly** income of the actual borrowers at purchase, D their other monthly debt repayments, d the configured maximum total-debt ratio:

~~~text
maximum_mortgage_payment = max(0, d × Y - D)
~~~

The baseline d is 0.35, but finance uses the supplied assumption. Existing debts consume that allowance. Do not calculate 35% of income and then ignore debts.

Inputs are already prepared for the purchase month. They may differ from the saving household's income and debt. A roommate's income is not automatically mortgage income; a savings contributor need not be a borrower. Income reached after purchase must not be used prematurely. These selections belong upstream; finance must not inspect participant IDs or interpolate salary milestones.

### 5.2 Fixed-rate annuity

For annual nominal interest a and mortgage term T years:

~~~text
r = a / 12
n = 12 × T

annuity_factor = (1 - (1 + r)^(-n)) / r    if r > 0
annuity_factor = n                        if r = 0

monthly_payment(L) = L / annuity_factor
maximum_loan(M) = M × annuity_factor
~~~

Use the contractual nominal rate, not TAE/APR including fees. The first payment is one month after origination; payments are monthly and level while the assumed rate remains fixed. All calculations are in nominal euros.

Own the annuity factor once in mortgage.py and use it for both directions. For small positive rates, prefer the stable equivalent:

~~~python
-math.expm1(-n * math.log1p(r)) / r
~~~

Handle a zero monthly rate explicitly, including a representational underflow to zero for an exceptionally tiny valid annual rate. Do not add an arbitrary economic threshold that rounds an ordinary positive rate to zero. Do not calculate a large positive power of 1+r.

Zero principal gives zero payment; zero payment capacity gives zero loan. Terms must be positive integers and interest nonnegative, as established by MortgageAssumptions. Reject non-finite outputs from extreme inputs rather than inventing limits. No arbitrary bank age/term caps are introduced here.

## 6. Purchase costs and the fixed-financing solver

### 6.1 Proportional cost policy

Construct the immutable ProportionalPurchaseCostPolicy from the existing validated PurchaseCostAssumptions. It implements PurchaseCostPolicy:

~~~text
purchase_cost_eur = allowance_fraction × price_eur
mortgage_formalisation_cost_eur = 0
~~~

The current global allowance uses the supplied fraction c, normally 0.10 from defaults. It is a simplified purchase-cost allowance, not a universal tax rate. Do not add another 10% in the solver or include loan interest in upfront cash.

The protocol's context contains destination, purchase month and target-property characteristics. The baseline policy accepts this context without inferring location-specific rules. Later policies can use it.

The common required_upfront_cash helper accepts a PurchaseCostPolicy and adds:

~~~text
down_payment = (1 - financed_fraction) × price
upfront_cash = down_payment
             + purchase_cost_eur
             + mortgage_formalisation_cost_eur
~~~

Both cost components are included once when supplied. Test the helper with a small explicit alternative policy returning distinct components; this proves the existing boundary without implementing real taxes.

For the proportional solver, the policy exposes its known upfront fraction:

~~~text
k = (1 - f) + c
~~~

Keep cost arithmetic owned by costs.py. Do not infer an arbitrary policy's fraction by quoting it at a €1 property, inspecting private attributes or sampling two prices. Do not introduce a generic root solver for this phase.

### 6.2 Two limits and their intersection

For usable savings S, fixed financed fraction f and the policy's upfront fraction k:

~~~text
P_savings = S / k                  when k > 0
P_savings = unbounded              when k = 0

M_max = max(0, d × Y_buy - D_buy)
L_max = maximum_loan(M_max)
P_mortgage = L_max / f

P_max = min(P_savings, P_mortgage)
~~~

For an unbounded savings limit, P_max equals P_mortgage. Otherwise calculate the actual minimum of the two finite limits. **Never take their maximum, add them, average them, or silently change the financing fraction.**

The current Scenario allows 0 < f ≤ 1 and c ≥ 0. Therefore f=1, c=0 is a valid boundary case: no upfront cash is required by these assumptions, even with zero savings. Return savings_price_limit_eur=None to represent unbounded, with a finite mortgage limit and maximum price. Do not reject an otherwise valid Scenario merely to avoid this case.

The baseline is explicitly fixed financing. A buyer with surplus savings still finances f of the price; using a smaller loan to increase P_max is a later solver extension.

### 6.3 Binding constraint

- A lower finite savings limit means savings binds.
- A lower mortgage limit means mortgage binds.
- Finite limits equal within **€0.01 absolute tolerance** mean both bind.
- An unbounded savings limit means mortgage binds, including when mortgage capacity is zero.

The tolerance changes only the explanation. P_max remains the actual minimum; do not increase it to match the larger limit. A viable scenario with both finite limits zero has binding_constraint=both.

Return the existing price-limit/result fields. Zero capacity is valid. There is no need to fabricate a target or dataset identifier to calculate a purchasing budget.

## 7. Target-property diagnostics

The caller may supply a finite positive target_price_eur, already resolved for the purchase destination and date. It may be above, below or equal to P_max.

~~~text
target_loan = f × target_price
target_upfront_cash = required_upfront_cash(target_price, ...)
target_monthly_payment = monthly_payment(target_loan, mortgage)
target_cash_shortfall = max(0, target_upfront_cash - usable_savings)
target_payment_shortfall = max(0, target_monthly_payment - M_max)
~~~

Call the common costs and mortgage functions. Do not copy their formulas into purchase.py, tests' actual calculations, the CLI or output model validators.

Compute diagnostics even when the target is unaffordable. Both shortfalls can be positive independently. If there is no target, all target fields, including target_loan_eur, are None. Do not convert an absent target to a zero-price home.

This phase estimates the two agreed constraints. It does not simulate post-purchase ownership spending or certify bank approval. Keep richer household-budget checks at their later explicit boundary rather than silently adding a third cap now.

## 8. Verification cases and independent numerical evidence

All amounts below are deliberately synthetic. Use these as independent expected values, not as real Spanish market observations.

### 8.1 Monthly path with staged rent

Opening savings €10,000; reserve €2,000. Six months starting October 2026. In each month income is €2,000, nonhousing expenses €600 and existing debt €100:

| Month | Prepared rent | Contribution | Closing savings |
|---|---:|---:|---:|
| 2026-10 | 400 | 900 | 10,900 |
| 2026-11 | 400 | 900 | 11,800 |
| 2026-12 | 700 | 600 | 12,400 |
| 2027-01 | 700 | 600 | 13,000 |
| 2027-02 | 500 | 800 | 13,800 |
| 2027-03 | 500 | 800 | 14,600 |

Expected ending savings: €14,600. Usable savings: €12,600. Viability: viable. A future six-month scenario purchases in April 2027, without a seventh saving contribution.

Additional savings cases:

- Starting €1,000; contributions −€600 then +€800: balances €400 and €1,200, viable.
- Starting €100; contributions −€200 then +€300: balances −€100 and €200, funds_exhausted despite recovery.
- Reserve greater than a positive ending balance: usable savings zero, without changing ending savings.
- An exactly zero closing balance, no mutation, one month, year boundaries, and duplicate/gapped/reversed dates.

### 8.2 Hand-checkable zero-interest capacity cases

Use f=0.80, c=0.10, d=0.35 and 25 years at zero interest. Then n=300 and every €1/month supports €300 of loan principal.

| Case | Usable savings S | Borrower income/month | Other debt/month | P_savings | P_mortgage | P_max / binding |
|---|---:|---:|---:|---:|---:|---|
| Savings limited | 60,000 | 3,000 | 0 | 200,000 | 393,750 | 200,000 / savings |
| Mortgage limited | 90,000 | 2,000 | 0 | 300,000 | 262,500 | 262,500 / mortgage |
| Both bind | 78,750 | 2,000 | 0 | 262,500 | 262,500 | 262,500 / both |
| Existing debt | 90,000 | 2,000 | 100 | 300,000 | 225,000 | 225,000 / mortgage |
| No payment capacity | 60,000 | 2,000 | 700 | 200,000 | 0 | 0 / mortgage |
| Staged-rent savings above | 12,600 | 2,000 | 100 | 42,000 | 225,000 | 42,000 / savings |

Target examples:

- Savings-limited case, target €250,000: loan €200,000; upfront cash €75,000; monthly payment €666.666666…; cash shortfall €15,000; payment shortfall zero.
- Mortgage-limited case, target €300,000: loan €240,000; upfront cash €90,000; monthly payment €800; cash shortfall zero; payment shortfall €100.

Also test zero income, zero usable savings, both zero limits, non-default f/c/d/term, and f=1,c=0 with its unbounded cash limit.

### 8.3 Positive-rate reference

For a €200,000 principal, a=0.035 and 25 years:

- Monthly payment ≈ **€1,001.247140518986**.
- Maximum loan at €700/month ≈ **€139,825.61780644136**.
- At f=0.80, that loan supports P_mortgage ≈ **€174,782.0222580517**.

These references were calculated independently with high-precision Decimal arithmetic. Store literal expected values in tests. Use sensible tolerances, for example relative 1e−10 and absolute 1e−7 EUR for ordinary reference comparisons. Do not weaken tolerances until a broken formula passes.

Test exact zero and small positive interest, such as 1e−12 annual, to expose cancellation errors. Round-trip payment/loan checks help but are insufficient by themselves: two inverse functions can share the same mistake.

### 8.4 Invariants and composition

Use a small deterministic parameter grid; no property-testing dependency is required:

- For positive rates, maximum_loan(monthly_payment(L)) approximately recovers L.
- With other inputs fixed, more usable savings/income cannot reduce capacity; more other debt/cost allowance/interest cannot increase it.
- A longer term cannot reduce maximum loan at the same payment.
- At P_max, upfront cash and mortgage payment satisfy their respective caps within numerical tolerance.
- Above a finite binding limit by a meaningful amount, its corresponding constraint fails.
- target_payment_shortfall uses capacity after existing debts.
- Input permutation is not accepted as a substitute for chronological validation.
- Identical financial inputs produce identical baseline results under different PurchaseContext locations/dates; the engine does not fetch local data.
- A recovered-but-exhausted SavingsResult is rejected by the public capacity function.
- Results serialize as ordinary JSON and round-trip, including unbounded savings and absent/present targets.

At least one composition test must call the actual savings function, cost policy and purchase function together with prepared budgets. Demonstrate separate saving-household and borrower inputs: two savers can fund cash while only one borrower's explicitly supplied income supports the mortgage. Do not write a participant selector in production finance to create this test.

## 9. Autonomous work loop and milestones

### 9.1 Persistent state and recovery

Use **docs/progress/PHASE_2.md** as the single current execution record. Keep it concise:

- Current milestone and M1–M6 statuses.
- Acceptance IDs with evidence, not only checkmarks.
- Last verified checkpoint commit and exact executed check commands/results.
- Material API/contract/numerical decisions and short reasons.
- Outstanding failures, blockers and the next concrete actions.

Do not maintain several competing status files or append full terminal logs. The guide states requirements; the progress file states what actually happened. This phase does not require another AGENTS.md, JSON task registry or long-running agent service.

For each coherent slice: inspect → implement → run focused checks → repair → review the diff → checkpoint → update progress → continue. Do not defer known failures to M6 or stop after a successful unit-test subset.

On resume, read progress and Git history, inspect the worktree and verify the last checkpoint. Run checks affected by any unverified changes before building on them. Context compaction or a session restart does not make previously unverified claims true.

Make scoped local commits when Git identity and repository policy permit. Stage only task-owned changes. Never reset, discard, stash automatically, commit unrelated work or invent an identity. If commits are unavailable, leave reviewable changes and record that limitation.

If tooling or package access blocks verification, record the exact limitation and continue independent work; do not retry indefinitely, rewrite the package architecture or use unlocked substitutes as proof of the locked gate. Report completion as blocked until required checks can actually run.

### 9.2 M1 — Re-establish foundation and settle contracts

**Implement:** inspect current code and instructions; run the locked baseline; repair necessary pre-existing integration failures in a scoped way; reconcile Phase 1's stale verification state; create Phase 2 progress; implement/document the minimal PurchaseResult refinements.

**Verify:** existing suite and import contracts pass; result round trips preserve target-free finite payloads; unbounded/target-coherence cases are covered; no changes to Scenario semantics, defaults or dependency direction.

**Checkpoint:** clear baseline evidence and an agreed executable contract. Source-access questions are carried forward to Phase 3, not reopened as a prerequisite.

### 9.3 M2 — Savings engine

**Implement:** simulate_savings against prepared budgets; chronological validation; signed recurrence; reserve handling; persistent exhaustion status.

**Verify:** the complete six-month reference path, negative-but-funded months, recovered deficit, zero/end-reserve cases and invalid ordering; input immutability.

**Checkpoint:** actual SavingsResult values are explained by independent arithmetic. No path interpolation or market logic has entered finance.

### 9.4 M3 — Mortgage engine

**Implement:** one annuity factor, payment, inverse loan and total-debt capacity.

**Verify:** zero-rate hand cases, positive-rate literals, small-rate stability, zero capacity and invalid scalar input; a deterministic monotonicity/round-trip grid.

**Checkpoint:** units and repayment timing are documented; both directions share the same numerical owner.

### 9.5 M4 — Costs and purchasing capacity

**Implement:** proportional policy, common upfront-cash helper, fixed-financing limits, unbounded-cash representation, actual minimum and binding explanation; reject exhausted savings.

**Verify:** all capacity table cases, generic helper inclusion of both cost components, non-default assumptions, near-equal labels and f=1,c=0. Verify feasibility at the returned price.

**Checkpoint:** capacity works without a target and without any configuration or provider access.

### 9.6 M5 — Target diagnostics and composed workflow

**Implement:** target principal, cash, payment and both shortfalls; absent-target semantics; one complete prepared-budget-to-purchase composition; concise callable API example.

**Verify:** both target references, both simultaneous shortfalls, a below-limit target, no-target output, JSON round trips, separately supplied borrower income/debt and exhausted-path refusal.

**Checkpoint:** the installed Python API can explain a financial result without a map, real prices or an evaluation CLI.

### 9.7 M6 — Full gate, wheel, review and handoff

**Implement:** any remaining fixes; update README/architecture/progress; link this phase guide from the existing documentation map where appropriate.

**Verify:** full quality gate, build, isolated wheel smoke including financial API, all acceptance criteria; review ownership and duplication.

**Checkpoint:** final status is complete only with evidence. Hand off prepared-input expectations to Phase 4 and retain Phase 3's independent data work.

## 10. Verification commands and code review

### 10.1 Reuse the current gate

From the repository root:

~~~bash
uv sync --locked
bash scripts/check.sh
uv build
~~~

The existing check script owns:

~~~bash
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src/spain_housing
uv run --locked lint-imports
uv run --locked pytest
~~~

Do not create another conflicting full-check script. Focused development checks can use uv run --locked pytest tests/finance after that directory exists. The final gate runs the **whole suite**, including the installed CLI and import-linter sensitivity test.

Tests must be offline and deterministic. Preserve their actual behavior rather than replacing meaningful assertions with mocks or broad exception checks. No blanket skips, new broad type ignores or weakened import contracts.

### 10.2 Built-wheel smoke

Use a fresh environment and a working directory outside the source repository. Adapt the wheel filename to the actual build; do not alter the package version merely to match this example:

~~~bash
repo_dir="$(pwd)"
wheel_path="$repo_dir/dist/spain_housing-0.1.0-py3-none-any.whl"
wheel_env_dir="$(mktemp -d)"
uv venv "$wheel_env_dir" --python 3.12
uv pip install --python "$wheel_env_dir/bin/python" "$wheel_path"
(
    cd /tmp
    "$wheel_env_dir/bin/spain-housing" --help
    "$wheel_env_dir/bin/spain-housing" validate-scenario \
        --defaults "$repo_dir/configs/defaults.yaml" \
        --scenario "$repo_dir/configs/scenarios/room_only.yaml" --json
)
~~~

Then run the documented financial API example using that environment's Python from outside the repository. It must call simulate_savings and calculate_fixed_financing_capacity and check a literal expected result, such as the zero-interest savings-limited €200,000 case. Confirm the imported package comes from the wheel environment, without PYTHONPATH or an editable source install.

A successful editable import or source-tree test is not evidence that the wheel includes the new modules. Record both types of verification distinctly.

### 10.3 Final review questions

- Is each formula owned once and reused by target diagnostics?
- Do results retain raw precision, signed deficits and meaningful zeros?
- Is an exhausted path distinguishable from a viable zero-capacity case?
- Are input units clear, with no annual/monthly or saver/borrower confusion?
- Does the cost implementation respect the existing protocol without claiming unsupported inversion?
- Is finance independent of files, source schemas, geography selection and the UI?
- Have targeted model changes been documented and compatibility checked?
- Have future features remained future work?

No fixed file-length quota, generic framework or duplicated validation layer is required to demonstrate clean code. Favor focused functions, concrete names, narrow errors, immutable inputs and tests that check economic behavior.

## 11. Acceptance criteria and final report

IDs below belong to Phase 2. Track them in docs/progress/PHASE_2.md.

| ID | Complete when |
|---|---|
| A1 | Current locked Phase 1 baseline is verified, necessary failures are repaired, and stale handoff claims are reconciled with actual evidence |
| A2 | Savings returns the correct monthly path, signed balances, reserve-adjusted usable savings and persistent cash-exhaustion status |
| A3 | Payment, maximum loan and debt capacity match zero/positive/small-rate references, with finite outputs and explicit units |
| A4 | Proportional costs implement the existing protocol; common upfront cash includes each supplied component once |
| A5 | Fixed-financing capacity returns both limits, their actual minimum and binding label, including zero and unbounded-cash cases |
| A6 | Target principal, cash, payment and both shortfalls are correct; absent targets remain consistently absent |
| A7 | Public boundary errors are useful; invalid sequences/scalars are rejected; exhausted savings cannot become an ordinary feasible purchase result |
| A8 | Independent reference, invariant, serialization and composed-workflow tests pass, including separate saving and borrower inputs |
| A9 | Full locked gate, unchanged dependency boundaries, package build and outside-repository wheel financial/CLI smoke pass |
| A10 | Code ownership, minimal contract changes, API example, progress evidence and Phase 3/4 handoff are documented; own changes are reviewable and checkpointed where possible |

Do not mark an acceptance item complete because files exist or a related unit test passed. A required skipped/unavailable check is incomplete. Do not report Phase 3 data access as a financial-engine failure, or report a financial-engine gate failure as an irrelevant data limitation.

Final report:

- Overall complete/blocked status, with incomplete acceptance IDs if any.
- Important implemented APIs and contract changes.
- Executed checks and actual results, including the wheel smoke.
- Scoped checkpoint commits, if available.
- Remaining limitations and the next concrete handoff.

Keep the report concise. Do not imply that market evaluation, maps or later features were implemented.

## 12. Extension requirements and handoff

**The pipeline must remain modular enough that these additions do not require substantial repository restructuring. Prepare through explicit inputs and ownership; do not implement speculative machinery now.**

| Future work | Preserved boundary and expected extension |
|---|---|
| Save/rent in A, buy in B — essential next geographic extension | SavingsResult is independent of destination and can be reused. Purchase gets destination context separately. Mode selection/caching belongs in application, without new savings or mortgage formulas |
| Salary realism by profession/location | Employment data produces/contextualizes income upstream. Finance continues to consume explicit monthly borrower/saver amounts; no job-probability assumptions enter numerical rules |
| Historical scenarios, e.g. save from 2010 and buy in 2017 — last major extension | Explicit monthly dates, prepared cash flows and purchase context support historical inputs. Data selection/boundary reconciliation stays outside finance; no implicit latest/today lookup |
| More precise regional/property/buyer costs | Implement another PurchaseCostPolicy and extend/replace the cash-price-limit solver in finance/purchase.py. The costs-only protocol is retained; nonlinear inversion must be implemented explicitly. Do not spread tax branches across application or UI |
| Larger down payments / variable financing | Add a dedicated purchase-solver alternative that jointly respects cash and loan constraints. Reuse savings, costs and mortgage helpers; preserve the fixed-fraction baseline's behavior |
| Savings returns | Extend savings through explicit rate/timing assumptions. Preserve prepared-budget input and explainable monthly balances; no silent return assumption now |
| Richer ownership-budget checks | Add explicit prepared ownership costs and a separately explained check. Do not silently reinterpret the present two-bottleneck result |

Phase 3 remains independently responsible for the pilot snapshot, provenance and access/coverage issues. Phase 4 will:

1. Expand annual net income paths to monthly amounts, with purchase income sampled at offset N.
2. Select saver/borrower sets separately and aggregate initial savings and expenses once.
3. Resolve living stages, rent shares, utility treatment and market projections into exactly N PreparedMonthlyBudget records.
4. Call this engine; translate exhaustion into unviable status.
5. Resolve purchase-date target prices and compute market indicators, LocationResult and RunResult metadata.

Do not duplicate any Phase 2 equation when that assembly work begins.

## 13. Research basis

The workflow requirements apply the previous research to this repository. They are engineering guidance, not a guarantee that an autonomous agent will succeed.

- [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 26 November 2025: incremental changes, persistent state and tested checkpoints. Applied through a single progress file, scoped commits, resume checks and evidence-backed acceptance.
- [OpenAI — Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), 23 February 2026: scoped milestones, validation/repair and an inspectable execution record. Applied through M1–M6; checkpoints do not require repeated user permission.
- [OpenAI — Harness engineering](https://openai.com/index/harness-engineering/), 11 February 2026: repository-visible knowledge and enforceable boundaries. Applied by preserving the existing documentation map and Import Linter contracts, rather than adding another instruction hierarchy.
- [Banco de España — Cuota hipotecaria](https://clientebancario.bde.es/pcb/es/menu-horizontal/productosservici/financiacion/hipotecas/guia-textual/primerospasoscon/Cuota_hipotecaria.html) and [mortgage/personal-loan simulator assumptions](https://clientebancario.bde.es/pcb/es/menu-horizontal/podemosayudarte/simuladores/simulador_prestamo_hipotecario_personal.html): level monthly payments under the French amortisation system while the rate remains fixed.
- [Banco de España — Mortgage TAE simulator assumptions](https://clientebancario.bde.es/pcb/es/menu-horizontal/podemosayudarte/simuladores/calculo-de-la-tae-de-un-prestamo-hipotecario.html): distinguishes the nominal interest used in monthly interest calculations from total-cost comparisons.
- [Banco de España — First-mortgage guidance](https://clientebancario.bde.es/pcb/es/blog/consejos-para-firmar-tu-primera-hipoteca.html): existing debt matters when assessing the income burden. The project's 35%, 80%, 25-year and 10% assumptions remain configurable model choices, not universal underwriting or tax rules.
- [Python 3.12 math documentation](https://docs.python.org/3.12/library/math.html): log1p/expm1 provide numerically stable elementary calculations; fsum supports accurate summation.

The financial references validate conventions. The exact product scope, fixed-financing baseline, reserve semantics and result behavior remain the project's documented decisions.
