.PHONY: worker beat

worker:
	.venv\Scripts\python -m celery -A celery_worker.celery worker --loglevel=info -P solo

beat:
	.venv\Scripts\python -m celery -A celery_worker.celery beat --loglevel=info