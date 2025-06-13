# CHANGELOG

## [UNRELEASED]

### Feat

- feat(api): Adding endpoint ```api/v1/documents/<document_id>/huffman```
  
  - It will return the contents of the document encoded by [Huffman Code](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D0%B4_%D0%A5%D0%B0%D1%84%D1%84%D0%BC%D0%B0%D0%BD%D0%B0)

## [1.5.0] - 2025-06-13

### Feat
- feat(app): Adding a secure connection to a web application

## [1.4.0] - 2025-06-13

### Feat
- feat(api): Adding API workflow endpoints:

  - Adding endpoints for:
    - login, registration
    - working with document(s) and statistics for documents
    - collections and statistics for collections
    - working with user
  - Detailed documentation is available [here](http://37.9.53.222/apidocs)

## [1.3.4] - 2025-06-10

### Fix
- fix(structure): Removing relative imports

## [1.3.3] - 2025-06-10

### Fix
- fix(import): Changing module imports

## [1.3.2] - 2025-06-10

### Fix
- fix(container): Changing volume mount in web container

## [1.3.1] - 2025-06-10

### Fix
- fix(container): Fixing the logic of the ```alembic upgrade``` command

## [1.3.0] - 2025-06-10

### Feat
- feat(database): Changing the database structure and relationships between models, adding a new "collection" model
- feat(web): Improving the logic of data validation during registration and authorization
- feat(database): Added database [schema](Schema_db.drawio.png) 

### Fix
- fix(web): Incorrect logic for outputting information on the document was detected. Previously, the TF-IDF value was output in the IDF column, changing the calculation logic
- fix(web): Adding a check and informing about the uniqueness of the document name
- fix(structure): Distribution of functions for working with models in the database, according to logical files

## [1.2.2] - 2025-06-03

### Fix
- fix(container): Changing the name of docker-compose and dockerfile files

## [1.2.1] - 2025-06-03

### Fix
- fix(container): Change container access policy

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