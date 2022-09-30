import requests
import os
import re
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import yaml
COOKIES = {'auth': '1'}
REPO_HREF = 'https://lifechemicals.com/#'
JOB_ROOT = './data/'
SETTINGS = {}

def init(settings_file='./settings.yaml'):
    global SETTINGS
    with open(settings_file, 'r', encoding='utf-8') as f:
        SETTINGS = yaml.load(f, Loader=yaml.Loader)

    if SETTINGS['repo_tree']['job_specified'] or SETTINGS['downloads']['job_specified']:
        if SETTINGS['runtime']['job_name'] == '':
            job_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        else:
            job_name = SETTINGS['runtime']['job_name'].replace('\\','/').replace('/','_')
        job_name += '/'
    else:
        job_name = ''
    SETTINGS['runtime']['job_dir'] = '%s%s' %(JOB_ROOT, job_name)
    SETTINGS['repo_tree']['file_path'] = '%s%srepo.yaml' %(JOB_ROOT, job_name)
    SETTINGS['downloads']['save_dir'] = '%s%sdownloads/' %(JOB_ROOT, job_name)
    if not os.path.exists(JOB_ROOT):
        os.mkdir(JOB_ROOT)
    if not os.path.exists(SETTINGS['runtime']['job_dir']):
        os.mkdir(SETTINGS['runtime']['job_dir'])
    if not os.path.exists(SETTINGS['downloads']['save_dir']):
        os.mkdir(SETTINGS['downloads']['save_dir'])

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
    try:
        start = time.time()
        response = requests.get(url=url, cookies=cookies, headers=headers, stream=True)
        # print(response.text)
        size = 0
        chunk_size = 1024 # 每次下载的数据大小
        content_size = int(response.headers['content-length']) # 下载文件总大小
    
        if response.status_code == 200: #判断是否响应成功
            print('\tDownload started\n\t[File size]: {size:.2f} MB'.format(size = content_size / chunk_size / 1024))   #开始下载，显示下载文件大小
            with open(file_path,'wb') as f: #显示进度条
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
                        print('\r'+'\t[Progress]: %s %.2f%% %.2f MB/s' % ('>' * int(size * 50 / content_size), float(size / content_size * 100), float(MB_speed)), end=' ')
                    else:
                        print('\r'+'\t[Progress]: %s %.2f%% %.2f KB/s' % ('>' * int(size * 50 / content_size), float(size / content_size * 100), float(MB_speed * 1024)), end=' ')
        end = time.time() # 下载结束时间
        print('\n\tDownload completed!, time: %.2fs' % (end - start)) # 输出下载用时时间
    except Exception as e:
        print('\n\tERROR: %s' %(str(e)))
        with open('%slog.txt' %(SETTINGS['runtime']['job_dir']), 'a', encoding='utf-8') as f:
            f.write(os.path.dirname(os.path.abspath(file_path)))
            f.write('\n\t' + os.path.abspath(file_path))
            f.write('\n\t' + file_name)
            f.write('\n\t' + str(e))
            f.write('\n')

def write_data(repo, files_dir, cookies, skip_file = False):
    print('writing data in ' + files_dir)
    for item in repo:
        if item['type'] == 'file':
            fname = item['fname']
            dlink = item['dlink']
            file_path = files_dir + fname
            if skip_file:
                if os.path.exists(file_path):
                    print('skipping file: %s' %(file_path))
                    continue
            print('writing file: %s' %(file_path))
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

def build_tree(driver, root):
    repo = []
    cnt = len(driver.find_elements(by=By.XPATH, value='%s/li'%(root)))
    for i in range(1, cnt+1):
        # file or repo
        sub_root = '%s/li[%s]/ul'%(root,str(i))
        a_tag = driver.find_element(by=By.XPATH, value='%s/li[%s]/a'%(root,str(i)))
        a_tag_text = format_str(a_tag.text)
        a_tag_href = format_str(a_tag.get_attribute('href'))
        if a_tag_href != REPO_HREF:
            # file
            finfo = a_tag_text
            fname = re.match('(.*) \| size', finfo).group(1)
            fsize = re.search('\| size: (.*) \| updated', finfo).group(1)
            fdate = re.search('\| updated: (.*) \|', finfo).group(1)
            item = {
                'type': 'file',
                'fname': fname,
                'dlink': a_tag_href,
                'fsize': fsize,
                'fdate': fdate
            }
            repo.append(item)
        else:
            # repo
            rname = a_tag_text
            item = {
                'type': 'repo',
                'rname': rname,
                'items': build_tree(driver, sub_root)
            }
            repo.append(item)
    return repo

def driver_init(myoption):
    if myoption['browser'] == 'chrome':
        options = webdriver.ChromeOptions()
    elif myoption['browser'] == 'edge':
        options = webdriver.EdgeOptions()
    for i in myoption['options']:
        options.add_argument(i)
    # options.add_experimental_option('detach',True) # 程序结束后保留浏览器窗口
    options.add_experimental_option('excludeSwitches',['enable-logging']) # 关闭selenium控制台提示
    if myoption['driver_path'] == '':
        # apply options
        if myoption['browser'] == 'chrome':
            driver = webdriver.Chrome(options=options)
        elif myoption['browser'] == 'edge':
            driver = webdriver.Edge(options=options)
    else:
        driver_service = Service(myoption['driver_path'])
        if myoption['browser'] == 'chrome':
            driver = webdriver.Chrome(service=driver_service, options=options)
        elif myoption['browser'] == 'edge':
            driver = webdriver.Edge(service=driver_service, options=options)

    driver.implicitly_wait(4)
    driver.maximize_window() # maximize
    driver.get('https://lifechemicals.com/downloads')
    return driver

def get_repo_tree(repo_tree_file):
    if (not SETTINGS['repo_tree']['remote_fetch']) and os.path.exists(repo_tree_file):
        with open(repo_tree_file, 'r', encoding='utf-8') as f:
            repo = yaml.load(f, Loader=yaml.Loader)
    else:
        print('fetching repo tree from remote')
        driver = driver_init(SETTINGS['driver'])
        driver.find_element(by=By.ID, value='open-all').click()
        print('download page loaded')
        repo = build_tree(driver, '//div[@id="downloads_tree"]/ul')
        try:
            with open(repo_tree_file, 'w', encoding='utf-8') as f:
                yaml.dump(repo, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print('WARNING: repo_tree_file (%s) not writable: %s' %(repo_tree_file, str(e)))
    return repo

def download_all(save_dir, cookies=COOKIES.copy()):
    repo = get_repo_tree(repo_tree_file=SETTINGS['repo_tree']['file_path'])
    print('repo tree ready')

    if SETTINGS['downloads']['remote_fetch']:
        with open('%slog.txt' %(SETTINGS['runtime']['job_dir']), 'w', encoding='utf-8') as f:
            from datetime import datetime
            f.write(str(datetime.now()))
            f.write('\n')
        write_data(repo, save_dir, cookies)
    else:
        print('remote fetch disabled in settings')

def main():
    init()
    download_all(save_dir=SETTINGS['downloads']['save_dir'])

if __name__ == '__main__':
    main()
