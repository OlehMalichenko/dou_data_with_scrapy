# -*- coding: utf-8 -*-
import scrapy
import csv
from dou.items import DouItem
from pprint import pprint
from time import sleep
import random


class DouSpiderSpider(scrapy.Spider):
    name = 'dou_spider'
    allowed_domains = ['jobs.dou.ua']


    def start_requests(self):
        with open('needed_csv.csv', newline='\n', encoding='utf8') as file:
            reader = csv.reader(file)

            count = 0
            count_all = 0
            for line in reader:
                count_all = count_all + 1

                href = self.check_line(line)

                if href is None:
                    continue

                yield scrapy.Request(href)

                count = count + 1
                # if count == 1:
                #     break
                if count == 50:
                    sec = self.get_random_time()
                    print('SLEEP--------------------' + str(sec))
                    print('count_all----------------' + str(count_all))
                    sleep(sec)
                    count = 0


    def check_line(self, line):

        if type(line) is list:

            if len(line) == 1:
                href = line[0]

                if type(href) is str:
                    check_http = href.find('http', 0, 4)

                    if check_http != -1:
                        return href
                    else:
                        print('is not link-http')
                        return None
                else:
                    print('is not str')
                    return None
            else:
                print('is not correct len in line')
                return None
        else:
            print('line in csv is not list')
            return None

    def parse(self, response):
        if response.status == 200:
            # inner hrefs
            href = response.request.url
            href_vacancy = href + 'vacancies/'
            href_offices = href + 'offices/'

            # start create item
            item = DouItem()
            item['name'] = self.get_data(response, self.get_name_path())
            item['href'] = href
            item['location'] = self.get_data(response, self.get_location_path())
            item['link'] = self.get_data(response, self.get_link_path())
            item['href_vacancy'] = href_vacancy
            item['href_offices'] = href_offices

            # go to vacancy
            yield scrapy.Request(url=href_vacancy,
                                 callback=self.go_to_vacancy,
                                 meta={'item': item, 'href_offices': href_offices})



#==========STEP VACANCY============#
    # first step (turn to office - second step)
    def go_to_vacancy(self, response):
        path = self.get_vacancy_path()
        vacancies_list = response.xpath(path)
        if vacancies_list is None:
            return

        item = response.meta['item']
        href_offices = response.meta['href_offices']
        vacancies = list()

        for el in vacancies_list:
            title = el.xpath('.//text()').get()
            href = el.xpath('.//@href').get()
            vacancies.append([title, href])

        item['vacancy'] = vacancies

        # go to offices
        yield scrapy.Request(url=href_offices,
                             callback=self.go_to_kiev_offices,
                             meta={'item': item})


#==========STEP OFFICES============#
    # yield item
    def go_to_kiev_offices(self, response):
        item = response.meta['item']

        path = self.get_office_kiev_path()
        element = response.xpath(path)

        if element is None:
            yield item
            return

        office = self.get_data_from_kiev_office(element)

        item['address'] = office['address']
        item['email'] = office['email']
        item['tel'] = office['tel']
        item['persons_admin'] = office['persons_admin']

        yield item

    def get_data_from_kiev_office(self, element):
        result = {'address': self.get_data(element, self.get_address_path()),
                  'email': self.get_data(element, self.get_mail_path()),
                  'tel': self.get_data(element, self.get_tel_path()),
                  'persons_admin': self.get_persons_info(element)}
        return result

    def get_persons_info(self, element):
        path_info = self.get_person_info_path()
        info = element.xpath(path_info)

        if len(info) > 1:
            info = self.find_need_info(info)

        if info is None:
            return None

        path_li = self.get_person_li_path()
        persons = info.xpath(path_li)
        if persons is None:
            return None

        persons_list = list()
        path_position = self.get_person_position_path()
        path_name = self.get_person_name_path()

        for person in persons:
            try:
                position_ = person.xpath(path_position)
                position = position_[-1].get().strip()

                person_name_ = person.xpath(path_name)
                person_name = person_name_[-1].get().strip()
            except:
                continue

            persons_list.append([position, person_name])

        return persons_list

    def find_need_info(self, infos):
        for info in infos:
            persons = info.xpath('.//ul[@class="persons"]')
            if persons is not None:
                return info
        return None


#=========PATHES TO DATA===========#
    def get_data(self, response, path):
        try:
            return response.xpath(path).get().strip()
        except:
            return None

    def get_name_path(self):
        return '//div[@class="company-info"]/h1[@class="g-h2"]/text()'

    def get_location_path(self):
        return '//div[@class="company-info"]/div[@class="offices"]/text()'

    def get_link_path(self):
        return '//div[@class="company-info"]/div[@class="site"]/a[@href]/@href'

    def get_vacancy_path(self):
        return '//div[@id="vacancyListId"]//div[@class="vacancy"]/div[@class="title"]/a[@class="vt"]'

    def get_office_kiev_path(self):
        return '//h4[@id="kiev"]/..'

    def get_address_path(self):
        return './/div[@class="contacts"]//div[@class="address"]/text()'

    def get_mail_path(self):
        return './/div[@class="contacts"]//div[@class="mail"]/a[@href]/text()'

    def get_tel_path(self):
        return './/div[@class="contacts"]//div[@class="phones"]/text()'

    def get_person_info_path(self):
        return './/div[@class="info"]'

    def get_person_li_path(self):
        return './/ul[@class="persons"]/li'

    def get_person_position_path(self):
        return './/a[@class="name"]/following-sibling::text()'

    def get_person_name_path(self):
        return './/a[@class="name"]/child::text()'

#=========RANDOM TIME===========#
    def get_random_time(self):
        return random.uniform(1, 5)