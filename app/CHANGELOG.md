# CHANGELOG


## [UNRELEASED]

### Feat
- feat(database): Added database schema
- feat(api): Adding endpoints for login, registration and logout
- feat(api): Adding endpoints for working with document(s) and statistics for documents
- feat(api): Adding endpoints with collections and statistics for collections
- feat(api): Adding endpoints for working with user


## [1.2.2] - 2025-06-03

### Fix
- fix(container): changing the name of docker-compose and dockerfile files

## [1.2.1] - 2025-06-03

### Fix
- fix(container): change container access policy

## [1.2.0] - 2025-06-02

### Feat
- feat(api): Added endpoints for status, metrics, and version

    - api/v1/status/ (returns the status of the application)
    - api/v1/metrics/ (returns the metrics of the application)
    - api/v1/version/ (returns the version of the application)

The ```api/v1/metrics/``` returns 5 metrics: 

1. Number of registered users
2. Number of users who returned to the site
3. Number of users who returned to the site today
4. Number of files uploaded
5. Number of files uploaded today

These metrics will help determine interest in the site and the rate of reuse of the web application

## [1.1.0] - 2025-05-31

### Feat
- feat(container): Added application containerization and orchestration

  - The database is now deployed using Docker Compose
  - Added Nginx for proxying
  - Port for sending requests 80

## [1.0.1] - 2025-05-30

### Fix
- fix(structure): Updated project structure for better organization

### BREAKING CHANGE
- removed the container used for creating the database