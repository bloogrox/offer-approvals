run:
	nameko run app

shell:
	nameko shell

test:
	python -m pytest --cov=. --cov-config .coveragerc

up:
	docker-compose up &
