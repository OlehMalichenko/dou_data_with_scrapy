from pprint import pprint
import csv

class DouPipeline(object):

    def process_item(self, item, spider):
        pprint(item)

        block = list()
        block.append(item['name'])
        block.append(item['href'])
        block.append(item['location'])
        block.append(item['link'])
        block.append(item['href_offices'])
        block.append(item['href_vacancy'])
        block.append(item['email'])
        block.append(item['tel'])
        block.append(item['address'])
        block.append(item['persons_admin'])
        block.append(item['vacancy'])

        # self.block_main.append(block)
        self.write_csv(block)
        return item

    def write_csv(self, block):
        with open('dou_data.csv', 'a', newline='\n', encoding='utf8') as file:
            writer = csv.writer(file)
            writer.writerow(block)
            # for block in self.block_main:
            #     writer.writerow(block)


    # def open_spider(self, spider):
    #     self.block_main = list()

    # def close_spider(self, spider):
    #     self.write_csv()