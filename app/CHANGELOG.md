# CHANGELOG

## [UNRELEASED]

- Adding endpoints:
    - /status (returns the status of the application)
    - /metrics (returns the metrics of the application)
    - /version (returns the version of the application)


## [1.0.1] - 2025-05-31

### Feat
- feat(container): Added application containerization and orchestration

  - The database is now deployed using Docker Compose
  - Added Nginx for proxying
  - Port for sending requests 80

## [1.0.0] - 2025-05-30

### Fix
- fix(structure): Updated project structure for better organization

### BREAKING CHANGE
- removed the container used for creating the database