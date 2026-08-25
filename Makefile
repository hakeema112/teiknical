.PHONY: setup pipeline dashboard
 
setup:
	pip install -r requirements.txt
 
pipeline:
	python pipeline.py
 
dashboard:
	python -m http.server 8000 --directory output
 
