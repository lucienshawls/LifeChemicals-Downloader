import requests
import os

def get_credentials(file_path='credentials.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        credentials = f.read().strip().split()[:2]
    return credentials

def login(credentials):
    s = requests.session()
    # 访问登录页

    headers = {
        'authority': 'shop.lifechemicals.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50',
    }

    response = s.get('https://shop.lifechemicals.com/login?go=https://lifechemicals.com/downloads', headers=headers)
    # 发送登录请求

    headers = {
        'authority': 'shop.lifechemicals.com',
        'accept': 'application/vnd.api+json, application/json',
        'accept-language': 'en-US,en;q=0.9',
        'api-key': '68615f7b-8caf-4b8c-9902-c47279bc0e99','dnt': '1',
        'origin': 'https://shop.lifechemicals.com',
        'referer': 'https://shop.lifechemicals.com/login?go=https://lifechemicals.com/downloads',
        'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50',
    }

    json_data = {
        'email': credentials[0],
        'password': credentials[1],
        'session_key': None,
    }

    response = s.post('https://shop.lifechemicals.com/api/accounts/token/', headers=headers, json=json_data)

    # 访问下载页
    response = s.get('https://lifechemicals.com/downloads',headers=headers)
    cookies = response.cookies.get_dict()
    cookies['pathname'] = '%2Fdownloads'
    cookies['auth'] = '1'
    return cookies

def download(url, file_name, file_dir='./downloads/', cookies={'auth': '1'}):
    file_dir.replace('\\', '/')
    if file_dir[-1] != '/':
        file_dir += '/'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_path = file_dir + file_name

    headers = {
        'authority': 'lifechemicals.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9','dnt': '1',
        'referer': 'https://lifechemicals.com/downloads',
        'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50',
    }
    response = requests.get(url=url, cookies=cookies, headers=headers)

    with open(file_path,'wb') as f:
        f.write(response.content)

def main():
    # cookies = login(get_credentials())
    url = 'https://lifechemicals.com/download.php?path=Pre-plated+Fragment+Screening+Sets%2FPre-plated+Fragment+Diversity+Sets%2FLC_Preplated_Fragment_Diversity_Sets_Description.pdf'
    download(url,'Preplated Fragment Diversity Sets Description.pdf','downloads/Pre-plated Fragment Screening Sets/Pre-plated Fragment Diversity Sets')

    pass

if __name__ == '__main__':
    main()