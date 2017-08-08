#! coding=utf8
import multiprocessing, Queue
import os, sys
import time
from multiprocessing import Process, Manager
import re
import json

# 遍历指定目录，显示目录下的所有文件名
class Consumer(multiprocessing.Process):
    def __init__(self, result_list, queue, webshell_rules):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.webshell_rules = webshell_rules
        self.result_list = result_list

    def run(self):
        try:
            while not self.queue.empty():
                file_name = self.queue.get(True, 1)

                fopen = open(file_name, 'r')
                filestr = fopen.read()
                result = []
                for rule in self.webshell_rules:
                    rule = rule.strip()
                    result = re.findall(rule, filestr)
                    if result:
                            code = self.get_code(file_name, rule)
                            result_dict = {
                                "regex": rule,
                                "code": code,
                                "file_name": file_name
                            }
                            self.result_list.append(result_dict)
                fopen.close()
        except Exception,e :
            print e

    def get_code(self, file_name, rule):
        try:
            fopen = open(file_name, 'r')
            lines = fopen.readlines()
            for line in lines: 
                result = re.findall(rule, line)
                if result:
                    return line
        finally:
            fopen.close()


def list_dictionary_codes(root_dir):
    queue = multiprocessing.Queue(0)
    for parent, dirNames, fileNames in os.walk(root_dir):
        for name in fileNames:
            ext = ['.php','.jsp', 'java']
            if name.endswith(tuple(ext)):
                queue.put( os.path.join(parent, name))
    return queue

def read_rule(rule_file_path):
    list_webshell = []
    webshell_txt = open(rule_file_path, 'r').readlines()
    for i in webshell_txt:
        list_webshell.append(i)
    return list_webshell

if __name__=='__main__':    

    file_path = sys.argv[1]    #填代码目录
    webshell_rule_path = "./rule.txt"

    print "[*] 扫描中...."
    paths_list = list_dictionary_codes(file_path)
    webshell_rules = read_rule(webshell_rule_path)

    processed = []
    mgr = multiprocessing.Manager()
    result_list = mgr.list()

    for i in range(4):
        processed.append(Consumer(result_list, paths_list, webshell_rules))
    for i in range(4):
        processed[i].start()
    for i in range(4):
        processed[i].join(10)
    for result in result_list:
        print json.dumps(result, sort_keys=True, indent=4)
    print "[+] 扫描完成...."
    
