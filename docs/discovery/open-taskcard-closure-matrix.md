<!-- GENERATED — do not edit manually. Run: python -m plugin_examples sync-taskcard-docs -->
# Open Taskcard Closure Matrix

**Matrix date:** 2026-05-09
**Sprint:** Post-Discovery Next Sprint (Phases A-H) — state board update
**Total:** 120 | **Open:** 48 | **Closed:** 71

---

## Open Taskcards

| ID | Title | Blocking |
|----|-------|----------|
| `followup-family-readiness-ranker-trust` | Add confidence and evidence_source fields to generation readiness ranking | Observability only |
| `followup-words-split-criteria-enumeration` | Add SplitCriteria enum values to DllReflector catalog output | WORDS-005 Splitter.Split |
| `followup-words-pair-fixture-strategy` | Define fixture strategy for paired-input scenarios (Comparer, Merger) | WORDS-006 Comparer, WORDS-007 Merger |
| `followup-words-mail-merger-fixture-documentation` | Create template DOCX with documented merge field names for MailMerger | WORDS-008 MailMerger |
| `followup-words-docx-semantic-validation` | Automate DOCX text extraction validation in pipeline | Automated semantic validation for DOCX output scenarios |
| `followup-example-reviewer-feedback-loop` | Example reviewer feedback loop — per-example structured reviewer feedback driving targeted repair | Reviewer-driven repair loop (not blocking current publish) |
| `followup-full-planned-example-completion-contract` | Define per-scenario completion contract (required_options_class, required_inputs, known_invalid_patterns, few_shot_required, completion_blocker) |  |
| `followup-scenario-completion-queue` | Replace binary pass/exclude with state machine: discovered > classified > contract_defined > ready_to_generate > blocked_* > generation_in_progress > validated > packaged > pr_published > merged |  |
| `followup-backlog-to-taskcard-bridge` | Auto-create taskcard entries when scenarios enter backlogged state; bridge backlog JSON to taskcard matrix |  |
| `followup-readiness-rank-full-completion-metrics` | Add full_completion_possible, true_completion_rate, next_blocker_to_clear, expected_completion_after_fixes to readiness rank |  |
| `followup-learning-repair-system` | Implement learning/repair system: backlog failures become negative constraints; successful code becomes few-shot templates; code validator issues trigger targeted repair with API catalog excerpts |  |
| `followup-coverage-100-denominator-model` | Create and maintain formal coverage denominator model: per-family runnable classification rules, total/runnable/deferred counts, evidence-backed denominator baseline JSON updated each sprint |  |
| `followup-pdf-remaining-candidate-classification` | Classify 21 unattempted PDF WORKFLOW_ROOT types: run DllReflector per type, assess standalone runnability, assign RUNNABLE or NON_RUNNABLE with evidence, finalize PDF denominator |  |
| `followup-words-full-coverage-expansion` | Group taskcard: all 5 deferred Words types — Splitter.Split (SplitCriteria enum), Comparer.Compare (paired fixture), Merger.Merge (paired fixture), MailMerger.Execute (template DOCX), Processor/ReportBuilder (role classification) |  |
| `followup-cells-coverage-denominator-audit` | Formal audit of 13 non-runnable Cells type classifications: verify each is provably non-runnable (abstract, options class, callback, result) with DllReflector evidence; document in denominator baseline |  |
| `followup-pdf-pr3-review-and-merge` | PDF PR #3: create live PR (Merger + Splitter), review, merge, and post-merge verify | PDF PR #3 publication — 3 examples await (Merger+Splitter in PR#3, Optimizer in PR#4 after 2nd pass) |
| `NEW-01-followup-all-family-yaml-creation` | Create discovery-only YAML configs for all Aspose .NET candidate families without current configs | True |
| `NEW-02-followup-email-blocker-investigation` | Resolve email discovery blocker: enabled=true config in disabled/ dir; reflection status unknown |  |
| `NEW-03-followup-slides-dll-name-fix` | Fix Slides DLL name mismatch: Aspose.Slides.NET package produces Aspose.Slides.dll not Aspose.Slides.NET.dll |  |
| `NEW-04-followup-monthly-workflow-all-families` | Extend monthly-package-refresh.yml to cover all active LowCode families, not just cells |  |
| `NEW-06-followup-cells-words-pr1-merge-artifact` | Create post-merge verification artifacts for Cells PR#1 and Words PR#1 example merges |  |
| `NEW-07-followup-words-workflow-root-classification` | Run full type-role classification for all 25 Aspose.Words.LowCode types; resolve workflow_root_types=NULL in denominator | True |
| `TASK-NEW-08-followup-dropped-planned-example-audit` | Audit: add 21 PDF deferred WORKFLOW_ROOT types and 16 Words deferred types to completion queue | True |
| `TASK-NEW-09-followup-verification-failure-root-cause-taxonomy` | Formalize root-cause taxonomy; supersede stale RC-005 pdf-splitter runtime failure record |  |
| `TASK-NEW-10-followup-dropped-example-to-backlog-sync` | Add backlog entries for 21 PDF deferred types and Words unclassified types lacking backlog entries |  |
| `TASK-NEW-11-followup-backlog-to-relaunch-queue` | Implement mechanism to promote resolved backlog entries to RELAUNCH_READY in completion queue |  |
| `TASK-NEW-12-followup-relaunch-result-to-denominator-sync` | Automate denominator published_count update after successful relaunch and PR merge |  |
| `TASK-NEW-13-followup-reviewer-failure-actionable-feedback` | Add structured per-example reviewer feedback (which API misused, which pattern missing, suggested fix) |  |
| `TASK-NEW-14-followup-validator-failure-classification` | Replace unknown_runtime_failure catch-all with typed classification (wrong_input_format, missing_fixture_file, api_exception, output_missing, wrong_output_content, unknown) |  |
| `TASK-NEW-15-followup-fixture-gap-relaunch-system` | Implement pair-input, template-DOCX, and form-fields-PDF fixture strategies for blocked examples | True |
| `TASK-NEW-16-followup-options-class-repair-learning` | Extend LLM generation prompt to include correct paired_options_class name for every new PDF WORKFLOW_ROOT type |  |
| `TASK-NEW-17-followup-forbidden-core-api-regression-guard` | Extend FORBIDDEN constraint injection to cover all families; make family-specific constraints configurable per YAML |  |
| `TASK-NEW-18-followup-post-merge-failure-relaunch-policy` | Document relaunch policy for post-merge checkout validation failures |  |
| `NEW-19-followup-email-controlled-pilot-planning` | Plan and configure Email controlled pilot: fixture strategy, allowed_types, target repo |  |
| `NEW-20-followup-slides-controlled-pilot-planning` | Plan and configure Slides controlled pilot: fixture strategy, allowed_types, target repo |  |
| `NEW-21-followup-diagram-controlled-pilot-planning` | Plan and configure Diagram controlled pilot: fixture strategy, allowed_types, target repo |  |
| `NEW-22-followup-epub-reflection-blocker-investigation` | Investigate Aspose.Epub NuGet package availability and correct package ID |  |
| `NEW-24-followup-ocr-reflection-blocker-investigation` | Fix OCR reflection blocker: Aspose.Drawing.Common missing transitive dep |  |
| `NEW-25-followup-omr-reflection-blocker-investigation` | Fix OMR reflection blocker: Newtonsoft.Json missing transitive dep |  |
| `NEW-26-followup-psd-reflection-blocker-investigation` | Fix PSD reflection blocker: Newtonsoft.Json missing transitive dep |  |
| `NEW-28-followup-confirmed-no-lowcode-documentation` | Create formal evidence registry for all 15 CONFIRMED_NO_LOWCODE families |  |
| `TC-WORDS-01-words-full-sot-classification` |  |  |
| `TC-PDF-01-pdf-merger-rerun-post-fix` |  |  |
| `TC-PDF-02-pdf-optimizer-2nd-pass` |  |  |
| `TC-SYS-01-github-token-contents-write-fix` |  |  |
| `TC-PDF-03-pdf-21-type-fixture-assessment` |  |  |
| `TC-EMAIL-01-email-fixture-strategy-design` |  |  |
| `TC-SLIDES-01-slides-fixture-strategy-design` |  |  |

---

## Closed Taskcards

| ID | Title | Closed In |
|----|-------|-----------|
| `followup-aspose-net-link-standardization` | Standardize all Aspose .NET README links to use aspose.net domain with correct URL patterns | Aspose .NET Link Standardization Hardening Review |
| `followup-publisher-evidence-ordering` | Publisher reads gate_verdict directly | Options-Aware API Usage Sprint |
| `followup-discovery-sweep-deps` | Discovery sweep resolves dependencies before DllReflector | Multi-Family API Catalog Expansion Sprint |
| `followup-github-api-403` | Fixture registry 403 degradation with explicit reason code | Multi-Family API Catalog Expansion Sprint |
| `followup-discovery-only-safety` | Block discovery_only families from generation pipeline | Governance Closure Sprint |
| `followup-disabled-configs-cleanup` | Remove stale disabled/ config files for words and pdf | Governance Closure Sprint |
| `followup-llm-provider-policy-enforcement` | Add policy guard to _check_provider() to prevent unapproved provider selection at preflight | Governance Closure Verification Review |
| `followup-words-role-classification-review` | Review MailMergeDataSource workflow_root classification | Words Readiness Review Sprint |
| `followup-words-options-aware-review` | Verify Aspose.Words.LowCode options-aware rules before generation | Words Readiness Review Sprint |
| `followup-words-converter-fix` | Fix Converter scenario: use valid output extension | Words Controlled Pilot Sprint Fix Pass |
| `followup-words-splitter-fix` | Fix Splitter scenario: ExtractPages-only, valid extension | Words Controlled Pilot Sprint Fix Pass |
| `followup-words-output-extension-prompt-guard` | Add output extension validation to LLM packet builder | Words Controlled Pilot Sprint Fix Pass |
| `followup-words-pr-packaging` | Package 4 verified Words examples into PR dry-run candidate against aspose-plugins-examples-dotnet | Words PR Packaging Sprint |
| `followup-pdf-reflection-dedup` | Deduplicate dependency assemblies before DllReflector for PDF | PDF Assembly Deduplication Sprint |
| `followup-fixture-token-ci` | Document and enforce GitHub token handling for fixture discovery in CI | Consistency Hardening Sprint (Sprint A2) |
| `followup-readme-backfill-token-refresh` | Refresh GITHUB_TOKEN with repo write scope and create README-only backfill PRs for Cells and Words | README Backfill Token Recheck and PR Creation Sprint |
| `followup-root-readme-backfill-prs` | README backfill PRs for Cells and Words await human review and merge | README Backfill PR Review, Merge, and Post-Merge Verification Sprint |
| `followup-readme-symbols-from-catalog` | Fix README generator to list actual method demonstrated, not full catalog symbols | README Demonstrated API Accuracy From Manifest/Catalog Sprint |
| `followup-family-publish-target-mapping` | Identify and configure correct family-specific published_plugin_examples_repo for each active family | Family-Specific Repo Mapping Verification and Config Update Sprint |
| `followup-repo-access-permission` | Verify GITHUB_TOKEN has read+write access to aspose-cells-net and aspose-words-net repos | Token Access Grant Sprint |
| `followup-family-repo-provisioning` | Provision aspose-cells-net and aspose-words-net target repos on GitHub | Token Access Grant Sprint |
| `followup-real-github-pr-publisher` | Implement real GitHub PR publisher replacing stub (result.status = 'published') with actual GitHub REST API calls | Real GitHub PR Publisher Implementation Sprint |
| `followup-words-live-pr-canary` | Create first live PR for Words controlled pilot (4 examples) as canary | Words Live PR Canary Sprint |
| `followup-words-live-pr-post-creation-verification` | Post-creation verification of Words PR #1: remote checks, clean checkout build/run, token policy cleanup | Words Live PR Post-Creation Verification and Token Policy Cleanup Sprint |
| `followup-token-policy-cleanup` | Ensure pipeline uses only GITHUB_TOKEN; docs do not require GH_TOKEN; evidence does not expose token values | Words Live PR Post-Creation Verification and Token Policy Cleanup Sprint |
| `followup-agent-operated-live-pr-creation` | Human gives explicit approval; Agent creates live PRs for Cells (9 examples) and Words (4 examples) using the approved, repeatable pipeline | Cells Live PR Canary Sprint |
| `followup-cells-live-pr-canary` | Create first live PR for Cells controlled pilot (9 examples) as canary, post Words PR verification | Cells Live PR Canary Sprint |
| `followup-publish-readiness-access-gates` | 4-tier publish readiness model: config_ready, repo_access_ready, pr_permission_ready, live_publish_ready | Repo Access Resolution and Repeatable Target Provisioning Sprint |
| `followup-live-pr-approval-gate` | Establish explicit human approval gate before live PR creation | Live PR Approval Gate and Safe Branch Probe Sprint |
| `followup-pr-review-and-merge-governance` | Define and implement repeatable safe PR review and merge workflow | PR Review and Merge Governance Sprint |
| `followup-words-pr-merge` | Merge Words PR #1 after human APPROVE_MERGE_PR approval | Words PR Merge and Post-Merge Verification Sprint |
| `followup-cells-pr-merge` | Merge Cells PR #1 after human APPROVE_MERGE_PR approval | Cells PR Merge and Post-Merge Verification Sprint |
| `followup-root-readme-template-workflow` | Implement repeatable root README generation workflow for LowCode family example repos | Root README Template and Update Workflow Sprint |
| `followup-pdf-role-classification-review` | Classify PDF LowCode types into WORKFLOW_ROOT / OPTIONS / PROVIDER_CALLBACK roles | PDF Role Classification + Options-Aware Review Sprint |
| `followup-pdf-options-aware-review` | Review PDF options-aware type patterns (41 options types identified) | PDF Role Classification + Options-Aware Review Sprint |
| `followup-pdf-controlled-pilot-enablement` | Enable PDF controlled pilot generation (4 types) after all 4 PDF blockers resolved | PDF Controlled Pilot Enablement Sprint |
| `followup-pdf-fixture-strategy-review` | Define fixture strategy for PDF examples (input file format and programmatic creation) | PDF Fixture Strategy Review |
| `followup-pdf-family-repo-target-mapping` | Map PDF family to target repository for publishing | PDF Family Repo Target Mapping Sprint |
| `followup-pdf-repo-provisioning` | Create aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples repo and grant GITHUB_TOKEN access | PDF Controlled Pilot Enablement Sprint |
| `followup-cells-monthly-rerun-proof` | Document Cells Tier-5 monthly rerun proof from pilot-cells-20260430-175422 | Cells Tier-5 E2E Evidence Review Sprint |
| `followup-family-scoped-evidence-promotion` | Fix --promote-latest to be family-scoped to prevent cross-family overwrite of workspace/verification/latest/ | Family-Scoped Evidence Promotion and Latest-State Isolation Sprint |
| `followup-pdf-splitter-options-class` | PDF Splitter: fix LLM PluginOptions → SplitOptions hallucination | Wave 1 PDF Tier 5 LLM Pilot Sprint |
| `followup-pdf-optimizer-options-class` | PDF Optimizer: fix LLM options class hallucination and timeout recovery | Sprint R2 Revised — PDF Optimizer Repair Constraint Injection Fix and Rerun |
| `followup-pdf-merger-few-shot-fix` | PDF Merger: add few-shot MergeOptions example to fix LLM code generation | PDF Pilot API Correctness Healing Sprint |
| `followup-pdf-text-extractor-lowcode-fix` | PDF TextExtractor: fix LLM to use Aspose.Pdf.LowCode.TextExtractor not TextAbsorber | PDF Pilot API Correctness Healing Sprint |
| `followup-example-lifecycle-tracking` | Example lifecycle tracking and per-family backlog system | Example Failure Recovery, Reviewer Repair Loop, and Per-Family Backlog Tracking Sprint |
| `followup-pdf-repo-provisioning-confirmed` | PDF repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples provisioned and accessible | Example Failure Recovery Sprint (Phase 8 probe) |
| `followup-example-failure-recovery-lifecycle` | Example failure recovery lifecycle — lifecycle records for all planned examples including excluded/failed | Example Lifecycle, Backlog Backfill, and Reviewer Feedback Loop Hardening Sprint |
| `followup-per-family-example-backlog` | Per-family example backlog — durable backlog entries for failed/excluded examples with root cause and taskcard cross-links | Example Lifecycle, Backlog Backfill, and Reviewer Feedback Loop Hardening Sprint |
| `followup-pdf-pr1-merge` | Merge PDF PR #1 (merger + text-extractor) to aspose-pdf-net target repo | PDF PR #1 Merge, Post-Merge Verification, and Cross-Family Failure-Recovery Audit Sprint |
| `followup-pdf-optimizer-build-repair-constraint-injection` | PDF Optimizer: add PDF constraint re-injection to build repair path in runner.py | PDF Optimizer Build-Repair Constraint Injection Fix Sprint |
| `followup-pdf-text-extractor-static-validation-regression` | PDF TextExtractor: investigate static validation regression — strengthen repair prompt with explicit TextExtractorOptions example | PDF Optimizer Build-Repair Constraint Injection Fix Sprint |
| `followup-pdf-optimizer-llm-rerun` | PDF Optimizer: run LLM Tier 5 pilot with constraint injection fix active to produce publishable example | Sprint R2 Revised — PDF Optimizer Repair Constraint Injection Fix and Rerun |
| `followup-pdf-optimizer-repair-constraint-injection` | PDF Optimizer: inject FORBIDDEN DataSources constraint into repair prompt in code_generator.py | Sprint R2 Revised — PDF Optimizer Repair Constraint Injection Fix and Rerun |
| `TC14-03-production-gate-tests` | Add 14 unit tests for is_agent_metrics_production_enabled() and runner integration | TC14 Source Gate and Production-Shaped Dry Run Sprint |
| `TC14-04-production-shaped-dry-run` | Run production-shaped dry-run with AGENT_METRICS_PRODUCTION_ENABLED=true, verify all 14 dry-run gates | TC14 Source Gate and Production-Shaped Dry Run Sprint |
| `TC14-05-production-approval-checklist` | Human reviews dry-run evidence and approves Sprint 2 one-row production POST | TC14 One-Row Production POST Sprint |
| `TC14-06-one-row-production-post` | Execute exactly one production POST to Agent Metrics Google Sheet endpoint | TC14 One-Row Production POST Sprint |
| `TC14-08-rollback-disable-verification` | Verify production posting is instantly disabled after Sprint 2 by unsetting env vars | TC14 One-Row Production POST Sprint |
| `TC14-09-independent-verification` | Independent read-only audit of all Sprint 2 evidence — confirm 1 production row, all gates verified, no secrets | TC14 Independent Verification and Final Closure Sprint |
| `NEW-05-followup-release-status-pdf-default` | Fix release-status CLI default to include pdf alongside cells and words |  |
| `NEW-23-followup-html-reflection-blocker-investigation` | CLOSED: html confirmed CONFIRMED_NO_LOWCODE after manual DllReflector run | Post-Discovery Next Sprint Phase D (same sprint) |
| `NEW-27-followup-svg-reflection-blocker-investigation` | CLOSED: svg confirmed CONFIRMED_NO_LOWCODE after manual DllReflector run | Post-Discovery Next Sprint Phase D (same sprint) |
| `SPRINT-R5-enum-blocked-scenarios-tracking` |  |  |
| `SPRINT-R5-per-type-constraints-all-families` |  |  |
| `SPRINT-R5-generalize-semantic-validation` |  |  |
| `SPRINT-R5-completeness-gate` |  |  |
| `SPRINT-R5-partial-pr-labeling` |  |  |
| `SPRINT-R5-release-status-all-families` |  |  |
| `SPRINT-R5-pdf-merger-textfragment-constraint-fix` |  |  |
| `SPRINT-R5-words-denominator-guard` |  |  |
