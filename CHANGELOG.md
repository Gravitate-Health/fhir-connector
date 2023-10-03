# Changelog

This repository uses [SemVer](https://semver.org).

## [Unreleased]

## [0.10.0] - 2023-09-28

### Added

- Service sendes emails reporting errors in execution. A JSON file is ttached to the email to have structured data about the errors.

## [0.9.0] - 2023-09-22

### Fixed

- Bump sushi version to `fsh-sushi@3.4.0`.

### Changed


## [0.8.0] - 2023-09-21

### Fixed

- Fixed cronjob deployment, as it didn't terminate the job.

### Fixed

- Fix typos in recent README changes.
- Update outdated unreleased diff link.

## [0.7.0] - 2023-09-19

### Fixed

- Bundles which included all the rsources in the fsh files are now splitted into resources to be uploaded separately.

## [0.6.0] - 2023-09-11

### Added

- Added "List" FHIR resource to uploadeable resources list

## [0.5.0] - 2023-07-31

### Fixed

- Fixed FHIR resources list to be uploaded.

## [0.4.0] - 2023-06-30

### Added

- Added trivy action for security scanning

## [0.3.0] - 2023-06-30

### fixed

- Fixed actions for local execution with 'act'

## [0.2.0] - 2023-06-29

### Added

- Github actions

## [0.1.0] - 2023-06-23

### Added

- Syncs [HL7 Gravitate Health ePI repository](https://github.com/hl7-eu/gravitate-health). Uploads ePI in [this folder](https://github.com/hl7-eu/gravitate-health/tree/master/input/fsh) as bundles to FHIR server.
- Syncs [HL7 Gravitate Health IPS repository](https://github.com/hl7-eu/gravitate-health-ips). Uploads IPS in [this folder](https://github.com/hl7-eu/gravitate-health-ips/tree/master/input/fsh) as bundles to FHIR server.

[0.9.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Gravitate-Health/fhir-connector/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Gravitate-Health/fhir-connector/releases/tag/v0.1.0