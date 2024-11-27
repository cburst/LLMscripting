import sys
import time
import csv
import re
import unicodedata
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser

# List of RSS feed URLs
rss_urls = [
    "http://www.newsdaily.kr/rss/S1N30.xml",
    "http://www.newsdaily.kr/rss/S1N32.xml",
    "http://www.newsdaily.kr/rss/S1N38.xml",
    "http://www.newsdaily.kr/rss/S1N39.xml",
    "http://www.newsdaily.kr/rss/S1N4.xml",
    "http://www.newsdaily.kr/rss/S1N40.xml",
    "http://www.newsdaily.kr/rss/S1N46.xml",
    "http://www.newsdaily.kr/rss/S1N47.xml",
    "http://www.newsdaily.kr/rss/S1N49.xml",
    "http://www.newsdaily.kr/rss/S1N50.xml",
    "http://www.newsdaily.kr/rss/S1N51.xml",
    "http://www.newspost.kr/rss/allArticle.xml",
    "http://www.newspost.kr/rss/clickTop.xml",
    "http://www.newspost.kr/rss/S1N1.xml",
    "http://www.newspost.kr/rss/S1N2.xml",
    "http://www.newspost.kr/rss/S1N3.xml",
    "http://www.newspost.kr/rss/S1N4.xml",
    "http://www.newspost.kr/rss/S1N5.xml",
    "http://www.newspost.kr/rss/S1N6.xml",
    "http://www.newswith.co.kr/rss/allArticle.xml",
    "http://www.newswith.co.kr/rss/clickTop.xml",
    "http://www.newswith.co.kr/rss/S1N1.xml",
    "http://www.newswith.co.kr/rss/S1N10.xml",
    "http://www.newswith.co.kr/rss/S1N11.xml",
    "http://www.newswith.co.kr/rss/S1N2.xml",
    "http://www.newswith.co.kr/rss/S1N3.xml",
    "http://www.newswith.co.kr/rss/S1N4.xml",
    "http://www.newswith.co.kr/rss/S1N5.xml",
    "http://www.newswith.co.kr/rss/S1N6.xml",
    "http://www.newswith.co.kr/rss/S1N7.xml",
    "http://www.newswith.co.kr/rss/S1N8.xml",
    "http://www.newswith.co.kr/rss/S1N9.xml",
    "http://www.today-news.co.kr/rss/allArticle.xml",
    "http://www.today-news.co.kr/rss/clickTop.xml",
    "http://www.today-news.co.kr/rss/S1N1.xml",
    "http://www.today-news.co.kr/rss/S1N2.xml",
    "http://www.today-news.co.kr/rss/S1N3.xml",
    "http://www.today-news.co.kr/rss/S1N4.xml",
    "http://www.today-news.co.kr/rss/S1N5.xml",
    "http://www.today-news.co.kr/rss/S1N6.xml",
    "http://www.top-rider.com/rss/allArticle.xml",
    "http://www.top-rider.com/rss/clickTop.xml",
    "http://www.top-rider.com/rss/S1N1.xml",
    "http://www.top-rider.com/rss/S1N4.xml",
    "http://www.top-rider.com/rss/S1N5.xml",
    "http://www.top-rider.com/rss/S1N7.xml",
    "http://www.top-rider.com/rss/S1N8.xml",
    "http://www.top-rider.com/rss/S1N9.xml",
    "http://art.chosun.com/site/data/rss/rss.xml",
    "http://biz.chosun.com/site/data/rss/enterprise.xml",
    "http://biz.chosun.com/site/data/rss/estate.xml",
    "http://biz.chosun.com/site/data/rss/global.xml",
    "http://biz.chosun.com/site/data/rss/market.xml",
    "http://biz.chosun.com/site/data/rss/news.xml",
    "http://biz.chosun.com/site/data/rss/policybank.xml",
    "http://biz.chosun.com/site/data/rss/rss.xml",
    "http://biz.chosun.com/site/data/rss/weeklybiz.xml",
    "http://biz.heraldm.com/rss/010000000000.xml",
    "http://biz.heraldm.com/rss/010100000000.xml",
    "http://biz.heraldm.com/rss/010103000000.xml",
    "http://biz.heraldm.com/rss/010104000000.xml",
    "http://biz.heraldm.com/rss/010106000000.xml",
    "http://biz.heraldm.com/rss/010107000000.xml",
    "http://biz.heraldm.com/rss/010108000000.xml",
    "http://biz.heraldm.com/rss/010109000000.xml",
    "http://biz.heraldm.com/rss/010110000000.xml",
    "http://biz.heraldm.com/rss/010200000000.xml",
    "http://biz.heraldm.com/rss/010202000000.xml",
    "http://biz.heraldm.com/rss/010203000000.xml",
    "http://biz.heraldm.com/rss/010204000000.xml",
    "http://biz.heraldm.com/rss/010205000000.xml",
    "http://biz.heraldm.com/rss/010206000000.xml",
    "http://biz.heraldm.com/rss/010207000000.xml",
    "http://biz.heraldm.com/rss/010208000000.xml",
    "http://biz.heraldm.com/rss/010209000000.xml",
    "http://biz.heraldm.com/rss/010300000000.xml",
    "http://biz.heraldm.com/rss/010301000000.xml",
    "http://biz.heraldm.com/rss/010303000000.xml",
    "http://biz.heraldm.com/rss/010305000000.xml",
    "http://biz.heraldm.com/rss/010306000000.xml",
    "http://biz.heraldm.com/rss/010308000000.xml",
    "http://biz.heraldm.com/rss/010309000000.xml",
    "http://biz.heraldm.com/rss/010400000000.xml",
    "http://biz.heraldm.com/rss/010403000000.xml",
    "http://biz.heraldm.com/rss/010404000000.xml",
    "http://biz.heraldm.com/rss/010405000000.xml",
    "http://biz.heraldm.com/rss/010406000000.xml",
    "http://biz.heraldm.com/rss/010409000000.xml",
    "http://biz.heraldm.com/rss/010410000000.xml",
    "http://biz.heraldm.com/rss/010500000000.xml",
    "http://biz.heraldm.com/rss/010501000000.xml",
    "http://biz.heraldm.com/rss/010502000000.xml",
    "http://biz.heraldm.com/rss/010503000000.xml",
    "http://biz.heraldm.com/rss/010504000000.xml",
    "http://biz.heraldm.com/rss/010505000000.xml",
    "http://biz.heraldm.com/rss/010506000000.xml",
    "http://biz.heraldm.com/rss/010600000000.xml",
    "http://biz.heraldm.com/rss/010601000000.xml",
    "http://biz.heraldm.com/rss/010602000000.xml",
    "http://biz.heraldm.com/rss/010604000000.xml",
    "http://books.chosun.com/site/data/rss/rss.xml",
    "http://careview.chosun.com/site/data/rss/rss.xml",
    "http://danmee.chosun.com/site/data/rss/rss.xml",
    "http://file.mk.co.kr/news/rss/rss_30000001.xml",
    "http://file.mk.co.kr/news/rss/rss_30000023.xml",
    "http://file.mk.co.kr/news/rss/rss_30100041.xml",
    "http://file.mk.co.kr/news/rss/rss_30200030.xml",
    "http://file.mk.co.kr/news/rss/rss_30300018.xml",
    "http://file.mk.co.kr/news/rss/rss_30500041.xml",
    "http://file.mk.co.kr/news/rss/rss_30800011.xml",
    "http://file.mk.co.kr/news/rss/rss_40200003.xml",
    "http://file.mk.co.kr/news/rss/rss_40200124.xml",
    "http://file.mk.co.kr/news/rss/rss_40300001.xml",
    "http://file.mk.co.kr/news/rss/rss_50000001.xml",
    "http://file.mk.co.kr/news/rss/rss_50100032.xml",
    "http://file.mk.co.kr/news/rss/rss_50200011.xml",
    "http://file.mk.co.kr/news/rss/rss_50300009.xml",
    "http://file.mk.co.kr/news/rss/rss_50400012.xml",
    "http://file.mk.co.kr/news/rss/rss_50600001.xml",
    "http://file.mk.co.kr/news/rss/rss_50700001.xml",
    "http://file.mk.co.kr/news/rss/rss_60000007.xml",
    "http://forum.chosun.com/rss/RSSServlet?bbs_type=P",
    "http://forum.chosun.com/rss/RSSServlet?bbs_type=R",
    "http://forum.chosun.com/rss/RSSServlet?bbs_type=S",
    "http://health.chosun.com/rss/column.xml",
    "http://health.chosun.com/site/data/rss/rss.xml",
    "http://imnews.imbc.com/rss/citizen/movnews.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_01.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_02.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_03.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_04.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_05.xml",
    "http://imnews.imbc.com/rss/fullmov/fullmov_06.xml",
    "http://imnews.imbc.com/rss/mpeople/rptcolumn.xml",
    "http://imnews.imbc.com/rss/news/news_00.xml",
    "http://imnews.imbc.com/rss/news/news_01.xml",
    "http://imnews.imbc.com/rss/news/news_02.xml",
    "http://imnews.imbc.com/rss/news/news_03.xml",
    "http://imnews.imbc.com/rss/news/news_04.xml",
    "http://imnews.imbc.com/rss/news/news_05.xml",
    "http://imnews.imbc.com/rss/news/news_06.xml",
    "http://imnews.imbc.com/rss/news/news_07.xml",
    "http://imnews.imbc.com/rss/news/news_08.xml",
    "http://imnews.imbc.com/rss/replay/replay_01.xml",
    "http://imnews.imbc.com/rss/replay/replay_02.xml",
    "http://imnews.imbc.com/rss/replay/replay_03.xml",
    "http://imnews.imbc.com/rss/replay/replay_04.xml",
    "http://imnews.imbc.com/rss/replay/replay_05.xml",
    "http://imnews.imbc.com/rss/replay/replay_06.xml",
    "http://imnews.imbc.com/rss/replay/replay_07.xml",
    "http://imnews.imbc.com/rss/replay/replay_08.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_01.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_02.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_03.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_04.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_05.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_06.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_07.xml",
    "http://imnews.imbc.com/rss/weekly/weekly_08.xml",
    "http://inside.chosun.com/rss/rss.xml",
    "http://keywui.chosun.com/rss/rss.xml",
    "http://media.daum.net/rss/part/primary/culture/rss2.xml",
    "http://media.daum.net/rss/part/primary/digital/rss2.xml",
    "http://media.daum.net/rss/part/primary/economic/rss2.xml",
    "http://media.daum.net/rss/part/primary/entertain/rss2.xml",
    "http://media.daum.net/rss/part/primary/foreign/rss2.xml",
    "http://media.daum.net/rss/part/primary/politics/rss2.xml",
    "http://media.daum.net/rss/part/primary/society/rss2.xml",
    "http://media.daum.net/rss/today/primary/all/rss2.xml",
    "http://media.daum.net/rss/today/primary/entertain/rss2.xml",
    "http://media.daum.net/rss/today/primary/sports/rss2.xml",
    "http://myhome.chosun.com/rss/kid_section_rss.xml",
    "http://myhome.chosun.com/rss/www_section_rss.xml",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=b&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=e&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=l&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=p&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=po&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=s&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=t&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=w&output=rss",
    "http://news.google.co.kr/news?pz=1&cf=all&ned=kr&hl=ko&topic=y&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=b&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=e&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=l&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=p&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=po&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=s&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=t&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=w&output=rss",
    "http://news.google.co.kr/news?pz=1&hdlOnly=1&cf=all&ned=kr&hl=ko&topic=y&output=rss",
    "http://newsplus.chosun.com/hitdata/xml/chosunbiz/index/index.xml",
    "http://newsplus.chosun.com/hitdata/xml/index/index.xml",
    "http://newsplus.chosun.com/hitdata/xml/newsplus/index/index.xml",
    "http://newsplus.chosun.com/hitdata/xml/se/sports/index.xml",
    "http://newsplus.chosun.com/hitdata/xml/se/star/index.xml",
    "http://newsplus.chosun.com/inside/xml/inside_rss.xml",
    "http://newsplus.chosun.com/site/data/rss/news.xml",
    "http://photo.chosun.com/site/data/rss/photonews.xml",
    "http://review.chosun.com/site/data/rss/rss.xml",
    "http://rss.donga.com/book.xml",
    "http://rss.donga.com/child.xml",
    "http://rss.donga.com/culture.xml",
    "http://rss.donga.com/economy.xml",
    "http://rss.donga.com/editorials.xml",
    "http://rss.donga.com/health.xml",
    "http://rss.donga.com/inmul.xml",
    "http://rss.donga.com/international.xml",
    "http://rss.donga.com/leisure.xml",
    "http://rss.donga.com/lifeinfo.xml",
    "http://rss.donga.com/national.xml",
    "http://rss.donga.com/politics.xml",
    "http://rss.donga.com/science.xml",
    "http://rss.donga.com/show.xml",
    "http://rss.donga.com/sports.xml",
    "http://rss.donga.com/sportsdonga/baseball.xml",
    "http://rss.donga.com/sportsdonga/entertainment.xml",
    "http://rss.donga.com/sportsdonga/golf.xml",
    "http://rss.donga.com/sportsdonga/soccer.xml",
    "http://rss.donga.com/sportsdonga/sports_general.xml",
    "http://rss.donga.com/total.xml",
    "http://rss.donga.com/travel.xml",
    "http://rss.donga.com/woman.xml",
    "http://rss.hankooki.com/economy/sk_culture.xml",
    "http://rss.hankooki.com/economy/sk_economy.xml",
    "http://rss.hankooki.com/economy/sk_estate.xml",
    "http://rss.hankooki.com/economy/sk_industry.xml",
    "http://rss.hankooki.com/economy/sk_main.xml",
    "http://rss.hankooki.com/economy/sk_opinion.xml",
    "http://rss.hankooki.com/economy/sk_politics.xml",
    "http://rss.hankooki.com/economy/sk_society.xml",
    "http://rss.hankooki.com/economy/sk_stock.xml",
    "http://rss.hankooki.com/economy/sk_world.xml",
    "http://rss.hankooki.com/kids/kd_childworld.xml",
    "http://rss.hankooki.com/kids/kd_learn.xml",
    "http://rss.hankooki.com/kids/kd_main.xml",
    "http://rss.hankooki.com/kids/kd_news.xml",
    "http://rss.hankooki.com/kids/kd_play.xml",
    "http://rss.hankooki.com/magazine/gh_main.xml",
    "http://rss.hankooki.com/magazine/gm_main.xml",
    "http://rss.hankooki.com/magazine/pop_main.xml",
    "http://rss.hankooki.com/magazine/wk_main.xml",
    "http://rss.hankooki.com/news/hk_culture.xml",
    "http://rss.hankooki.com/news/hk_economy.xml",
    "http://rss.hankooki.com/news/hk_entv.xml",
    "http://rss.hankooki.com/news/hk_it_tech.xml",
    "http://rss.hankooki.com/news/hk_life.xml",
    "http://rss.hankooki.com/news/hk_main.xml",
    "http://rss.hankooki.com/news/hk_opinion.xml",
    "http://rss.hankooki.com/news/hk_people.xml",
    "http://rss.hankooki.com/news/hk_photoi.xml",
    "http://rss.hankooki.com/news/hk_politics.xml",
    "http://rss.hankooki.com/news/hk_society.xml",
    "http://rss.hankooki.com/news/hk_sports.xml",
    "http://rss.hankooki.com/news/hk_tv.xml",
    "http://rss.hankooki.com/news/hk_world.xml",
    "http://rss.hankooki.com/sports/sp_enjoy.xml",
    "http://rss.hankooki.com/sports/sp_entv.xml",
    "http://rss.hankooki.com/sports/sp_life.xml",
    "http://rss.hankooki.com/sports/sp_main.xml",
    "http://rss.hankooki.com/sports/sp_sports.xml",
    "http://rss.hankyung.com/auto.xml",
    "http://rss.hankyung.com/column.xml",
    "http://rss.hankyung.com/community.xml",
    "http://rss.hankyung.com/economy.xml",
    "http://rss.hankyung.com/english.xml",
    "http://rss.hankyung.com/estate.xml",
    "http://rss.hankyung.com/ft.xml",
    "http://rss.hankyung.com/golf.xml",
    "http://rss.hankyung.com/industry.xml",
    "http://rss.hankyung.com/intl.xml",
    "http://rss.hankyung.com/janggun.xml",
    "http://rss.hankyung.com/leaders.xml",
    "http://rss.hankyung.com/politics.xml",
    "http://rss.hankyung.com/sports.xml",
    "http://rss.hankyung.com/stock.xml",
    "http://rss.hankyung.com/xfile.xml",
    "http://rss.joinsmsn.com/joins_culture_list.xml",
    "http://rss.joinsmsn.com/joins_homenews_list.xml",
    "http://rss.joinsmsn.com/joins_it_list.xml",
    "http://rss.joinsmsn.com/joins_life_list.xml",
    "http://rss.joinsmsn.com/joins_money_list.xml",
    "http://rss.joinsmsn.com/joins_news_list.xml",
    "http://rss.joinsmsn.com/joins_politics_list.xml",
    "http://rss.joinsmsn.com/joins_sports_list.xml",
    "http://rss.joinsmsn.com/joins_star_list.xml",
    "http://rss.joinsmsn.com/joins_world_list.xml",
    "http://rss.joinsmsn.com/news/joins_cnnnews_total.xml",
    "http://rss.joinsmsn.com/news/joins_health_list.xml",
    "http://rss.joinsmsn.com/news/joins_jonly_list.xml",
    "http://rss.joinsmsn.com/news/joins_joongangdaily_news.xml",
    "http://rss.joinsmsn.com/news/joins_lifenews_total.xml",
    "http://rss.joinsmsn.com/news/joins_sports_baseball_list.xml",
    "http://rss.joinsmsn.com/news/joins_sports_etc_list.xml",
    "http://rss.joinsmsn.com/news/joins_sports_golf_list.xml",
    "http://rss.joinsmsn.com/news/joins_sports_soccer_list.xml",
    "http://rss.joinsmsn.com/news/joins_star_entertainment_list.xml",
    "http://rss.joinsmsn.com/news/joins_star_etc_list.xml",
    "http://rss.joinsmsn.com/news/joins_star_movie_list.xml",
    "http://rss.joinsmsn.com/photo/joins_gallery_list_news.xml",
    "http://rss.joinsmsn.com/photo/joins_gallery_list_world.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_hot.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_it.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_life.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_money.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_politics.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_sports.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_star.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list_world.xml",
    "http://rss.joinsmsn.com/photo/joins_photo_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_it_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_life_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_money_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_opinion_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_politics_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_sports_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_star_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_total_list.xml",
    "http://rss.joinsmsn.com/sonagi/joins_sonagi_world_list.xml",
    "http://rss.nocutnews.co.kr/NocutColum.xml",
    "http://rss.nocutnews.co.kr/NocutCplan.xml",
    "http://rss.nocutnews.co.kr/NocutCulture.xml",
    "http://rss.nocutnews.co.kr/NocutEconomy.xml",
    "http://rss.nocutnews.co.kr/NocutEnter.xml",
    "http://rss.nocutnews.co.kr/NocutEtc.xml",
    "http://rss.nocutnews.co.kr/NocutGlobal.xml",
    "http://rss.nocutnews.co.kr/NocutHotissue.xml",
    "http://rss.nocutnews.co.kr/NocutIndustry.xml",
    "http://rss.nocutnews.co.kr/NocutIT.xml",
    "http://rss.nocutnews.co.kr/NocutLocal.xml",
    "http://rss.nocutnews.co.kr/nocutnews.xml",
    "http://rss.nocutnews.co.kr/NocutOnly.xml",
    "http://rss.nocutnews.co.kr/NocutPhoto.xml",
    "http://rss.nocutnews.co.kr/NocutPolitics.xml",
    "http://rss.nocutnews.co.kr/NocutSocial.xml",
    "http://rss.nocutnews.co.kr/NocutSports.xml",
    "http://rss.segye.com/segye_culture.xml",
    "http://rss.segye.com/segye_economy.xml",
    "http://rss.segye.com/segye_entertainment.xml",
    "http://rss.segye.com/segye_family.xml",
    "http://rss.segye.com/segye_international.xml",
    "http://rss.segye.com/segye_local.xml",
    "http://rss.segye.com/segye_opinion.xml",
    "http://rss.segye.com/segye_people.xml",
    "http://rss.segye.com/segye_photo.xml",
    "http://rss.segye.com/segye_politic.xml",
    "http://rss.segye.com/segye_punchnews.xml",
    "http://rss.segye.com/segye_recent.xml",
    "http://rss.segye.com/segye_root.xml",
    "http://rss.segye.com/segye_segyeTV.xml",
    "http://rss.segye.com/segye_society.xml",
    "http://rss.segye.com/segye_sports.xml",
    "http://rss.segye.com/segye_task_force.xml",
    "http://rss.segye.com/segye_total.xml",
    "http://rss.sportsworldi.com/sw_baseball.xml",
    "http://rss.sportsworldi.com/sw_basketball.xml",
    "http://rss.sportsworldi.com/sw_entertainment.xml",
    "http://rss.sportsworldi.com/sw_golf.xml",
    "http://rss.sportsworldi.com/sw_leisure.xml",
    "http://rss.sportsworldi.com/sw_opinion.xml",
    "http://rss.sportsworldi.com/sw_recent.xml",
    "http://rss.sportsworldi.com/sw_soccer.xml",
    "http://rss.sportsworldi.com/sw_total.xml",
    "http://thestar.chosun.com/site/data/rss/rss.xml",
    "http://travel.chosun.com/site/data/rss/rss.xml",
    "http://www.aving.net/rss/avpa.xml",
    "http://www.aving.net/rss/computing.xml",
    "http://www.aving.net/rss/game.xml",
    "http://www.aving.net/rss/homeappliance.xml",
    "http://www.aving.net/rss/housing.xml",
    "http://www.aving.net/rss/industry.xml",
    "http://www.aving.net/rss/life.xml",
    "http://www.aving.net/rss/misc.xml",
    "http://www.aving.net/rss/mobile.xml",
    "http://www.aving.net/rss/motor.xml",
    "http://www.chosun.com/site/data/rss/culture.xml",
    "http://www.chosun.com/site/data/rss/editorials.xml",
    "http://www.chosun.com/site/data/rss/ent.xml",
    "http://www.chosun.com/site/data/rss/international.xml",
    "http://www.chosun.com/site/data/rss/politics.xml",
    "http://www.chosun.com/site/data/rss/rss.xml",
    "http://www.chosun.com/site/data/rss/sports.xml",
    "http://www.chosun.com/site/data/rss/video.xml",
    "http://www.clubcity.kr/rss/allArticle.xml",
    "http://www.clubcity.kr/rss/clickTop.xml",
    "http://www.clubcity.kr/rss/S1N10.xml",
    "http://www.clubcity.kr/rss/S1N11.xml",
    "http://www.clubcity.kr/rss/S1N12.xml",
    "http://www.clubcity.kr/rss/S1N13.xml",
    "http://www.clubcity.kr/rss/S1N14.xml",
    "http://www.clubcity.kr/rss/S1N15.xml",
    "http://www.clubcity.kr/rss/S1N16.xml",
    "http://www.clubcity.kr/rss/S1N17.xml",
    "http://www.clubcity.kr/rss/S1N19.xml",
    "http://www.clubcity.kr/rss/S1N23.xml",
    "http://www.clubcity.kr/rss/S1N24.xml",
    "http://www.clubcity.kr/rss/S1N25.xml",
    "http://www.clubcity.kr/rss/S1N26.xml",
    "http://www.clubcity.kr/rss/S1N27.xml",
    "http://www.clubcity.kr/rss/S1N28.xml",
    "http://www.clubcity.kr/rss/S1N29.xml",
    "http://www.clubcity.kr/rss/S1N30.xml",
    "http://www.clubcity.kr/rss/S1N6.xml",
    "http://www.clubcity.kr/rss/S1N7.xml",
    "http://www.clubcity.kr/rss/S1N8.xml",
    "http://www.cstimes.com/rss/allArticle.xml",
    "http://www.cstimes.com/rss/clickTop.xml",
    "http://www.cstimes.com/rss/S1N1.xml",
    "http://www.cstimes.com/rss/S1N10.xml",
    "http://www.cstimes.com/rss/S1N11.xml",
    "http://www.cstimes.com/rss/S1N12.xml",
    "http://www.cstimes.com/rss/S1N13.xml",
    "http://www.cstimes.com/rss/S1N14.xml",
    "http://www.cstimes.com/rss/S1N15.xml",
    "http://www.cstimes.com/rss/S1N16.xml",
    "http://www.cstimes.com/rss/S1N17.xml",
    "http://www.cstimes.com/rss/S1N18.xml",
    "http://www.cstimes.com/rss/S1N19.xml",
    "http://www.cstimes.com/rss/S1N20.xml",
    "http://www.cstimes.com/rss/S1N21.xml",
    "http://www.cstimes.com/rss/S1N3.xml",
    "http://www.cstimes.com/rss/S1N4.xml",
    "http://www.cstimes.com/rss/S1N5.xml",
    "http://www.cstimes.com/rss/S1N7.xml",
    "http://www.cstimes.com/rss/S1N8.xml",
    "http://www.cstimes.com/rss/S1N9.xml",
    "http://www.datanet.co.kr/rss/allArticle.xml",
    "http://www.datanet.co.kr/rss/clickTop.xml",
    "http://www.datanet.co.kr/rss/S1N1.xml",
    "http://www.datanet.co.kr/rss/S1N2.xml",
    "http://www.datanet.co.kr/rss/S1N3.xml",
    "http://www.datanet.co.kr/rss/S1N4.xml",
    "http://www.datanet.co.kr/rss/S1N5.xml",
    "http://www.datanet.co.kr/rss/S1N6.xml",
    "http://www.evernews.co.kr/rss/allArticle.xml",
    "http://www.evernews.co.kr/rss/clickTop.xml",
    "http://www.evernews.co.kr/rss/S1N10.xml",
    "http://www.evernews.co.kr/rss/S1N11.xml",
    "http://www.evernews.co.kr/rss/S1N12.xml",
    "http://www.evernews.co.kr/rss/S1N2.xml",
    "http://www.evernews.co.kr/rss/S1N4.xml",
    "http://www.evernews.co.kr/rss/S1N5.xml",
    "http://www.evernews.co.kr/rss/S1N6.xml",
    "http://www.evernews.co.kr/rss/S1N8.xml",
    "http://www.evernews.co.kr/rss/S1N9.xml",
    "http://www.expojr.com/rss/allArticle.xml",
    "http://www.expojr.com/rss/clickTop.xml",
    "http://www.expojr.com/rss/S1N1.xml",
    "http://www.expojr.com/rss/S1N2.xml",
    "http://www.expojr.com/rss/S1N3.xml",
    "http://www.expojr.com/rss/S1N5.xml",
    "http://www.expojr.com/rss/S1N6.xml",
    "http://www.expojr.com/rss/S1N7.xml'}]",
    "http://www.fnnews.com/rss/fn_manyview_all.xml",
    "http://www.fnnews.com/rss/fn_manyview_circulation.xml",
    "http://www.fnnews.com/rss/fn_manyview_culture.xml",
    "http://www.fnnews.com/rss/fn_manyview_economy.xml",
    "http://www.fnnews.com/rss/fn_manyview_edu.xml",
    "http://www.fnnews.com/rss/fn_manyview_finance.xml",
    "http://www.fnnews.com/rss/fn_manyview_industry.xml",
    "http://www.fnnews.com/rss/fn_manyview_international.xml",
    "http://www.fnnews.com/rss/fn_manyview_it.xml",
    "http://www.fnnews.com/rss/fn_manyview_people.xml",
    "http://www.fnnews.com/rss/fn_manyview_politics.xml",
    "http://www.fnnews.com/rss/fn_manyview_realestate.xml",
    "http://www.fnnews.com/rss/fn_manyview_society.xml",
    "http://www.fnnews.com/rss/fn_manyview_sports.xml",
    "http://www.fnnews.com/rss/fn_manyview_stock.xml",
    "http://www.fnnews.com/rss/fn_realnews_all.xml",
    "http://www.fnnews.com/rss/fn_realnews_circulation.xml",
    "http://www.fnnews.com/rss/fn_realnews_culture.xml",
    "http://www.fnnews.com/rss/fn_realnews_economy.xml",
    "http://www.fnnews.com/rss/fn_realnews_edu.xml",
    "http://www.fnnews.com/rss/fn_realnews_finance.xml",
    "http://www.fnnews.com/rss/fn_realnews_industry.xml",
    "http://www.fnnews.com/rss/fn_realnews_international.xml",
    "http://www.fnnews.com/rss/fn_realnews_it.xml",
    "http://www.fnnews.com/rss/fn_realnews_people.xml",
    "http://www.fnnews.com/rss/fn_realnews_politics.xml",
    "http://www.fnnews.com/rss/fn_realnews_realestate.xml",
    "http://www.fnnews.com/rss/fn_realnews_society.xml",
    "http://www.fnnews.com/rss/fn_realnews_sports.xml",
    "http://www.fnnews.com/rss/fn_realnews_stock.xml",
    "http://www.focuscolorado.net/rss/allArticle.xml",
    "http://www.focuscolorado.net/rss/clickTop.xml",
    "http://www.focuscolorado.net/rss/S1N1.xml",
    "http://www.focuscolorado.net/rss/S1N2.xml",
    "http://www.focuscolorado.net/rss/S1N3.xml",
    "http://www.focuscolorado.net/rss/S1N4.xml",
    "http://www.focuscolorado.net/rss/S1N5.xml",
    "http://www.focuscolorado.net/rss/S1N6.xml",
    "http://www.focuscolorado.net/rss/S1N7.xml",
    "http://www.focuscolorado.net/rss/S1N8.xml",
    "http://www.ilemonde.com/rss/allArticle.xml",
    "http://www.ilemonde.com/rss/clickTop.xml",
    "http://www.ilemonde.com/rss/S1N28.xml",
    "http://www.ilemonde.com/rss/S1N29.xml",
    "http://www.ilemonde.com/rss/S1N30.xml",
    "http://www.ilemonde.com/rss/S1N31.xml",
    "http://www.ilemonde.com/rss/S1N32.xml",
    "http://www.ilemonde.com/rss/S1N34.xml",
    "http://www.ilemonde.com/rss/S1N35.xml",
    "http://www.ilemonde.com/rss/S1N36.xml",
    "http://www.ilemonde.com/rss/S1N37.xml",
    "http://www.ilemonde.com/rss/S1N38.xml",
    "http://www.ilemonde.com/rss/S1N39.xml",
    "http://www.ilemonde.com/rss/S1N40.xml",
    "http://www.jbnews.com/rss/allArticle.xml",
    "http://www.jbnews.com/rss/clickTop.xml",
    "http://www.jbnews.com/rss/S1N1.xml",
    "http://www.jbnews.com/rss/S1N10.xml",
    "http://www.jbnews.com/rss/S1N11.xml",
    "http://www.jbnews.com/rss/S1N12.xml",
    "http://www.jbnews.com/rss/S1N13.xml",
    "http://www.jbnews.com/rss/S1N14.xml",
    "http://www.jbnews.com/rss/S1N15.xml",
    "http://www.jbnews.com/rss/S1N16.xml",
    "http://www.jbnews.com/rss/S1N18.xml",
    "http://www.jbnews.com/rss/S1N19.xml",
    "http://www.jbnews.com/rss/S1N2.xml",
    "http://www.jbnews.com/rss/S1N3.xml",
    "http://www.jbnews.com/rss/S1N4.xml",
    "http://www.jbnews.com/rss/S1N5.xml",
    "http://www.jbnews.com/rss/S1N6.xml",
    "http://www.jbnews.com/rss/S1N7.xml",
    "http://www.jbnews.com/rss/S1N8.xml",
    "http://www.jbnews.com/rss/S1N9.xml",
    "http://www.khan.co.kr/rss/rssdata/culture.xml",
    "http://www.khan.co.kr/rss/rssdata/economy.xml",
    "http://www.khan.co.kr/rss/rssdata/itnews.xml",
    "http://www.khan.co.kr/rss/rssdata/kh_entertainment.xml",
    "http://www.khan.co.kr/rss/rssdata/kh_fun.xml",
    "http://www.khan.co.kr/rss/rssdata/kh_special.xml",
    "http://www.khan.co.kr/rss/rssdata/kh_sports.xml",
    "http://www.khan.co.kr/rss/rssdata/kh_unse.xml",
    "http://www.khan.co.kr/rss/rssdata/mx.xml",
    "http://www.khan.co.kr/rss/rssdata/opinion.xml",
    "http://www.khan.co.kr/rss/rssdata/people.xml",
    "http://www.khan.co.kr/rss/rssdata/politic.xml",
    "http://www.khan.co.kr/rss/rssdata/society.xml",
    "http://www.khan.co.kr/rss/rssdata/sports.xml",
    "http://www.khan.co.kr/rss/rssdata/total_news.xml",
    "http://www.khan.co.kr/rss/rssdata/world.xml",
    "http://www.kmobile.co.kr/rss/all",
    "http://www.kmobile.co.kr/rss/internet",
    "http://www.kmobile.co.kr/rss/it",
    "http://www.kmobile.co.kr/rss/software",
    "http://www.newsdaily.kr/rss/allArticle.xml",
    "http://www.newsdaily.kr/rss/clickTop.xml",
    "http://www.newsdaily.kr/rss/S1N1.xml",
    "http://www.newsdaily.kr/rss/S1N2.xml",
    "http://www.newsdaily.kr/rss/S1N30.xml",
    "http://www.newsdaily.kr/rss/S1N32.xml",
    "http://www.newsdaily.kr/rss/S1N38.xml",
    "http://www.newsdaily.kr/rss/S1N39.xml",
    "http://www.newsdaily.kr/rss/S1N4.xml",
    "http://www.newsdaily.kr/rss/S1N40.xml",
    "http://www.newsdaily.kr/rss/S1N46.xml",
    "http://www.newsdaily.kr/rss/S1N47.xml",
    "http://www.newsdaily.kr/rss/S1N49.xml",
    "http://www.newsdaily.kr/rss/S1N50.xml",
    "http://www.newsdaily.kr/rss/S1N51.xml",
    "http://www.newspost.kr/rss/allArticle.xml",
    "http://www.newspost.kr/rss/clickTop.xml",
    "http://www.newspost.kr/rss/S1N1.xml",
    "http://www.newspost.kr/rss/S1N2.xml",
    "http://www.newspost.kr/rss/S1N3.xml",
    "http://www.newspost.kr/rss/S1N4.xml",
    "http://www.newspost.kr/rss/S1N5.xml",
    "http://www.newspost.kr/rss/S1N6.xml",
    "http://www.newswith.co.kr/rss/allArticle.xml",
    "http://www.newswith.co.kr/rss/clickTop.xml",
    "http://www.newswith.co.kr/rss/S1N1.xml",
    "http://www.newswith.co.kr/rss/S1N10.xml",
    "http://www.newswith.co.kr/rss/S1N11.xml",
    "http://www.newswith.co.kr/rss/S1N2.xml",
    "http://www.newswith.co.kr/rss/S1N3.xml",
    "http://www.newswith.co.kr/rss/S1N4.xml",
    "http://www.newswith.co.kr/rss/S1N5.xml",
    "http://www.newswith.co.kr/rss/S1N6.xml",
    "http://www.newswith.co.kr/rss/S1N7.xml",
    "http://www.newswith.co.kr/rss/S1N8.xml",
    "http://www.newswith.co.kr/rss/S1N9.xml",
    "http://www.today-news.co.kr/rss/allArticle.xml",
    "http://www.today-news.co.kr/rss/clickTop.xml",
    "http://www.today-news.co.kr/rss/S1N1.xml",
    "http://www.today-news.co.kr/rss/S1N2.xml",
    "http://www.today-news.co.kr/rss/S1N3.xml",
    "http://www.today-news.co.kr/rss/S1N4.xml",
    "http://www.today-news.co.kr/rss/S1N5.xml",
    "http://www.today-news.co.kr/rss/S1N6.xml",
    "http://www.top-rider.com/rss/allArticle.xml",
    "http://www.top-rider.com/rss/clickTop.xml",
    "http://www.top-rider.com/rss/S1N1.xml",
    "http://www.top-rider.com/rss/S1N4.xml",
    "http://www.top-rider.com/rss/S1N5.xml",
    "http://www.top-rider.com/rss/S1N7.xml",
    "http://www.top-rider.com/rss/S1N8.xml",
    "http://www.top-rider.com/rss/S1N9.xml",
    "http://imnews.imbc.com/rss/news/news_00.xml",
]

def format_publication_date(published):
    """Convert the publication date to 'yyyymmddhhmm' format."""
    if not published or published == "No Date":
        return "unknown_date"
    try:
        return parser.parse(published).strftime("%Y%m%d%H%M")
    except Exception as e:
        print(f"Error formatting publication date: {e}")
        return "unknown_date"

def extract_date_from_html(soup):
    """Extract the most reliable date and time from the HTML content."""
    print("Attempting to extract date and time from HTML content...")
    meta_tags = [
        {"property": "article:published_time"},
        {"property": "og:published_time"},
        {"name": "pubdate"},
        {"name": "publish_date"},
        {"name": "date"},
    ]
    for tag in meta_tags:
        meta = soup.find("meta", tag)
        if meta and meta.get("content"):
            try:
                print(f"Found date in meta tag: {meta['content']}")
                return parser.parse(meta["content"]).strftime("%Y%m%d%H%M")
            except Exception as e:
                print(f"Error parsing meta tag date: {e}")

    spans = soup.find_all("span")
    for span in spans:
        date_text = span.get_text(strip=True)
        if re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", date_text):
            try:
                print(f"Found date in span: {date_text}")
                return parser.parse(date_text).strftime("%Y%m%d%H%M")
            except Exception as e:
                print(f"Error parsing span date: {e}")

    content = soup.get_text()
    date_time_pattern = re.compile(
        r"(\b\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}\b|\b\d{4}-\d{2}-\d{2}\b)"
    )
    match = date_time_pattern.search(content)
    if match:
        try:
            date_str = match.group()
            if ":" not in date_str:
                date_str += " 00:00"
            print(f"Found date using regex fallback: {date_str}")
            return parser.parse(date_str).strftime("%Y%m%d%H%M")
        except Exception as e:
            print(f"Error parsing fallback date: {e}")

    print("No date found in HTML content.")
    return "unknown_date"

def extract_date(rss_entry, soup=None):
    """Extract date from RSS or HTML content."""
    for field in ["published", "updated", "pubDate"]:
        if field in rss_entry and rss_entry[field]:
            date = format_publication_date(rss_entry[field])
            if date != "unknown_date":
                print(f"Found date in RSS feed ({field}): {date}")
                return date
    if soup:
        return extract_date_from_html(soup)
    print("No date found in RSS entry or HTML content.")
    return "unknown_date"

def sanitize_content(content):
    """Sanitize content for TSV and CSV."""
    sanitized = content.replace("\t", " ")
    sanitized = unicodedata.normalize('NFKD', sanitized).encode('utf-8', 'ignore').decode('utf-8')
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.strip()

def split_content_for_tsv(content, publication_date):
    """Split content into chunks of 3600 characters."""
    chunks = []
    suffix = 1
    while len(content) > 3600:
        split_index = content.rfind(" ", 0, 3600)
        if split_index == -1:
            split_index = 3600
        chunk = content[:split_index].strip()
        chunks.append((f"{publication_date}_{suffix}", chunk))
        content = content[split_index:].strip()
        suffix += 1
    if content:
        chunks.append((f"{publication_date}_{suffix}", content))
    return chunks

def sanitize_filename(name):
    """Sanitize filenames to remove special characters."""
    return re.sub(r'[\/:*?"<>|]', '_', name)

def download_from_rss_list(rss_urls, keywords=None, max_articles=100):
    """Fetch and process articles from a list of RSS feeds."""
    sanitized_keywords = sanitize_filename("_".join(keywords) if keywords else "all_articles")
    csv_filename = f"{sanitized_keywords}.csv"
    tsv_filename = f"{sanitized_keywords}-for-analysis-raw.tsv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Link", "Title", "Publication", "Publication Date", "Content"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with open(tsv_filename, mode="w", newline="", encoding="utf-8") as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            tsv_writer.writerow(["Publication Date", "Content"])

            options = Options()
            options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            for rss_url in rss_urls:
                print(f"Fetching RSS feed: {rss_url}")
                feed = feedparser.parse(rss_url)
                articles = feed.entries
                filtered_articles = articles if not keywords else [
                    article for article in articles if any(keyword.lower() in article.get("title", "").lower() for keyword in keywords)
                ]

                for i, article in enumerate(filtered_articles[:max_articles], start=1):
                    title = article.get("title", "No Title")
                    link = article.get("link", "No Link")
                    print(f"Processing article {i}: {title}")

                    try:
                        driver.get(link)
                        time.sleep(2)
                        soup = BeautifulSoup(driver.page_source, "html.parser")

                        formatted_date = extract_date(article, soup)
                        paragraphs = soup.find_all("p")
                        article_text = "\n".join(para.get_text() for para in paragraphs)
                        if not article_text.strip():
                            print(f"Skipping empty article at {link}")
                            continue

                        sanitized_content = sanitize_content(article_text)
                        writer.writerow({
                            "Link": link,
                            "Title": title,
                            "Publication": "",
                            "Publication Date": formatted_date,
                            "Content": sanitized_content,
                        })

                        chunks = split_content_for_tsv(sanitized_content, formatted_date)
                        for chunk_date, chunk_content in chunks:
                            tsv_writer.writerow([chunk_date, chunk_content])

                        print(f"Processed article {i}: {title}")

                    except Exception as e:
                        print(f"Failed to process article {link}: {e}")

            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py [<keyword1,keyword2,...>]")
        sys.exit(1)

    keywords = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    download_from_rss_list(rss_urls, keywords)