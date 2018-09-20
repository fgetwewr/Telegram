import requests

proxy = 'http://' + requests.get('http://127.0.0.1:5555/random').text
print(proxy)
proxies = {'http': proxy}
response = requests.get(url='http://www.gatherproxy.com/zh/proxylist/anonymity/?t=Elite', proxies=proxies)
print(response.text)
print(requests.get('http://example.org', proxies=proxies))