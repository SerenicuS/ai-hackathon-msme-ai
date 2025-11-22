1. get /suggest-orders-smart - suggestive Ai decision on how many cacao do you need and what supplier to call


2. post /update-scores - updating the score of suppliers and rank them


Install these - pip install fastapi uvicorn pandas sqlalchemy psycopg2-binary prophet

then run the main.py using > uvicorn warehouse_app:app --reload
