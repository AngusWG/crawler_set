#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/12/17 22:32 
# @author  : zza
# @Email   : 740713651@qq.com
import hashlib
import os
import shutil
from tqdm import tqdm

r = {}


def md5sum(filename):
    f = open(filename, 'rb')
    md5 = hashlib.md5()
    while True:
        fb = f.read(8096)
        if not fb:
            break
        md5.update(fb)
    f.close()
    return md5.hexdigest()


def is_empty_dir(_path):
    if os.path.isdir(_path):
        if len(os.listdir(_path)) == 0:
            os.rmdir(_path)
            return True


def move_file(a, b):
    while True:
        try:
            # file_name = os.path.basename(a)
            shutil.move(a, os.path.join(b))
            break
        except shutil.Error as err:
            print(err)
        except FileNotFoundError as err:
            pass


def do_files(param):
    print(param)
    if param.endswith(".xml"):
        os.remove(param)
        return
    md5 = md5sum(param)
    key = r.get(md5)
    if key is None:
        r[md5sum(param)] = param
    else:
        if key == param:
            return
        else:
            print(key, param)
            if os.path.exists(key):
                move_file(key, r"W:/same/")
            os.remove(param)


def server(_path):
    a = os.walk(_path)

    for root, dirs, files in tqdm(a):
        if '.git' in root:
            continue
        if '.idea' in root:
            continue
        if is_empty_dir(root):
            continue
        for file in files:
            do_files(os.path.join(root, file))


if __name__ == '__main__':
    server(r'W:\tumblr')
    server(r'D:\tumblr')
