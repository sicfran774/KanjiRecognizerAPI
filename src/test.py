import requests

root = "http://127.0.0.1:5000/"

uri = open('../uri.txt').read()
res = requests.post(root, json={"uri": uri})

print(res.json())
    