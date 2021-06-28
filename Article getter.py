# Library inmport
import time
import requests
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.remote import file_detector
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup

# deep Lに突っ込む
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
    # 必要情報の入力
    search_keyword = input('Enter word:>>>')
    pages = input('Enter number how many pages do you want to get>>>')
    if pages.isdecimal()==False:
        print('Error...input number. execution is terminated.')
        exit()
    file_name = input('Enter file name>>>')

    # 初期設定
    col = ['title', 'link', 'publisher', 'abstract', 'abstract_ja']
    df = pd.DataFrame([], columns=col)
    page = 0

    # driverを起動、Google Chromeを使うこと
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # Webサイトを開く
    driver.get("https://scholar.google.com/")
    time.sleep(3)
    # 検索窓に入力
    driver.find_element_by_name("q").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_name("btnG").click()
    time.sleep(3)
    
    # 繰り返し処理
    while page < int(pages):
        current_url = driver.current_url
        html = requests.get(current_url)
        soup = BeautifulSoup(html.text, "lxml")
        articles = soup.find_all(class_="gs_rt")
        abst11 = soup.find_all(class_="gs_rs")

        for article, abst in zip(articles, abst11):
            try:
                title = article.text
                link = article.find_all("a")[0].get('href')
                publisher = link[8:link.find("/", 8)]
                abst1 = abst.text.replace('\n', ' ')
                # translate with deepL
                abst1_ja = translate(abst1)

                element = pd.Series([title, link, publisher, abst1, abst1_ja], index = col)
                df = df.append(element, ignore_index=True)
            except:
                pass
        
        # 次のページへ
        driver.find_element_by_xpath("//*[@id='gs_n']/center/table/tbody/tr/td[12]/a").click()
        time.sleep(3)
        page += 1
    df.to_csv(file_name+'.csv')

if __name__ == '__main__':
    main()
