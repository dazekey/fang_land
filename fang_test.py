#!/usr/bin/python
# encoding: utf-8

"""
@author: ocean
@contact: dazekey@163.com
@file:fang_test.py
@time:2017/3/4 13:52
"""

import urllib
import urllib2
import re
import cookielib
import gzip
import StringIO
import lxml.html
from lxml import etree
import csv
import time

class fang_land:

    #初始化
    def __init__(self):
        #初始连接
        self.init_url = "http://land.fang.com/market/510100________1_0_1.html"
        # 加入报头
        self.headers = {
            'Referer': 'http://sh.lianjia.com/ershoufang/d1',
            'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

        # 加入代理
        self.enable_proxy = True
        # proxy_handler = urllib2.ProxyHandler({"http": '101.231.67.202:808'})
        # 调试阶段，不设置代理
        self.proxy_handler = urllib2.ProxyHandler({})

        # 加入cookies
        self.enable_cookie = True
        # 设置cookie
        self.cookie = cookielib.LWPCookieJar()
        # cookie处理器
        self.cookie_handler = urllib2.HTTPCookieProcessor(self.cookie)

        # 设置opener
        self.opener = urllib2.build_opener(self.proxy_handler, self.cookie_handler, urllib2.HTTPHandler)

        #设置CSV初始化的开关
        self.control = False

    def getPage(self,url):
        request = urllib2.Request(url, headers = self.headers)
        response = self.opener.open(request)
        content = response.read()

        #由于网页被加密，显示乱码，分析后得到结果是压缩了
        content = StringIO.StringIO(content)
        gzipper = gzip.GzipFile(fileobj=content)
        content = gzipper.read().decode('gbk')
        # print content
        return content

    def getProvinceDatas(self,url):
        content = self.getPage(url)

        #使用xpath分析网页
        # 用lml.html.fromstring和tostring模块处理网页
        tree = lxml.html.fromstring(content)
        # tree = etree.HTML(content)
        html = lxml.html.tostring(tree,pretty_print=True)
        # html = etree.tostring(tree)
        # print html

        #获得省份和url
        Province_urls = tree.xpath('//span[@class="w866 fr"]/a/@href')
        # for Province_url in Province_urls:
        #     print Province_url
        Provinces = tree.xpath('//span[@class="w866 fr"]/a')
        # print Provinces
        # for Province in Provinces:
        #     print Province.text
        Province_datas = []
        i=0
        while i < len(Province_urls):
            Province_url = "http://land.fang.com"+Province_urls[i]
            Province = Provinces[i].text
            Province_datas.append([Province,Province_url])
            i +=1

        for data in Province_datas:
            print data[0],data[1]

        return Province_datas



    # 获取项目信息：
    def getListDatas(self,url):
        content = self.getPage(url)
        tree = lxml.html.fromstring(content)
        html = lxml.html.tostring(tree, pretty_print=True)

        #获得标题
        titles = tree.xpath('//dl[@class="llist01"]/dd/div/h3/a/@title')
        # for title in titles:
        #     print title

        #获得son_urls
        son_urls = tree.xpath('//dl[@class="llist01"]/dd/div/h3/a/@href')
        # for son_url in son_urls:
        #     print son_url

        #获得推出时间
        gettimes = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[1]/td[1]')
        # for gettime in gettimes:
        #     print gettime.text

        #成交状态
        deal_statements  = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[1]/td[2]')
        # for deal_statement in deal_statements:
        #     print deal_statement.text

        #土地面积
        land_areas = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[2]/td[1]')
        # for land_area in land_areas:
        #     print land_area.text

        #所属地区
        districts = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[2]/td[2]')
        # for district in districts:
        #     print district.text

        #规划建筑面积
        planning_construction_areas = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[3]/td[1]')
        # for planning_consturction_area in planning_construction_areas:
        #     print planning_consturction_area.text

        #规划用途
        planning_usages = tree.xpath('//dl[@class="llist01"]/dd/div/table/tbody/tr[3]/td[2]')
        # for planning_usage in planning_usages:
        #     print planning_usage.text

        #土地编号
        land_No_s = tree.xpath('//div[@class="lr_main01 fr"]/span/b')
        # for land_No in land_No_s:
        #     print land_No.text

        datas = []
        son_datas = []
        i=0
        while i < len(titles):
            title = titles[i]
            son_url = "http://land.fang.com"+son_urls[i]
            gettime = gettimes[i].text
            deal_statement = deal_statements[i].text
            land_area =land_areas[i].text
            district = districts[i].text
            planning_construction_area = planning_construction_areas[i].text
            planing_usage =planning_usages[i].text
            land_No = land_No_s[i].text

            datas.append([title,son_url,gettime,deal_statement,land_area,district,planning_construction_area,planing_usage,land_No])

            son_data = self.getSonPageDatas(son_url)
            son_datas.append(son_data)
            #每提取一个子页面休息一秒
            time.sleep(0)
            i += 1
            # return son_datas

        # for data in datas:
        #     print data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8]

        return son_datas

    #获得子页面上的信息
    def getSonPageDatas(self,url):
        content = self.getPage(url)
        tree = lxml.html.fromstring(content)
        html = lxml.html.tostring(tree, pretty_print=True)

        #标题
        title = tree.xpath('//div[@class="tit_box01"]')
        title = title[0].text
        # print title

        #地块编号
        land_No = tree.xpath('//span[@class="gray2"]')
        land_No = land_No[0].text

        #土地基本信息
        #地区
        Province = tree.xpath('//div[@class="p1015"]/table/tbody/tr[1]/td[1]/a')
        Province = Province[0].text
        # print Province

        #城市
        city = tree.xpath('//div[@class="p1015"]/table/tbody/tr[1]/td[2]/a')
        city = city[0].text
        # print city

        #总面积
        total_area = tree.xpath('//div[@class="p1015"]/table/tbody/tr[2]/td[1]/em')
        total_area = total_area[0].text
        # print total_area

        #建筑面积
        construction_area = tree.xpath('//div[@class="p1015"]/table/tbody/tr[2]/td[2]/em')
        construction_area = construction_area[0].text
        # print construction_area

        #规划建筑面积
        planning_construction_area = tree.xpath('//div[@class="p1015"]/table/tbody/tr[3]/td[1]/em')
        planning_construction_area = planning_construction_area[0].text
        # print planning_construction_area

        #代征面积
        proxy_area = tree.xpath('//div[@class="p1015"]/table/tbody/tr[3]/td[2]/em')
        proxy_area = proxy_area[0].text
        # print proxy_area

        #容积率
        plot_ratio = tree.xpath('//div[@class="p1015"]/table/tbody/tr[4]/td[1]')
        plot_ratio = plot_ratio[0].xpath('string()')[4:]
        # print plot_ratio

        #绿化率
        green_ratio = tree.xpath('//div[@class="p1015"]/table/tbody/tr[4]/td[2]')
        green_ratio = green_ratio[0].xpath('string()')[4:]
        # print green_ratio

        #商业比例
        commercial_ratio = tree.xpath('//div[@class="p1015"]/table/tbody/tr[5]/td[1]')
        commercial_ratio = commercial_ratio[0].xpath('string()')[5:]
        # print commercial_ratio

        #建筑密度
        building_density = tree.xpath('//div[@class="p1015"]/table/tbody/tr[5]/td[2]')
        building_density = building_density[0].xpath('string()')[5:]
        # print building_density

        #限制高度
        limit_height = tree.xpath('//div[@class="p1015"]/table/tbody/tr[6]/td[1]')
        limit_height = limit_height[0].xpath('string()')[5:]
        # print limit_height

        #出让形式
        transfer_form = tree.xpath('//div[@class="p1015"]/table/tbody/tr[6]/td[2]')
        transfer_form = transfer_form[0].xpath('string()')[5:]
        # print transfer_form

        #出让年限
        transfer_year = tree.xpath('//div[@class="p1015"]/table/tbody/tr[7]/td[1]')
        transfer_year = transfer_year[0].xpath('string()')[5:]
        # print transfer_year

        #位置
        location = tree.xpath('//div[@class="p1015"]/table/tbody/tr[7]/td[2]')
        location = location[0].xpath('string()')[3:]
        # print location

        #四至
        four_boundaries = tree.xpath('//div[@class="p1015"]/table/tbody/tr[8]/td/@title')
        four_boundaries = four_boundaries[0]
        # print four_boundaries

        #规划用途
        planning_usage = tree.xpath('//div[@class="p1015"]/table/tbody/tr[8]/td/a')
        planning_usage = planning_usage[0].text
        # print planning_usage

        base_datas = [title,land_No,Province,city,total_area,construction_area,planning_construction_area,proxy_area,plot_ratio,\
                      green_ratio,commercial_ratio,building_density,limit_height, transfer_form, transfer_year, location,\
                      four_boundaries,planning_usage]
        # for data in base_datas:
        #     print data


        #土地交易信息
        deal_info = []
        #交易状况
        deal_status = tree.xpath('//div[@class="banbox"]/table/tbody/tr[1]/td[1]')
        deal_status = deal_status[0].xpath('string()')[5:]
        # print deal_status
        deal_info.append(deal_status)

        #竞得方
        get_party = tree.xpath('//div[@class="banbox"]/table/tbody/tr[1]/td[2]')
        get_party = get_party[0].xpath('string()')[4:]
        # print get_party
        deal_info.append(get_party)

        #起始日期tart_time
        start_time = tree.xpath('//div[@class="banbox"]/table/tbody/tr[2]/td[1]')
        start_time = start_time[0].xpath('string()')[5:]
        # print start_time
        deal_info.append(start_time)

        #戒指日期
        end_time = tree.xpath('//div[@class="banbox"]/table/tbody/tr[2]/td[2]')
        end_time = end_time[0].xpath('string()')[5:]
        # print end_time
        deal_info.append(end_time)

        #成交日期
        deal_time = tree.xpath('//div[@class="banbox"]/table/tbody/tr[3]/td[1]')
        deal_time = deal_time[0].xpath('string()')[5:]
        # print deal_time
        deal_info.append(deal_time)

        #交易地点
        deal_location = tree.xpath('//div[@class="banbox"]/table/tbody/tr[3]/td[2]')
        deal_location = deal_location[0].xpath('string()')[5:]
        # print deal_location
        deal_info.append(deal_location)

        #起始价
        start_price = tree.xpath('//div[@class="banbox"]/table/tbody/tr[4]/td[1]')
        start_price = start_price[0].xpath('string()')[4:]
        # print start_price
        deal_info.append(start_price)

        #成交价
        deal_price = tree.xpath('//div[@class="banbox"]/table/tbody/tr[4]/td[2]')
        deal_price = deal_price[0].xpath('string()')[4:]
        # print deal_price
        deal_info.append(deal_price)

        #楼面地价
        floor_price = tree.xpath('//div[@class="banbox"]/table/tbody/tr[5]/td[1]')
        floor_price = floor_price[0].xpath('string()')[5:]
        # print floor_price
        deal_info.append(floor_price)

        #溢价率
        premium_ratio = tree.xpath('//div[@class="banbox"]/table/tbody/tr[5]/td[2]')
        premium_ratio = premium_ratio[0].xpath('string()')[4:]
        # print premium_ratio
        deal_info.append(premium_ratio)

        #土地公告及链接
        land_announcement = tree.xpath('//div[@class="banbox"]/table/tbody/tr[6]/td[1]/a')
        land_announcement = land_announcement[0].text
        # print land_announcement
        deal_info.append(land_announcement)
        land_announcement_url = tree.xpath('//div[@class="banbox"]/table/tbody/tr[6]/td[1]/a/@href')
        # print land_announcement_url[0]
        deal_info.append(land_announcement_url[0])

        #咨询电话
        phone_No = tree.xpath('//div[@class="banbox"]/table/tbody/tr[6]/td[2]')
        phone_No = phone_No[0].xpath('string()')[5:]
        # print phone_No
        deal_info.append(phone_No)

        #保证金
        cash_deposit = tree.xpath('//div[@class="banbox"]/table/tbody/tr[7]/td[1]')
        cash_deposit = cash_deposit[0].xpath('string()')[4:]
        # print cash_deposit
        deal_info.append(cash_deposit)

        #最小加价幅度
        minimum_price_increase = tree.xpath('//div[@class="banbox"]/table/tbody/tr[7]/td[2]')
        minimum_price_increase = minimum_price_increase[0].xpath('string()')[7:]
        # print minimum_price_increase
        deal_info.append(minimum_price_increase)

        datas = base_datas + deal_info
        # for data in datas:
        #     print data
        return datas

    #存储到csv
    def initCsv(self):
        csvfile = file('cd_fang_land.csv','wb')
        writer = csv.writer(csvfile)
        # writer.writerow(['标题','地块编号'])
        writer.writerow(['标题','地块编号','省份','城市','总面积','建设用地面积','规划建筑面积','代征面积','容积率',\
                         '绿化率','商业比例','建筑密度','限制高度','出让形式','出让年限','位置','四至','规划用途',\
                         '交易状况','竞得方','起始日期','截止日期','成交日期','交易低点','起始价','成交价','楼面地价',\
                         '溢价率','土地公告','咨询电话','保证金','最小加价幅度'])
        csvfile.close()

    def saveCsv(self,url):

        csvfile = file('cd_fang_land.csv','ab')
        writer = csv.writer(csvfile)

        datas = self.getListDatas(url)
        for data in datas:
            csv_data = []
            for item in data:
                item = item.strip().encode('utf-8')
                csv_data.append(item)
            writer.writerow(csv_data)

        csvfile.close()

        # print "cd_fang_land.csv is finished"

    def start(self):
        # url = self.init_url
        #设置一个初始化CSV的函数
        if self.control == True:
            self.initCsv()

        i = 31
        while i <=34:
            url = "http://land.fang.com/market/510100________1_0_" + str(i) +".html"
            self.saveCsv(url)
            print "page "+str(i) +" is crawled"
            # print url
            i += 1
            #每写完一页主页面休息5秒
            time.sleep(1)
        print "cd_fang_land.csv is finished"




init_url = "http://land.fang.com/market/510100________1_0_8.html"
# init_url = "http://fang.com"
# init_url = "http://land.fang.com/"
# init_url = "http://land.fang.com/market/81f4e310-2484-47e4-9049-97117e7a5b6a.html"
# request = urllib2.Request(init_url)
# response = urllib2.urlopen(request)
# content = response.read()
# print content
# print chardet.detect(content)
# print content
test = fang_land()
# test.getListDatas(init_url)
# test.getProvinceDatas(init_url)
# test.saveCsv(init_url)
# test.initCsv()
test.start()