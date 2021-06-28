# Library inmport
import os
import time
import requests
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup

# 以下関数は未使用
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless') # 画面を表示せずに動作するモード

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

# deep Lに突っ込む関数、使わない
def translate(text):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get("https://www.deepl.com/ja/translator")
    time.sleep(3)

    driver.find_element_by_xpath("//*[@id='dl_translator']/div[5]/div[3]/div[1]/div[2]/div[1]/textarea").send_keys(text)
    time.sleep(10)

    after = driver.find_element_by_xpath("//*[@id='dl_translator']/div[5]/div[3]/div[3]/div[3]/div[1]/textarea").get_attribute('value')
    driver.quit()
    
    return after

# main処理
def main():
    search_keyword = input('Enter word:')
    pages = input('Enter number how many pages do you want to get')
    # driverを起動、Google Chromeを使うこと
    driver = webdriver.Chrome(ChromeDriverManager().install())

    col = ['title', 'link', 'publisher', 'abstract', 'abstract_ja']
    df = pd.DataFrame([], columns=col)

    '''    
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    else:
        driver = set_driver("chromedriver_linux", False)
    '''

    # Webサイトを開く
    driver.get("https://scholar.google.com/")
    time.sleep(3)
    
    # 検索窓に入力
    driver.find_element_by_name("q").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_name("btnG").click()
    time.sleep(3)
    
    page = 1
    while page < pages:
        current_url = driver.current_url
        html = requests.get(current_url)
        soup = BeautifulSoup(html.text, "lxml")
        articles = soup.find_all(class_="gs_rt")
        abst11 = soup.find_all(class_="gs_rs")

    #    for article in articles:
        for i in range(len(articles)):
            try:
                title = articles[i].text
                link = articles[i].find_all("a")[0].get('href')
                publisher = link[8:link.find("/", 8)]
                abst1 = abst11[i].text.replace('\n', ' ')
                # translate with deepL
                # open DeepL
                driver.get("https://www.deepl.com/ja/translator")
                time.sleep(3)
                driver.find_element_by_xpath("//*[@id='dl_translator']/div[5]/div[3]/div[1]/div[2]/div[1]/textarea").send_keys(abst1)
                time.sleep(10)
                abst1_ja = driver.find_element_by_xpath("//*[@id='dl_translator']/div[5]/div[3]/div[3]/div[3]/div[1]/textarea").get_attribute('value')
                driver.quit()
                # abst1_ja = translate(abst1)

                element = pd.Series([title, link, publisher, abst1, abst1_ja], index = col)
                df = df.append(element, ignore_index=True)
            except:
                pass
        
        driver.find_element_by_xpath("//*[@id='gs_n']/center/table/tbody/tr/td[12]/a").click()
        time.sleep(3)
        page += 1
        
    df.to_csv('data.csv')

if __name__ == '__main__':
    main()
