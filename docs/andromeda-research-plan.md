# Andromeda: How Certain Is Our Galactic Future?

## Research Charter

- **Created:** 2026-10-28. **Revised:** 2026-10-28, reorganized around a pre-Gaia DR4 forecast and three story acts.
- **Status:** Research plan; no new simulations or findings yet.
- **Destination:** Deep Research in the Deep Space Portal, after scientific validation.
- **Starting material:** [Andromeda notes and documentary excerpts](../PDSL_Ideation/Andromeda/Andromeda.docx) and the accompanying reference images.
- **Primary question:** Which conclusions about the Milky Way-Andromeda encounter survive plausible changes in astrometry and dark-matter halo assumptions?
- **Headline contribution:** A dated, reproducible forecast published before Gaia Data Release 4 (DR4), stating in advance which new measurements would raise, lower, or leave unchanged the merger probability, then updated openly against that statement.
- **Companion question:** At each plausible encounter epoch, what state would the Sun, surviving planets, and their galactic environment already occupy?
- **Approach:** Reproduce published results, commit the forecast before DR4, explain why published forecasts differ, and update when DR4-based measurements appear. Build the public experience from validated outputs.

The project covers nine topics in three acts, delivered through five stages. Coverage does not mean building nine new simulation engines: some topics warrant numerical analysis, others a transparent calculation or critical literature synthesis.

The pre-DR4 forecast applies published methods transparently. Its value is the advance commitment and the open update, not a new astrophysical model. Any further original contribution is a possibility to investigate, not a claim established by this plan.

## The Story We Are Telling

Science decides the content; the story decides the order. Every beat is anchored to a source or a planned calculation and must pass the evidence ledger before it reaches the public page.

| Beat | Story | Scientific anchor |
|------|-------|-------------------|
| 1 | **The blueshift is mostly us.** Andromeda approaches the Sun at about 300 km/s, but most of that is the Sun's own orbit around the Milky Way. Galaxy to galaxy, the approach is about 110 km/s. | Frame correction in Topic 1; values as quoted in [R3] |
| 2 | **The sideways motion decides everything.** The line-of-sight velocity shows Andromeda is approaching, not whether it hits. The answer is hidden in a proper motion of tens of microarcseconds per year. | Astrometric scale equation; Topic 1 |
| 3 | **Same framework, one key input, opposite headlines.** In 2025 the forecast read "coin flip". In 2026, largely the same framework with updated proper motions read "likely". | [R2], [R3]; reconciliation in Topic 3 |
| 4 | **Our next galactic collision isn't Andromeda.** The Large Magellanic Cloud merges with the Milky Way first, after a median of about 1.3 Gyr in recent semi-analytic models. | [R2], [R3], [R11]; Topic 2 |
| 5 | **Three clocks.** Earth's biosphere, the Sun, and the galaxies run on different timelines. Surface habitability is expected to end long before any Andromeda encounter, and the Sun ends as a white dwarf, not a neutron star. | [R7], [R8]; habitability source pending; Topic 5 |
| 6 | **A forecast with a date on it.** Before DR4 we publish what we expect and what would change our mind. Afterwards, we show the update. | Headline milestone; Stage 5 |

**Leadership insight:** Two capable teams, largely the same framework, and essentially one changed input reversed the headline. Know which input your decision is most sensitive to, and say in advance what evidence would change your mind. Present this reflection separately from the scientific evidence.

## Headline Milestone: A Forecast Before Gaia DR4

ESA lists Gaia DR4, based on 66 months of data, for **2 December 2026** [R15]. Andromeda's transverse motion is the input to which published forecasts are most sensitive [R3], which makes DR4 a natural, dated test.

**Publish by 1 December 2026** as a tagged, public commit with a short research note:

1. Reproduced merger statistics for the [R3] fiducial configuration and, if reproduced in time, the [R2] fiducial configuration, each with model, horizon, and sampling uncertainty.
2. A conditional merger-probability map across the M31 proper-motion plane, reproducing the approach of [R3], with current measurements marked.
3. Pre-stated regions where a new central value would raise, lower, or leave the probability materially unchanged, using a threshold fixed before DR4.
4. The decision rule: substitute newly published M31 proper motions (and, separately, M33) with their uncertainties into the frozen configuration, change nothing else in the first update, and report the result beside the pre-DR4 forecast. Model improvements are separate, labelled updates.
5. The frozen code commit, environment, seeds, parameter files, and figures.

**Cautions:**

- DR4 will not publish an Andromeda proper motion directly. Deriving one requires careful source selection and control of astrometric systematics [R4]; credible DR4-based values may take weeks to months. The update waits for them.
- Deriving our own DR4 proper motion for M31 is a later stretch goal, not part of this milestone.
- A proper-motion-plane map already exists in [R3]. Our contribution is the advance commitment, open reproducibility, and the public update, and the note must say so.
- If reproduction misses the Stage 1 tolerance by the deadline, publish the decision rule and a reproduction-in-progress note instead of unvalidated numbers.

## Starting Point

Start by reproducing the [R3] baseline from the public [R10] notebook. Do not start with a collision animation or a countdown.

Before 1 December 2026:

1. Freeze the parameter table for [R2] and [R3]: inputs, units, frames, and distributions.
2. Reproduce one published baseline and its separation-versus-time ensemble figure.
3. Write a short validation report covering agreement, discrepancies, and limitations.
4. Publish the pre-DR4 forecast.

The full evidence ledger, the consequence topics, and the stress tests continue after the forecast is frozen. A reproduced figure is a replication result, not a new prediction.

## Scientific Baseline

| Source | Result to investigate | Interpretation constraint |
|--------|-----------------------|---------------------------|
| van der Marel et al. (2012), [R1] | First pericentre around 3.9 Gyr and merger around 5.9 Gyr under their inputs | Historical benchmark, not an unconditional present-day forecast |
| Sawala et al. (2025), [R2] | Approximately half of sampled systems merge within 10 Gyr | Conditional on their input distributions, model, and merger criterion |
| Wu et al. (March 2026), [R3] | Fiducial merger fraction of 90%; median merger time of about 6.5 Gyr among merging cases | Updated proper motions change the result; significant sensitivity remains |
| Wu et al. (September 2026), [R5] | M31 mass inference depends on halo profile and velocity anisotropy | Candidate input for a controlled extension, not a replacement mass to insert without checking definitions |
| [R2] and [R3] | The LMC merges with the Milky Way before any MW-M31 encounter; median about 1.3 Gyr with a 20 kpc criterion ([R2] reports 1.9 Gyr with 10 kpc) | Depends on the merger criterion and the LMC's mass; compare with the dedicated model in [R11] |

The 2026 arXiv records list [R3] as accepted by Astrophysical Journal Letters and [R5] as accepted by Astrophysical Journal. Refresh publication metadata before release. The accessible 2024 preprint and public notebook associated with [R2] must be compared with the final 2025 publication before assigning reproduction targets.

Do not average the 50% and 90% results. They describe different conditional ensembles. Likewise, the 64.7%-100% variation across the proper-motion region discussed in [R3] is a sensitivity range, not automatically a confidence interval on one inferred probability.

## Act I: Will It Happen?

Topics 1-3 form the quantitative core and feed the pre-DR4 forecast.

### Topic 1: Will the Galaxies Merge?

**Question:** What do observations establish, and what remains conditional on the adopted model?

**Work:** Trace the forecast from [R1] through [R2]-[R4]. Record radial velocities, both proper-motion components, distances, coordinate conventions, statistical errors, systematic errors, and available covariances. Explain why approaching does not imply a direct hit or a merger within a chosen horizon. Open the public explanation with the frame correction: about -300 km/s heliocentric versus about -110 km/s Galactocentric radial velocity [R3].

**Method:** Published measurements first; Monte Carlo propagation through an established semi-analytic framework. Do not initially reprocess the full Gaia catalogue.

**Deliverable:** Evidence timeline, blueshift frame-correction explainer, baseline orbit ensemble, and distributions of first-pericentre time, first-pericentre distance, and merger time.

**Boundary:** No merger within 10 Gyr is not equivalent to no merger ever. Report merger-time distributions conditional on merging, alongside the unconditional fraction that has merged by each time.

### Topic 2: Smaller Galaxies, and Our First Collision

**Question:** Why can the Large Magellanic Cloud (LMC) and Triangulum (M33) change the outcome, why can the apparent direction of their effect reverse, and when does the LMC itself merge with the Milky Way?

**Work:** Compare MW-M31, MW-M31-M33, MW-M31-LMC, and the full four-body system with matched samples of shared inputs. Track relative velocity, angular momentum, and orbital geometry. Report the LMC-Milky Way merger, which precedes any MW-M31 encounter in [R2]-[R3], as a result in its own right and compare it with [R11].

**Method:** Reproduce the satellite comparisons in [R2] and [R3], distinguishing direct gravity from the host's motion induced by its satellite. Use [R6] for the M31-M33 context.

**Deliverable:** Controlled satellite-inclusion comparison, annotated orbital-plane diagrams, and the LMC merger-time distribution for the "next collision" story.

**Boundary:** The LMC does not universally prevent or promote merging. Satellite omission is a model comparison, not a physically observed alternative universe. Document mass accounting so satellite mass is not counted twice. Quote LMC merger times with their merger criterion and adopted LMC mass.

### Topic 3: Dark Matter and Forecast Robustness

**Question:** How much of the forecast depends on the assumed halo structure and mass distribution rather than astrometric precision alone?

**Work:** Begin with the published NFW-based configurations. Audit mass definitions, concentrations, prior truncation, and dynamical-friction prescriptions. Evaluate [R5] for an extension using consistently defined mass and structural constraints.

**Method:** Separate changes to mass distributions within the baseline model from genuine changes of density profile. For alternative profiles, update the density, potential, and friction inputs consistently; do not relabel an NFW calculation as an Einasto calculation.

**Deliverable:** Robustness matrix showing which conclusions survive alternative supported assumptions, with numerical and observational uncertainty reported separately.

**Boundary:** Preserve joint mass-concentration-anisotropy constraints where available. Do not combine incompatible estimates or assume equal credibility for every profile. This is not a test of dark matter's existence.

## Act II: What Would It Mean?

Act II turns orbits into consequences. Topic 5 is the centrepiece; Topics 6 and 7 are concise explainers.

### Topic 4: A Collision Without Frequent Stellar Impacts

**Question:** What physically interacts when galaxies pass through one another?

**Work:** Distinguish stellar impacts, gravitational tides, orbital redistribution, halo-mediated energy transfer, and gas shocks. Explain dynamical friction and why a point-mass flyby is not a self-consistent merger model.

**Method:** Literature synthesis plus order-of-magnitude stellar encounter calculations. Use published simulations for tidal structures and gas response. Source a dedicated gas/star-formation study during Stage 3 before making quantitative starburst claims.

**Deliverable:** A scale comparison and a mechanism diagram separating stars, gas, and dark matter.

**Boundary:** A low impact probability for an individual star is not a proof of zero impacts throughout two galaxies. Future gas supply is uncertain; a spectacular starburst is not guaranteed. Four halo-centre trajectories cannot predict stellar migration or star formation.

### Topic 5: Three Clocks: Earth, the Sun, and the Galaxies

**Question:** Which comes first: the end of Earth's surface habitability, the Sun's transformation, or a galactic encounter? What changes locally before, during, and after a possible encounter?

**Work:** Keep three clocks separate: Earth's surface habitability, solar and planetary evolution, and galactic encounters. Track main-sequence evolution, giant phases, mass loss, and the white-dwarf endpoint using published solar-calibrated models [R7]-[R8]. Add a dedicated modern climate/habitability source before assigning a numerical habitability deadline.

**Method:** Overlay encounter-time ensembles, including the LMC merger, on selected solar-evolution tracks. Use slow isotropic mass loss as an illustrative planetary-orbit calculation, not as a substitute for tides and engulfment modelling.

**Deliverable:** The three-clock timeline, the central storytelling figure of this research, and, where inputs support it, the conditional fraction of encounter realizations occurring during each solar phase.

**Boundary:** The Sun is not expected to become a neutron star. Main-sequence departure, red-giant maximum radius, and white-dwarf formation are distinct events. Do not assume a white dwarf at 4.5 or 6.5 Gyr from now: [R7], for example, places the red-giant-branch tip about 7.59 Gyr from now in its model. Determine phase from the chosen track. Habitability, physical survival, and gravitational binding are different outcomes.

### Topic 6 (Explainer): Our Place in the Galaxy and the Future Sky

**Question:** How could the Solar System's galactic location and the apparent sky change across plausible outcomes?

**Work:** Separate a changed orbit around the galaxy from changed planetary orbits around the Sun. Examine the solar-analogue results in [R1] with their original assumptions. Begin visual calculations with angular size along validated trajectories.

**Method:** Geometric illustrations first. Quantitative solar migration requires appropriate stellar tracer or N-body simulations; the four-body baseline does not provide it. Brightness predictions additionally require stellar-population, dust, and viewing models.

**Deliverable:** Scenario-labelled angular-size curves and optional future-sky illustrations with explicit observer and brightness assumptions.

**Boundary:** Never present a hypothetical viewpoint as a surviving observer on Earth. Greater angular extent does not itself imply greater surface brightness. Constellations already change through stellar motions without a galactic merger. Documentary screenshots are inspiration, not observational data or automatically licensed publication assets.

### Topic 7 (Explainer): Central Black Holes and Gravitational Waves

**Question:** If the galaxies merge, what additional processes are needed for their central black holes to coalesce?

**Work:** Review the sequence of orbital decay, binary formation, stellar/gas-driven hardening, and gravitational-wave-dominated inspiral using [R9] and a current hardening review to be selected in Stage 3.

**Method:** Critical literature synthesis and bounded timescale calculations. Keep black-hole initial conditions and hardening assumptions separate from the galaxy-merger model.

**Deliverable:** A conditional sequence of events and a table of assumptions controlling the delay between galaxy and black-hole mergers.

**Boundary:** Galaxy merger does not establish an immediate or guaranteed black-hole merger. The short delay in a particular simulation is not universal. Do not claim that gravitational waves alone bring kiloparsec-separated black holes together, or that a present-day detector will observe this future event.

## Act III: Why We Could Be Wrong

Act III keeps the forecast honest: what new data would change it, and where the model itself may fail.

### Topic 8: What Would Let Us Know More?

**Question:** Which improvements in measurements or model fidelity would most reduce uncertainty, and which would merely make one assumed model look more precise?

**Work:** Separate random measurement error, shared calibration/systematic error, dynamical-model uncertainty, and Monte Carlo sampling error. Revisit the proper-motion precision target discussed in [R3] without presenting it as our discovery. Use Gaia DR4 as the first real test: compare the pre-DR4 forecast with its update.

**Method:** After replication, compare precision-improvement scenarios with and without a documented systematic floor, across supported model variants. Respect available correlations; label unmeasured systematic assumptions as stress tests, not inferred posteriors.

**Deliverable:** Measurement-priority and robustness report, including conclusions that remain unresolved.

**Boundary:** Narrowing an error bar around its current central value is a hypothetical scenario, not a prediction of the next measurement. A smaller formal error does not guarantee a more reliable forecast.

### Topic 9: Where the Model May Break Down, and What the Past Allows

**Question:** Which simplifications could change the forecast, and is each sampled present-day configuration consistent with a plausible 13.8 Gyr shared history?

**Work:** Document model limits: rigid spherical NFW halos that overlap long before the galaxies meet, no tidal stripping of halo mass, Chandrasekhar-type dynamical friction designed for small satellites but applied to near-equal galaxies, a 20 kpc numerical merger flag, and a fixed solar position and velocity in the frame transformation. Compare the forecasts with the timing argument for Local Group mass [R12] and with constrained cosmological simulations of the Local Group [R13]-[R14].

**Method:** Cheap checks first: sample the solar Galactocentric distance and velocity within published uncertainties and report the change in merger fraction; vary the merger criterion and softening. Answer the history question by literature comparison, not new cosmological simulations.

**Deliverable:** A "why we could be wrong" table ranking model limitations by tested or literature-estimated effect, and a short note on whether past-history constraints narrow the forecast.

**Boundary:** Do not integrate the dissipative model backward in time: dynamical friction would become an unphysical acceleration. The timing argument has its own assumptions and known biases [R12]. Untested limitations are listed as open, not assumed negligible.

## Mathematical Framework

These equations define the scope of the calculations, not a substitute for the cited numerical methods.

### Astrometric Scale

$$
v_\perp = 4.74047\,\mu D.
$$

Here velocity is in km/s, proper motion in mas/yr, and distance in kpc. At 780 kpc, 10 microarcseconds/yr corresponds to approximately 37 km/s. Transform vector components into a common frame with a documented solar-motion correction; a heliocentric scalar is not the final MW-M31 transverse velocity.

### Conditional Encounter Probability

$$
P(T_{\rm merge}<T\mid\mathcal D,\mathcal M)
=\int \mathbf 1[T_{\rm merge}(\theta;\mathcal M)<T]
\,p(\theta\mid\mathcal D,\mathcal M)\,d\theta.
$$

The adopted distribution of parameters must be explicit, including when it is a literature-based approximation rather than a jointly inferred posterior. Set the initial comparison horizon to 10 Gyr. Define the numerical merger flag and distinguish it from resolved physical coalescence. Runs without a merger by the horizon are censored outcomes, not infinite merger times.

For independent Monte Carlo realizations, the approximate sampling standard error is:

$$
\operatorname{SE}(\hat p)\simeq\sqrt{\frac{\hat p(1-\hat p)}{N}}.
$$

At 10,000 realizations this is at most 0.5 percentage points. It does not include observational or model uncertainty. Use an appropriate binomial interval, including near zero or unity, and paired uncertainty estimates for matched-sample comparisons.

### Stellar Encounter Scale

$$
\tau=\int n(t)\,\sigma_{\rm coll}(t)\,v_{\rm rel}(t)\,dt,
\qquad P_{\rm coll}\simeq 1-e^{-\tau}.
$$

Define the stellar population, path, physical collision cross-section, and any gravitational focusing. This is an idealized per-star encounter calculation; a galaxy-wide event count needs integration over the population.

### Slow Stellar Mass Loss

$$
a_{\rm final}\simeq a_{\rm initial}
\frac{M_{\rm initial}}{M_{\rm final}}.
$$

This applies to a surviving low-mass planet under slow, approximately isotropic stellar mass loss, neglecting tides and other perturbations. It does not decide Earth's survival.

### Illustrative Angular Size

$$
\theta=2\arctan\left(\frac{R}{D}\right).
$$

This is the angular diameter for a simplified face-on circular extent with physical radius R at distance D. An inclined, evolving galaxy and an observer inside another galaxy require additional geometry. Angular size is not a surface-brightness forecast.

## Five Delivery Stages

Stages 1 and 2 are deadline-driven by Gaia DR4. Stages 3 and 4 can run in parallel afterwards. Stage 5 waits for credible DR4-based measurements.

### Stage 1: Reproduce the Baseline (target: 18 November 2026)

**Covers:** Topics 1-2, with inputs for Topics 3 and 8.

- Read the final [R2] publication alongside its preprint/notebook and [R3]-[R4]. Freeze the exact versions used.
- Assemble a parameter table with quantity, units, frame, epoch, central value, distribution, covariance, source location, and mass definition.
- Define first pericentre, closest approach over the integration window, merger flag, time origin, and the 10 Gyr horizon.
- Run the public [R10] notebook in the separate research repository (see Scope); preserve its provenance and respect GPL-3.0 requirements for redistributed derivatives.
- Record dependency versions, upstream commit, parameter configuration, seed, and numerical settings. Do not add a simulation dependency to the production portal.
- Run a small smoke-test ensemble and measure runtime, then a size justified by the desired sampling precision; 10,000 independent realizations is the planning target.
- Reproduce the [R3] fiducial four-body result first, because the forecast depends on it; then [R2] if time permits; then the satellite-inclusion comparisons.
- Export numerical results as well as figures, including non-merger outcomes, LMC merger times, and run metadata.

**Exit gate:** Recover the selected paper's result within a predeclared tolerance based on sampling uncertainty and input/version fidelity. A practical initial target is a difference below two combined sampling standard errors; discrepancies must be explained, not tuned away. Confirm timestep convergence and frame/unit correctness before interpreting outcomes.

### Stage 2: Publish the Pre-DR4 Forecast (deadline: 1 December 2026)

**Covers:** Topics 1 and 8; story beats 2 and 6.

- Fix the "materially changed" threshold, then compute the proper-motion-plane probability map in the frozen configuration and mark current measurements.
- Write the forecast note: what was reproduced, the pre-stated regions, the decision rule, and the limitations.
- Tag the commit and publish the note. A short static note is sufficient; the full Deep Research page comes later.

**Exit gate:** The forecast note, frozen code, and decision rule are public and timestamped before 2 December 2026. No numbers that failed Stage 1 validation.

### Stage 3: Reconcile and Stress-Test

**Covers:** Acts I and III quantitatively (Topics 1-3, 8, and 9), plus the evidence ledger for all topics.

- Build the evidence ledger with claim, source, publication status, assumptions, evidence class, uncertainty, intended use, and unresolved questions. Include the documentary claims listed below; do not reproduce the transcript as research prose.
- Select solar-calibrated evolutionary tracks, fill the remaining source gaps, review reuse permissions for code, figures, and images, and refresh the literature search.
- Reproduce whichever of [R2] and [R3] was not completed in Stage 1, using the same definitions when comparing outputs.
- Run the Topic 9 cheap checks: solar-parameter sampling, merger criterion, and softening.
- Use matched random draws for common inputs and a small factorial comparison to distinguish changed M31 proper motions, changed M33 proper motions, and concentration assumptions, including interactions between changes.
- Report differences in encounter distances/times and merger fractions, not just a headline percentage.
- Complete a targeted novelty review. Astrometric sensitivity and satellite-effect reversal are already studied in [R3]. The systematic-floor question below is a sub-question of Topic 8, secondary to the DR4 forecast.
- Candidate hypothesis: retaining a plausible shared astrometric systematic floor limits the gain from reducing random proper-motion errors, and the size of that limit depends on the supported halo configuration.
- Test with a baseline, random-error-only improvement, and improvement with an explicit systematic floor. Compare a preregistered measure, such as the spread in conditional merger probability over the declared nuisance-parameter region. Do not invent covariance evidence or substitute arbitrary distributions for observations.
- Disconfirmation: the systematic-floor and model variants have negligible effect relative to the predeclared tolerance, or the claimed limitation disappears under supported assumptions. A null result is acceptable.

**Exit gate:** Clearly separate replication, published mechanisms, sensitivity experiments, and any genuinely new result. Conclusions must survive the relevant numerical checks and disclose dependence on chosen systematic scenarios.

### Stage 4: Connect the Consequences

**Covers:** Act II (Topics 4-7), linked to the encounter ensembles.

- Build the three-clock timeline, the central storytelling figure, using a common time origin: elapsed time from the adopted present epoch, not total stellar age. Place the LMC merger on it.
- Assign solar phases from selected tracks; report alternative tracks separately unless defensible model weights exist. An initial independent-track overlay is a stated approximation, not a coupled simulation of stellar and galactic evolution.
- Produce the bounded stellar-collision and planetary mass-loss examples with assumptions and units visible.
- Build an angular-size illustration from validated trajectories. Defer predictive stellar migration, gas/starburst modelling, and photorealistic future skies unless suitable validated simulations are available.
- Review black-hole evolution conditionally on galaxy merger, including hardening uncertainty.

**Exit gate:** Each consequence is labelled calculated, literature-derived, or illustrative. No unsupported Earth-survival probability, fixed habitability deadline, guaranteed starburst, or guaranteed black-hole-coalescence time.

### Stage 5: Update Against DR4 and Publish the Deep Research Experience

**Covers:** All nine topics at their validated evidence level.

- When credible DR4-based proper motions for M31 and M33 are published, apply the decision rule and publish the update beside the pre-DR4 forecast, whatever the result.
- Build one research page in three acts with depth-on-demand sections; split into separate pages only when the material warrants it.
- Lead with the story beats and the evidence, not an inevitable-collision countdown. Make the model, date, and horizon visible beside each probability.
- Present the baseline ensemble, the LMC's "next collision", satellite comparisons, robustness results, the three-clock timeline, and the before/after DR4 comparison. Treat future-sky imagery as an optional, explicitly labelled companion.
- Optional epilogue: the far-future isolation of the Local Group as other galaxies recede, labelled as beyond the 10 Gyr horizon and sourced before use.
- Keep long-running simulations offline. Publish versioned, precomputed outputs and link to reproducible research code.
- Include sources, methods, limitations, data provenance, asset credits, and a concise change history. Reflect later findings as revisions, not silent number changes.
- Add one grounded scientist-leader archetype reflection, the leadership insight in the story section, kept separate from scientific evidence.

**Exit gate:** The DR4 update is published against the pre-stated rule, scientific review is complete, central numbers agree across prose and charts, all topics have evidence-backed coverage, and the eventual implementation passes accessibility, mobile/desktop, and interaction checks.

## Validation and Research Integrity

- Compare the gravity-only integrator against a known two-body orbit and test energy/angular-momentum conservation in that conservative limit.
- With dynamical friction enabled, test momentum accounting and expected orbital energy transfer; do not incorrectly demand conserved orbital energy from a dissipative approximation.
- Check timestep sensitivity, softening, merger threshold, and the bookkeeping of masses and momenta after a merger flag.
- Preserve uncertainty covariances where supplied; explicitly document independence assumptions in reproduction runs and test them only with justified alternatives.
- Keep numerical error, sampling error, observational uncertainty, systematic scenarios, and model spread separately labelled.
- Report both all-realization summaries and merger-conditional summaries with clear denominators.
- Treat selected N-body cross-checks as validation of those examples, not proof that the full ensemble is validated.
- Freeze comparison criteria before inspecting extension results. Retain null results, failures, and version-specific discrepancies.
- Seek review by a galactic-dynamics specialist before claiming a novel astrophysical result; use a clear independent-research label if specialist review has not occurred.
- Pre-registration: the pre-DR4 forecast, threshold, and decision rule are fixed in a tagged commit before 2 December 2026. Later changes are new versions, never edits to the original.

## Scope and Dependencies

**Core quantitative study:** Topics 1, 2, 3, 8, and 9, followed by the Topic 5 timeline overlay.

**Companion analysis:** Topics 4, 6, and 7 use cited synthesis and bounded calculations first. Detailed stellar migration, gas hydrodynamics, planetary tides, and relativistic black-hole dynamics are separate modelling projects, not hidden requirements for the first release.

**Sequence:** Stage 1 -> Stage 2 (DR4 deadline) -> Stages 3 and 4 in parallel -> Stage 5 (after credible DR4-based measurements). Literature work for Stage 4 can start at any time, but encounter-dependent conclusions wait for validated ensembles.

**Compute checkpoint:** Measure runtime and memory at the Stage 1 smoke test before selecting ensemble size or scheduling broader parameter sweeps. No GPU, cluster, cloud spend, or new observational campaign is assumed or authorized by this plan.

**Repository checkpoint:** Keep this plan in the portal documentation. Put the numerical work in a separate sibling repository, following the `3I-Atlas-Research` pattern, so GPL-3.0 upstream code stays out of the Flask application. Confirm the repository name and licensing before scaffolding.

## Documentary Claims to Verify

Check these claims from the supplied material during Stage 3, before any reuse:

- Andromeda contains about a trillion stars, and the Milky Way 200-400 billion.
- Andromeda's disc is about 200,000 light-years across.
- Andromeda's full extent spans about six full Moons on the sky.
- First close passage in 4-5 billion years, presented as inevitable.
- About 2 billion years from first contact to merger.
- Andromeda fills half the sky in 3 billion years, with individual stars visible.
- The gravitational-wave power of a supermassive black-hole merger exceeds the starlight of the observable universe.
- The Sun "will probably survive" and Earth "would likely survive" the encounter.

## Milestone Checklist

- [x] M1 (target 18 November 2026): Parameter table frozen, [R3] baseline reproduced, validation report written. Completed 2026-10-28 in the sibling `andromeda-research` repository (commit `22f7b8d`): Wu (2026) 90.1% and Sawala (2025) 52.3% merger fractions reproduced; see its `docs/reproduction-log.md`.
- [ ] M2 (deadline 1 December 2026): Pre-DR4 forecast, threshold, and decision rule public and timestamped.
- [ ] M3: Forecasts reconciled, Topic 9 checks run, evidence ledger complete.
- [ ] M4: Three-clock timeline and Act II explainers complete.
- [ ] M5: DR4 update published; scientific review, reproducibility package, and Deep Research publication complete.

## Initial Source Register

This is a starting bibliography, not a completed systematic review. Prefer final papers for scientific claims, preserve versions used in replication, and expand the ledger with page/table/figure locations during Stage 3.

| ID | Source | Role |
|----|--------|------|
| R1 | van der Marel et al. (2012), [The M31 Velocity Vector. III. Future Milky Way-M31-M33 Orbital Evolution, Merging, and Fate of the Sun](https://arxiv.org/abs/1205.6865) | Historical encounter model and solar-analogue outcomes |
| R2 | Sawala et al. (2025), [No certainty of a Milky Way-Andromeda collision](https://doi.org/10.1038/s41550-025-02563-1); [2024 preprint](https://arxiv.org/abs/2408.00064) | Uncertain four-body forecast; reconcile publication/code versions |
| R3 | Wu et al. (2026), [The Fate of the Milky Way-Andromeda System: To Merge or Not?](https://arxiv.org/abs/2603.22863) | Updated forecast, geometric satellite effects, and precision sensitivity |
| R4 | Wu et al. (2025), [Revisiting the proper motions of M31 and M33 using massive supergiant stars with Gaia DR3](https://doi.org/10.1051/0004-6361/202555477) | Measurement and astrometric-systematics basis of R3; full review pending |
| R5 | Wu et al. (2026), [Mass Distribution of M31 from its Rotation Curve up to 167 kpc](https://arxiv.org/abs/2609.25758) | Candidate halo-structure constraints; full methods review pending |
| R6 | Patel, Garavito-Camargo, and Escala (2025), [The M31-M33 Interaction: Impact on M31's Center-of-mass Motion and Satellite Orbits](https://doi.org/10.3847/1538-4357/adc992) | Satellite-induced motion; full review pending |
| R7 | Schroder and Smith (2008), [Distant future of the Sun and Earth revisited](https://arxiv.org/abs/0801.4031) | Solar evolution, mass loss, and conditional Earth-engulfment calculation |
| R8 | Veras (2016), [Post-main-sequence planetary system evolution](https://arxiv.org/abs/1601.05419) | Planetary dynamics around evolving stars; review |
| R9 | Schiavi et al. (2021), [Future merger of the Milky Way with the Andromeda galaxy and the fate of their supermassive black holes](https://arxiv.org/abs/2102.10938) | Conditional black-hole evolution and model-specific delay |
| R10 | Sawala, [MW-M31 public research code](https://github.com/TillSawala/MW-M31) | Baseline notebook; GPL-3.0; freeze upstream commit before use |
| R11 | Cautun et al. (2019), [The aftermath of the Great Collision between our Galaxy and the Large Magellanic Cloud](https://arxiv.org/abs/1809.09116) | Dedicated LMC-Milky Way merger model; extract merger time in Stage 3 |
| R12 | Sawala et al. (2023), [The timeless timing argument and the total mass of the Local Group](https://arxiv.org/abs/2307.13732) | Past-history constraint on Local Group mass |
| R13 | Wempe et al. (2024), [Constrained cosmological simulations of the Local Group using Bayesian hierarchical field-level inference](https://arxiv.org/abs/2406.02228) | Constrained Local Group simulations; full review pending |
| R14 | Woudenberg et al. (2026), [Alignment of the Milky Way and M31 with their cosmic environment](https://arxiv.org/abs/2607.13005) | Constrained Local Group simulations; submitted, full review pending |
| R15 | ESA, [Gaia data release scenario](https://www.cosmos.esa.int/web/gaia/release) | Gaia DR4 date of 2 December 2026; recheck before the deadline |

**Explicit source gaps:** Modern Earth-climate/habitability modelling; a dedicated gas/star-formation response study; a current massive-black-hole hardening review; a source for the far-future isolation epilogue; machine-readable solar-track availability and reuse terms; final publication metadata and any subsequent relevant results. Filling these gaps is part of Stage 3, not evidence already established here.