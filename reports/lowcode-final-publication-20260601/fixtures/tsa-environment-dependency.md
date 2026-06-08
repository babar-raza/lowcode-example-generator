# TSA Environment Dependency Evidence

## Example: pdf/timestamp

## Dependency
Requires network access to DigiCert TSA endpoint: `http://timestamp.digicert.com`

## Behavior
- **Online**: Builds and runs successfully, produces timestamped PDF (681KB output)
- **Offline**: Builds successfully, run exits with caught exception (graceful degradation via try/catch)

## E2E Evidence
- Build exit code: 0
- Run exit code: 0 (when online)
- Output size: 681KB

## Graceful Degradation
Program.cs wraps TSA call in try/catch, prints error message on failure. Does not crash with unhandled exception.

## Publication Decision
PUBLISH_ENVIRONMENT_DEPENDENT_EXAMPLE — useful reference code with clear documentation of TSA requirement.
