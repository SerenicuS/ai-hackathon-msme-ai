1. get /suggest-orders-smart - suggestive Ai decision on how many cacao do you need and what supplier to call


2. post /update-scores - updating the score of suppliers and rank them


Install these:

```bash
pip install fastapi uvicorn pandas sqlalchemy psycopg2-binary prophet
```

<br />

then run the main.py using:
```bash
uvicorn warehouse_app:app --reload
```
