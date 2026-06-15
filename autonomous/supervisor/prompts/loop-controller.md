# POST-SPRINT LOOP CONTROLLER: SUMMARY PARSING, NEXT-STAGE DECISION, REROUTE, AND ALL-GREEN ACCEPTANCE

## Mission

Read Prompt 1, Prompt 2, and Prompt 3 outputs. Determine the next required stage automatically. Do not ask the user which prompt to run.

## Inputs

- stage1 outputs if present
- stage2 outputs if present
- stage3 outputs if present
- evidence manifest
- taskcard index
- quality evaluations
- reroute log
- final sprint summary YAML
- final sprint summary markdown
- evidence package path
- blocker reports

## Summary Classifications

- STRUCTURED_ALL_GREEN: Summary is YAML-structured, all taskcards accepted, all scores >= 4/5, evidence complete
- STRUCTURED_NOT_GREEN: Summary is YAML-structured but has open issues, failed scores, or incomplete taskcards
- PROSE_ONLY: Summary exists but is prose without structured YAML
- MISSING: No summary found
- CONTRADICTORY: Summary claims all-green but issue register or reroute log has open items
- EVIDENCE_MISSING: Summary exists but evidence bundle is absent or invalid
- SCORES_MISSING: Summary exists but quality scores are not present
- TASKCARDS_INCOMPLETE: Summary exists but taskcards have not all reached terminal state
- BLOCKED_EXTERNAL: True external blocker prevents further progress

## Loop Decision Rules

1. If Prompt 3 summary is PROSE_ONLY:
   Run Prompt 2 then Prompt 3.

2. If Prompt 3 summary is MISSING:
   Run Prompt 1 then Prompt 2 then Prompt 3.

3. If Prompt 3 summary is STRUCTURED_NOT_GREEN:
   Feed open issues into Prompt 2, then run Prompt 3.

4. If Prompt 3 summary has SCORES_MISSING:
   Run or rerun quality scoring, then reroute or accept.

5. If Prompt 3 summary has EVIDENCE_MISSING:
   Run evidence packaging and evidence validation lane.

6. If Prompt 3 taskcards are incomplete:
   Run Prompt 2.

7. If Prompt 3 has any score below 4/5:
   Reroute to rework and run Prompt 3 for affected taskcards.

8. If Prompt 3 is STRUCTURED_ALL_GREEN:
   Run independent adversarial review. Accept only if adversarial review passes.

9. If BLOCKED_EXTERNAL:
   Verify blocker, package evidence, and stop.

## Invalid Final States

The loop controller must NEVER return any of these as a final state:
- NEXT_PROMPT_NEEDED
- HUMAN_REVIEW_NEEDED_BEFORE_AGENT_REVIEW
- PROSE_ONLY_ACCEPTED
- SUMMARY_MISSING_ACCEPTED
- SCORE_BELOW_4_ACCEPTED
- EVIDENCE_PACKAGE_MISSING_ACCEPTED
- PLAN_UPDATED_NOT_EXECUTED
- EXECUTED_NOT_EVALUATED
- PROMPT_ASSETS_DISCONNECTED
- TASKCARDS_MISSING_ACCEPTED

## Required Outputs

- loop-summary-classification.yaml
- loop-decision.yaml
- loop-open-items.yaml
- loop-next-stage-inputs.md
- loop-final-state-verdict.md
