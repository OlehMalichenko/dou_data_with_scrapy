import scrapy


class DouItem(scrapy.Item):
    name = scrapy.Field()
    href = scrapy.Field()
    location = scrapy.Field()
    link = scrapy.Field()
    href_offices = scrapy.Field()
    href_vacancy = scrapy.Field()
    email = scrapy.Field()
    tel = scrapy.Field()
    address = scrapy.Field()
    persons_admin = scrapy.Field()
    vacancy = scrapy.Field() #dictionary name:vacancy_href


