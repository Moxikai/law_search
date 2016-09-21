#!/usr/bin/env python
#coding:utf-8
"""
国务院法律全文查询
"""

import os
from time import sleep
from time import ctime
import hashlib
from random import uniform
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import requests

from model import session,Law
class LawSearch():

    def __init__(self):

        self.headers = {'Host':'search.chinalaw.gov.cn',
                        'Origin':'http://search.chinalaw.gov.cn',
                        'Cache-Control':'max-age=0',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Refer':'http://search.chinalaw.gov.cn/v4luceneResult/fgSearchAdvance2.jsp',
                        'Accept-Encoding':'zh-CN,zh;q=0.8',
                        'Content-Type':'application/x-www-form-urlencoded',
                        }
        self.headers2 = {'Host':'fgk.chinalaw.gov.cn',
                        'Cache-Control':'max-age=0',
                        'Upgrade-Insecure-Requests':'1',
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Refer':'http://search.chinalaw.gov.cn/v4luceneResult/fgSearchAdvance2.jsp',
                        'Accept-Encoding':'zh-CN,zh;q=0.8',
                        }

        self.urlPost = 'http://search.chinalaw.gov.cn/v4luceneResult/fgSearchAdvance2.jsp'
        self.postDataDefault = {'pageid':1,
                                'd_channel':'dffg',
                                'fromwhere':'chinalaw_article',
                                'key':'',
                                'title':'',
                                'category':'',
                                'sourcetype':'',
                                'area':'',
                                'startTime':'',
                                'endTime':'',
                                'indexPathName':'indexPath2'}


        self.baseDir = os.path.dirname(__file__)
        self.htmlCacheFolder = os.path.join(self.baseDir,'.cache')
        self.errorInfoPath = os.path.join(self.baseDir,'errorInfo.txt')
        self.pageNo = 1
        self.downloadPageCount = 0
        self.downloadErrorCount = 0
        self.crawlDataCount = 0
        self.crawlErrorCount = 0

    def checkLoadTimes(self):
        pass


    def createFolder(self):

        if os.path.exists(self.htmlCacheFolder):
            return True
        else:
            os.makedirs(self.htmlCacheFolder)
            return True

    def downloadListPage(self,pageid):

        self.postDataDefault['pageid'] = pageid
        try:
            r = requests.post(url=self.urlPost,
                              data=self.postDataDefault,
                              headers=self.headers)
            if r.status_code == 200:
                #print r.content
                self.downloadPageCount += 1
                return r.content
            else:
                return False
        except Exception as e:
            print '下载列表页第%s页失败'%pageid
            self.saveErrorInfo(*['列表页:',pageid,'下载失败',ctime()])

    def downloadDetailPage(self,url):

        r = requests.get(url,headers = self.headers2)
        if r.status_code == 200:
            print '页面%s下载成功'%(url)
            self.downloadPageCount += 1
            return r.content
        else:
            print '下载%s详细页面失败'%url
            self.saveErrorInfo(*['详细页:',url,'下载失败',ctime()])
            return False

    def getSignName(self,string):

        return hashlib.sha1(string).hexdigest()

    def saveHtmlCache(self,content,name):

        name = os.path.join(self.htmlCacheFolder,name+'.html')
        try:
            with open(name,'w') as f:
                f.write(content)
        except Exception as e:
            print '保存混存文件%s出错'%(name)
            return False

    def checkHtmkCache(self,name):

        name = os.path.join(self.htmlCacheFolder,name+'.html')
        return True if os.path.exists(name) else False


    def loadHtmlCache(self,name):

        name = os.path.join(self.htmlCacheFolder,name+'.html')
        try:
            with open(name,'r') as f:
                return f.read()
        except Exception as e:
            print '加载缓存文件%s出错'%name
            return False

    #保存下载错误信息
    def saveErrorInfo(self,*args):

        str = ''.join(args)
        with open(self.errorInfoPath,'a') as f:
            f.write(str)
        print '错误信息已储存!'

    def getListContent(self,pageid):

        name = self.getSignName(self.urlPost)
        name = name + str(pageid)
        if self.checkHtmkCache(name):
            return self.loadHtmlCache(name)
        else:
            content = self.downloadListPage(pageid)
            self.saveHtmlCache(content,name)
            return content

    def getDetailContent(self,url):

        name = self.getSignName(url)
        if self.checkHtmkCache(name):
            return self.loadHtmlCache(name)
        else:
            content = self.downloadDetailPage(url)
            self.saveHtmlCache(content,name)
            return content


    def parseListPage(self,content):

        if content:
            soup = BeautifulSoup(content,'lxml')
            try:
                return [[td.a.get('href'),td.a.get_text()] for td in soup.find_all('td',class_='f')]
            except Exception as e:
                print '解析列表页数据失败','\n',e
                return False
        else:
            return False
    def parseNextUrl(self,content):

        if content:
            status = 0
            soup = BeautifulSoup(content,'lxml')
            for item in soup.find_all('a'):
                if item.get_text() == '下一页' and item.get('href'):
                    status = 1
                    break
            return status
        else:
            return 2


    def parseDetailPage(self,content,url):

        if content:
            soup = BeautifulSoup(content,'lxml')
            try:

                id = self.getSignName(url)
                title = soup.find('div',class_='mtitle').get_text()
                fonts = soup.find_all('font',color='red')
                type = fonts[0].get_text()
                publishDepartment = fonts[1].get_text()
                status = fonts[2].get_text()
                publishDate = fonts[3].get_text()
                effectDate = fonts[4].get_text()
                loseEffectDate = fonts[5].get_text()
                content = ''.join(unicode(item) for item in soup.find_all('table',class_='aarticle')[1].contents)
                return {'id':id,
                        'title':title,
                        'type':type,
                        'publishDepartment':publishDepartment,
                        'status':status,
                        'publishDate':publishDate,
                        'effectDate':effectDate,
                        'loseEffectDate':loseEffectDate,
                        'content':content,
                        }

            except Exception as e:
                print '解析详细页面%s出错,请检查'%url,e
        else:
            return False


    def checkDumplicate(self,id):

        law = session.query(Law).filter(Law.id == id).first()
        return True if law else False

    def saveToSQLite(self,**kwargs):
        try:
            if self.checkDumplicate(kwargs['id']):
                pass
            else:
                law = Law(id = kwargs['id'],
                          title = kwargs['title'],
                          type = kwargs['type'],
                          publishDepartment = kwargs['publishDepartment'],
                          status = kwargs['status'],
                          publishDate = kwargs['publishDate'],
                          effectDate = kwargs['effectDate'],
                          loseEffectDate = kwargs['loseEffectDate'],
                          content = kwargs['content'])
                session.add(law)
                session.commit()
                self.crawlDataCount += 1
                print '记录%s保存成功'%(kwargs['title'])
        except Exception as e:
            self.crawlErrorCount += 1

    def run(self):
        status = 1
        pageNo = 1
        while status == 1:
            try:
                listContent = self.getListContent(pageNo)
                list = self.parseListPage(listContent)
                for item in list:
                    sleep(uniform(2,5))
                    url = item[0]
                    id = self.getSignName(url)
                    #检测重复
                    if not self.checkDumplicate(id):
                        detailContent = self.getDetailContent(url)
                        data = self.parseDetailPage(detailContent,url)
                        self.saveToSQLite(**data)
                        sleep(uniform(2, 5))
                    else:
                        print '记录%s已存在,不需重复解析'%(item[1])

                if not self.parseNextUrl(listContent):
                    status = 0
                pageNo += 1

            except Exception as e:
                print '程序出现错误:','\n',e
                sleep(10)
            else:
                print '下载页面数量:%s,下载失败数量:%s,采集数据数量:%s,采集失败数量:%s,当前列表页码%s'\
                      %(self.downloadPageCount,self.downloadErrorCount,self.crawlDataCount,self.crawlErrorCount,self.pageNo)

if __name__ == '__main__':

    test = LawSearch()
    test.createFolder()
    test.run()




