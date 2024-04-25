
import requests


res = requests.put("http://127.0.0.1:5000/api/blogs/1", json={"title": "бпх", "text": 'pchela', 'image':'wwww', 'user_id': 1})

print(res.status_code, res.reason)
