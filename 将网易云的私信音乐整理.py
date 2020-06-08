#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2019/12/19 9:36
# @author  : zza
# @Email   : 740713651@qq.com
# @File    : 将网易云的私信音乐整理.py
"""
该脚本会保存每天新私信里最后几首歌曲到tmp_save_dir
1.在Chrome上登录自己的网易云帐号t
2.创建tmp_save_dir
然后运行脚本
"""
import os
import glob
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

song_dir = "tmp_save_dir"


def init_driver():
    driver_path = ""
    if not os.path.exists("chromedriver.exe"):  # 无驱则需要下载
        # 本地项目 复制驱动
        if "crawler_set" in os.path.abspath(__file__):
            driver_path = glob.glob('chromedriver.exe')[0]
        else:  # 单个文件 下载驱动
            pass

    user_cookies = "".join([os.path.expanduser('~'), r"\AppData\Local\Google\Chrome\User Data"])

    option = webdriver.ChromeOptions()
    option.add_argument("--user-data-dir={}".format(user_cookies))  # 设置成用户自己的数据目录

    try:
        driver = webdriver.Chrome(driver_path, options=option)
        driver.implicitly_wait(5)
        return driver
    except WebDriverException:
        print("请先关掉所有的Chrome")
        exit(-2)


def get_private_detail():
    # 点击私信后
    driver.get("https://music.163.com/#/msg/m/private")
    driver.switch_to.frame("contentFrame")
    new_msg_items = driver.find_elements_by_xpath('//i[@class="u-bub"]/b[@class="f-alpha"]/..//parent::*//a')
    private_detail_url_set = set()
    for i in new_msg_items:
        _, singer_id = i.get_attribute("href").split("?")
        private_detail_url_set.add("https://music.163.com/#/msg/m/private_detail?" + singer_id)
    return private_detail_url_set


def get_song_url_from_album_set(url):
    song_set = set()
    # 歌曲页面保存
    driver.get(url)
    driver.switch_to.frame("contentFrame")
    url_list = driver.find_elements_by_xpath('//a[contains(@href, "/song?id")]')
    for item in url_list:
        if "伴奏" in item.text:
            break
        _, song_id = item.get_attribute("href").split("?id=")
        song_set.add("https://music.163.com/#/song?id=" + song_id)
        song_name = item.find_element_by_xpath("./b").get_attribute("title")
        print(song_name, end=" ")
    return song_set


def get_song_url_from_private_detail(url):
    album_set = set()
    song_set = set()
    # 歌曲页面保存
    driver.get(url)
    driver.switch_to.frame("contentFrame")
    url_list = driver.find_elements_by_xpath('//a[contains(@href, "album?id")]')
    for item in url_list[-2:]:
        _, album_id = item.get_attribute("href").split("?id=")
        album_set.add("https://music.163.com/#/album?id=" + album_id)

    url_list = driver.find_elements_by_xpath('//a[contains(@href, "/song?id")]')
    for item in url_list[-2:]:
        _, song_id = item.get_attribute("href").split("?id=")
        song_set.add("https://music.163.com/#/song?id=" + song_id)

    for album_url in album_set:
        song_set.update(get_song_url_from_album_set(album_url))
    return song_set


def save_song(url):
    print("[{}] start".format(url))
    driver.get(url)
    driver.switch_to.frame("contentFrame")
    driver.find_element_by_xpath('//*[contains(text(), "收藏")]').click()
    driver.find_element_by_xpath('//*[contains(text(), "{}")]'.format(song_dir)).click()


driver = init_driver()
if not os.path.exists("tmp.txt"):
    # 获取私信用户列表
    private_detail_url_set = get_private_detail()
    print("private_detail_url_set len={}".format(len(private_detail_url_set)))
    # 获取歌曲id
    song_url_set = set()
    for private_detail_url in private_detail_url_set:
        song_url_set.update(get_song_url_from_private_detail(private_detail_url))
        print("song_url_set len={}".format(len(song_url_set)))
    with open("tmp.txt", "w", encoding="utf8") as f:
        f.write("\n".join(song_url_set))
else:
    with open("tmp.txt", "r", encoding="utf8") as f:
        data = f.read()
    song_url_set = data.split("\n") if data else []
# 保存歌曲
for song_url in song_url_set:
    save_song(song_url)
os.remove("tmp.txt")
driver.close()
