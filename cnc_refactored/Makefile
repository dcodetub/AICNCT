.PHONY: all install train signals backtest test clean

all: install train signals

install:
	pip install -r requirements.txt

train:
	python train_model.py

signals:
	python main.py

backtest:
	python backtest.py

test:
	pip install pytest
	pytest tests/ -v

clean:
	rm -f xgb_model.pkl
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
