import requests
from http.client import HTTPResponse

r = requests.get('http://us1-external-sources.iptvserver.tv:80/live/kkkrkDp2a9KNwAwGzpb/QT94uK5NNQw4r4Qs/481.ts', stream=True)

print(r.headers)