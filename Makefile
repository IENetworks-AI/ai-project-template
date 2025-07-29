setup:
	pip install -r requirements.txt

extract:
	python src/preprocess.py

features:
	python src/feature_engineering.py

train:
	python src/train.py

evaluate:
	python src/evaluate.py
