import os
import requests
from bs4 import BeautifulSoup
import pymongo
import csv
import uuid

s = requests.session()


def login():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Referer': 'http://hkbbcc.xyz/forum.php'
    }

    login_data = {
        'fastloginfield': 'username',
        'username': 'ronngx',
        'password': 'b75d3vvv',
        'quickforward': 'yes',
        'handlekey': 'ls'
    }
    login_url = 'http://hkbbcc.xyz/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'

    res = s.post(login_url, data=login_data, headers=headers)


def insert_to_mongo(dic):
    Client = pymongo.MongoClient()
    db = Client['bisitequ_gaoqingwuma_database']
    collection = db['bisitequ_gaoqingwuma_collection']
    db.posts.insert_one(dic).inserted_id


def get_title_list_mongo(page):
    """
    写入数据库
    """
    url = "http://hkbbcc.xyz/forum-454-" + str(page) + ".html"
    res = s.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html5lib")
    title_list = soup.select('a.xst')  # 所有链接的列表

    for t in title_list:
        title = t.get_text()  # 标题
        url = 'http://hkbbcc.xyz/' + t['href']  # 链接
        dic = {'title': title, 'url': url}
        insert_to_mongo(dic)


def run_get_title_list_mongo():
    login()
    for i in range(1, 1001):
        print('开始获取第', str(i), '页,', '共1000页,', '进度=', str(i / 1000 * 100), '%')
        get_title_list_mongo(i)
    print('done!')


def get_title_list_csv(page, output_writer):
    """
    写入csv
    """
    url = "http://hkbbcc.xyz/forum-454-" + str(page) + ".html"
    res = s.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html5lib")
    title_list = soup.select('a.xst')  # 所有链接的列表
    for t in title_list:
        title = ''.join(t.get_text().split())  # 标题
        url = 'http://hkbbcc.xyz/' + t['href']  # 链接
        output_writer.writerow([title, url])


def run_get_title_list_csv():
    login()
    outputfile = open('title_list.csv', 'w', newline='')
    output_writer = csv.writer(outputfile)
    for i in range(1, 1001):
        print('开始获取第', str(i), '页,', '共1000页,', '进度=', str(i / 1000 * 100), '%')
        get_title_list_csv(i, output_writer)
    outputfile.close()
    print('done!')


def get_page_detail(url, path):
    """
    获取指定url帖子详情
    :param url: 帖子的url
    :return: None
    """
    res = s.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html5lib")
    img_list = soup.select('ignore_js_op > img')
    img_list = img_list[: -1]
    for i in img_list:
        ir = s.get('http://hkbbcc.xyz/' + i['zoomfile'])
        if ir.status_code == 200:
            open(path + '/' + str(uuid.uuid1()) + '.jpg', 'wb').write(ir.content)



def run_get_all_page_detail():
    """
    遍历title_list.csv中的所有帖子，将图片保存在文件夹中
    :return:
    """
    login()
    file = open('title_list.csv')
    reader = csv.reader(file)
    for row in reader:
        pic_path = os.getcwd() + '/pic/' + ''.join(row[0].split())
        os.makedirs(pic_path)
        print('正在下载第' + str(reader.line_num) + '行')
        get_page_detail(row[1], pic_path)


if __name__ == "__main__":
    # run_get_title_list_csv()
    run_get_all_page_detail()
