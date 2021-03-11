import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EestiItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'

class EestiSpider(scrapy.Spider):
	name = 'eesti'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [f'https://www.eestipank.ee/press/{year}']

	def parse(self, response):
		post_links = response.xpath('//table//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.eestipank.ee/press/{self.year}'
		if self.year >= 1997:
			self.year -= 1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="submitted"]/text()').get()
		title = response.xpath('//div[@class="field-name-title"]/h2/text()').get()
		content = response.xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden clearfix"]//text()[not (ancestor::table[@id="content-author"]) and not (ancestor::script)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EestiItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
