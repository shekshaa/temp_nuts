from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from ads.test.tests_models import create_categories, create_dummy_ads
from users.tests import create_member, login
from ads.models import Advertisement, Category

import time

DELAY = 3  # seconds


class AdsStaticLiveServerTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.Chrome()
        super(AdsStaticLiveServerTestCase, self).setUp()
        create_categories()

        self.member = create_member('test', 'test')
        login(self.selenium, self.live_server_url, 'test', 'test')

    def tearDown(self):
        self.selenium.quit()
        super(AdsStaticLiveServerTestCase, self).tearDown()


class SearchLiveServerTestAds(AdsStaticLiveServerTestCase):
    def test_redirect_to_homepage(self):
        self.selenium.get(self.live_server_url)
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/ads/')

    def test_homepage_show_ads(self):
        create_dummy_ads(self.member)
        self.selenium.get(self.live_server_url)

        try:
            WebDriverWait(self.selenium, DELAY).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
        except TimeoutException:
            print('time out')

        assert 'pride' in self.selenium.page_source
        assert 'good peugeot' in self.selenium.page_source
        assert 'ok truck' in self.selenium.page_source


class AdLiveServerTestAds(AdsStaticLiveServerTestCase):
    def create_ad_and_move_to_my_ads(self):
        Advertisement.objects.create(title='pride', price=500, is_urgent=True, description='good car',
                                     state='Tehran', city='Tehran', user=self.member,
                                     category=Category.objects.get(title='sport_car'))

        self.selenium.find_element_by_link_text('پروفایل').click()
        self.selenium.find_element_by_link_text('آگهی‌های من').click()

    def test_create_ad(self):
        self.selenium.find_element_by_id('create_advertisement').click()

        title = self.selenium.find_element_by_id('title')
        select1 = Select(self.selenium.find_element_by_id("select1"))
        select2 = Select(self.selenium.find_element_by_id("select2"))
        category = Select(self.selenium.find_element_by_id("category"))

        state = Select(self.selenium.find_element_by_id("state"))
        city = Select(self.selenium.find_element_by_id("city"))
        desc = self.selenium.find_element_by_id('desc')
        price = self.selenium.find_element_by_id('price')

        submit = self.selenium.find_element_by_id('submit')

        title.send_keys('my ad')
        desc.send_keys('a good ad')
        price.send_keys(1000)

        select1.select_by_index(1)
        state.select_by_index(1)
        time.sleep(1)

        select2.select_by_index(1)
        city.select_by_index(1)
        time.sleep(1)

        category.select_by_index(1)

        submit.send_keys(Keys.RETURN)

        try:
            WebDriverWait(self.selenium, DELAY).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
        except TimeoutException:
            print('time out')

        assert 'my ad' in self.selenium.page_source

    def test_show_created_ad_in_my_ads(self):
        self.create_ad_and_move_to_my_ads()
        assert 'pride' in self.selenium.page_source
