# Celery Event Service

This Celery service is responsible for periodically fetching events from an external provider's API, processing the XML data, and storing the events in a PostgreSQL database. The service is designed to handle large amounts of data efficiently using Celery tasks.

## Functionality

Scheduled Fetching: The service periodically fetches event data from an external API every 30 seconds (or a configured interval).
XML Data Processing: The fetched XML data is parsed and relevant event information is extracted.
PostgreSQL Storage: The processed events are stored or updated in a PostgreSQL database, ensuring no duplicate data is stored.

## How to use it

* Clone the repository

* Create virtual env:

    - python -m venv .venv
    - source .venv/bin/activate    (For Windows: .venv\Scripts\activate)

* Install dependencies
    
    - pip install -r requirements.txt

* Execute make commands

    - make worker
    - make beat

## Prerequisites

Have Flask, PostgreSQL and Redis running (https://github.com/FeverCodeChallenge/PatricioGhillino/tree/master)