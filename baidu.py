# -*- coding: utf-8 -*-
# 导入所需模块
import requests
import re
import os
from urllib.request import urlretrieve
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib

os.chdir(os.path.dirname(os.path.realpath(__file__)))  # 设置文件保存的位置 如：os.chdir('D:/')


# 获取URL信息
def get_url(key, pages, start_p=0, start_year='-', end_year='+'):  # 关键字、页数（每页10篇文献）、起始页
    urls = []
    for i in range(0 + start_p, pages + start_p):
        # urls.append('https://xueshu.baidu.com/s?wd=' + key
        #             + '&pn='+str(i*10) +'&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sort=sc_time',%())
        urls.append(
            'https://xueshu.baidu.com/s?wd={wd}&pn={pn}&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sort=sc_time&bcp=2&sc_f_para=sc_tasktype={{firstAdvancedSearch}}&sc_from=&sc_as_para=&filter=sc_year={{{start_year},{end_year}}}'.format(
                wd=key, pn=i * 10, start_year=start_year, end_year=end_year))
    return urls



# 设置请求头
headers = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Referer': 'https://googleads.g.doubleclick.net/'
}


# 获取相关论文的DOI列表
def get_paper_link(headers, url):
    response = requests.get(url=url, headers=headers)
    res1_data = response.text
    # 找论文链接
    paper_link = re.findall(r'<h3 class=\"t c_font\">\n +\n +<a href=\"(.*)\"',
                            res1_data)

    doi_list = []  # 用一个列表接收论文的DOI
    for link in paper_link:
        paper_link = link + '/' if 'https://' in link or 'http://' in link else 'https://' + link + '/'
        print(paper_link)
        response2 = requests.get(url=paper_link, headers=headers)
        res2_data = response2.text
        # 提取论文的DOI
        try:
            paper_doi = re.findall(r'\'doi\'}\">\n +(.*?)\n ', res2_data)
            if str(10) in paper_doi[0]:
                doi_list.append(paper_doi)
        except:
            pass

    return doi_list


def getFile(save_path, url):
    file_name = url.split('/')[-1]
    u = urllib.request.urlopen(url)
    f = open(os.path.join(save_path,file_name), 'wb')

    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        f.write(buffer)
    f.close()
    print("Sucessful to download" + " " + file_name)



def doi_download(headers, key, pages, start_p=0, start_year='-', end_year='+'):
    dir_path = os.getcwd()
    pages_url = get_url(key, pages, start_p, start_year, end_year)
    print(pages_url)
    doi_list = []
    for purl in pages_url:
        doi_list += get_paper_link(headers, purl)
    print(doi_list)
    base_url = 'https://sci-hub.st/'
    for doi in doi_list:
        print('\n', doi, doi[0])
        res = requests.post(base_url, data={'request': doi[0]})
        print('\n响应结果是：', res)
        print('访问的地址是：', res.url)
        # debug
        # soup = BeautifulSoup(res.text, features='lxml')
        # print(soup)
        # print(soup.button)
        # pdf_URL = soup.button['onclick']
        # print(pdf_URL[::-1])
        # print(re.search(re.compile('location.href='),soup.button['onclick']))
        # print(re.search(re.compile('fdp.*?//'), pdf_URL[::-1]).group())
        try:
            soup = BeautifulSoup(res.text, features='lxml')
            pdf_URL = soup.button['onclick']
        except:
            print("解析失败！")
            continue

        pdf_URL = re.search(re.compile('fdp.*?//'), pdf_URL[::-1]).group()[::-1][1::]
        print(pdf_URL)
        if not re.search(re.compile('^https://'), pdf_URL):
            pdf_URL = 'https:/' + pdf_URL
        print('PDF的地址是：', pdf_URL)
        name = re.search(re.compile('fdp.*?/'), pdf_URL[::-1]).group()[::-1][1::]
        print('PDF文件名是：', name)
        print('保存的位置在：', dir_path)

        try:
            print('\n正在下载')
            getFile(dir_path,pdf_URL)

        except:
            print("该文章为空")



# 检索及下载
key = input("请输入您想要下载论文的关键词（英文）：")
start_p = (input("请输入查询起始页（数字，0，可选）："))
num = input("请输入下载论文总数（数字）：") or 10
start_year = input("请输入论文起始年（数字，可选）：")
end_year = input("请输入论文终止年（数字，可选）：")
if start_p == '':
    start_p = 0
else:
    start_p = int(start_p)
if start_year == '':
    start_year = '-'
    if end_year == '':
        start_year = 2000

if end_year == '':
    end_year = '+'
pages = int(num) // 10
doi_download(headers, key, pages, start_p, start_year=start_year, end_year=end_year)


