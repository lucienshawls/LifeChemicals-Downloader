import requests
import os
import re
import time
import yaml
from lxml import etree
COOKIES = {'auth': '1'}


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

def download(url, file_name, file_dir='./downloads/', cookies=COOKIES.copy()):
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
    start = time.time()
    response = requests.get(url=url, cookies=cookies, headers=headers, stream=True)
    # print(response.text)
    size = 0
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    try:
        if response.status_code == 200:   #判断是否响应成功
            print('\tDownload started\n\t[File size]: {size:.2f} MB'.format(size = content_size / chunk_size / 1024))   #开始下载，显示下载文件大小
            with open(file_path,'wb') as f:   #显示进度条
                last_time = time.time()
                speed = 0
                for data in response.iter_content(chunk_size = chunk_size):
                    now_time = time.time()
                    f.write(data)
                    size += len(data)
                    if now_time - last_time > 1 / chunk_size:
                        speed = len(data)/float(now_time-last_time)
                        last_time = time.time()
                    MB_speed = speed / chunk_size / 1024
                    if MB_speed >= 1:
                        print('\r'+'\t[Progress]: %s %.2f%% %.2f MB/s' % ('>' * int(size*50 / content_size), float(size / content_size * 100), MB_speed), end=' ')
                    else:
                        print('\r'+'\t[Progress]: %s %.2f%% %.2f KB/s' % ('>' * int(size*50 / content_size), float(size / content_size * 100), MB_speed * 1024), end=' ')
        end = time.time()   #下载结束时间
        print('Download completed!, time: %.2fs' % (end - start))  #输出下载用时时间
    except:
        print('Error')

def write_data(repo, files_dir, cookies, skip_file = False):
    print('writing data in ' + files_dir)
    for item in repo:
        if item['type'] == 'file':
            fname = item['fname']
            dlink = item['dlink']
            print('writing file: %s' %(files_dir + fname))
            download(dlink, fname, files_dir, cookies)
        else:
            rname = item['rname']
            sub_repo = item['items']
            sub_files_dir = files_dir + rname + '/'
            if not os.path.exists(sub_files_dir):
                os.mkdir(sub_files_dir)
            write_data(sub_repo, sub_files_dir, cookies, skip_file)

def format_str(raw):
    mystr = str(raw).strip().replace('\n','')
    res = re.sub(' [ ]+', ' ', mystr)
    return res

def build_tree(html,root):
    repo = []
    cnt = len(html.xpath('%s/li'%(root))) # 所有项目都是li
    for i in range(1, cnt+1):
        #检查是文件还是文件夹
        sub_root = '%s/li[%s]/ul'%(root,str(i))
        # print(html.xpath(sub_root))
        if html.xpath(sub_root) == []: 
            # file (no /ul) 
            a_tag_text = html.xpath('%s/li[%s]/a/text()'%(root,str(i)))[0]
            a_tag_href = html.xpath('%s/li[%s]/a/@href'%(root,str(i)))[0]
            # # print('%s/li[%s]/a/small/text()'%(root,str(i)))
            # small_tag_text = html.xpath('%s/li[%s]/a/small/text()'%(root,str(i)))[0]
            # finfo = format_str(small_tag_text)
            # fsize = re.search('| size: (.*) |', finfo).group(1)
            # fdate = re.search('| updated: (.*) |', finfo).group(1)
            item = {
                'type': 'file',
                'fname': format_str(a_tag_text),
                'dlink': format_str(a_tag_href),
                # 'fsize': fsize,
                # 'fdate': fdate
            }
            repo.append(item)
        else:
            # repo
            a_tag_text = html.xpath('%s/li[%s]/a/text()'%(root,str(i)))[0]
            item = {
                'type': 'repo',
                'rname': format_str(a_tag_text),
                'items': build_tree(html, sub_root)
            }
            repo.append(item)
    return repo

def get_repo_tree(mode, yaml_file='', html_file=''):
    if mode == 'yaml':
        with open(yaml_file, 'r', encoding='utf-8') as f:
            repo = yaml.load(f, Loader=yaml.Loader)
    elif mode == 'html':
        with open(html_file, 'r', encoding='utf-8') as f:
            raw_html = f.read()
            html = etree.HTML(raw_html)
        repo = build_tree(html, '//div[@id="downloads_tree"]/ul')
        if yaml_file != '':
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml.dump(repo, f, allow_unicode=True, sort_keys=False)
    elif mode == selenium:
        repo = []
    else:
        repo = []
    return repo

def download_all(mode, files_dir='./downloads/', cookies=COOKIES.copy()):
    files_dir.replace('\\', '/')
    if files_dir[-1] != '/':
        files_dir += '/'
    if not os.path.exists(files_dir):
        os.mkdir(files_dir)
    
    if mode == 'yaml':
        repo = get_repo_tree(mode=mode, yaml_file='./repo/repo.yaml')
    print('ready')
    write_data(repo, files_dir, cookies)

def main():
    # cookies = login(get_credentials()) 
    download_all(mode='yaml')

if __name__ == '__main__':
    main()