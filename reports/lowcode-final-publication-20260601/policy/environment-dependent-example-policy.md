# Environment-Dependent Example Policy

## Definition
An environment-dependent example requires external services or resources not available in all build/run environments (e.g., TSA endpoints, network access, specific file fixtures).

## Criteria for PUBLISH_ENVIRONMENT_DEPENDENT_EXAMPLE
1. The example compiles successfully in all environments (build exit 0).
2. The example runs successfully when the required service is available.
3. The example includes graceful degradation (try/catch) for offline scenarios.
4. The dependency is documented in the example's comments or README.

## Denominator Contribution
Environment-dependent examples do NOT count toward the canonical 42-example denominator.
They are published as supplementary content with clear documentation of requirements.

## Current Environment-Dependent Examples
| Example | Family | Dependency |
|---------|--------|------------|
| pdf/timestamp | pdf | DigiCert TSA endpoint (http://timestamp.digicert.com) |

## Decision Authority
Agent-delegated per sprint `lowcode-final-publication-20260601`.
