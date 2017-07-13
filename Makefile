run:
	nameko run app

shell:
	nameko shell

pytest:
	python -m pytest --cov=. --cov-config .coveragerc

up:
	docker-compose up &
