import requests

from myScrapy.settings import PROXY_POOL_SERVER

url = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=765&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=python&kt=3&lastUrlQuery=%7B%22pageSize%22:%2260%22,%22jl%22:%22765%22,%22kw%22:%22python%22,%22kt%22:%223%22%7D&_v=0.36034137'


headers = {
    'Host':'fe-api.zhaopin.com',
    'Origin':'https://sou.zhaopin.com',
    'Referer':'https://sou.zhaopin.com/?pageSize=60&jl=765&kw=python&kt=3',
    'User-Agent':"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
}
proxy = requests.get(PROXY_POOL_SERVER).text
print(proxy)
response = requests.get(url, headers=headers, proxies={'http': 'http://' + proxy})
print(response.text)