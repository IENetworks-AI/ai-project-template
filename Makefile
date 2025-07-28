install:
	pip install -r requirements.txt

preprocess:
	python src/preprocess.py

train:
	python src/train.py

test:
	pytest tests/