import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import datetime
import pandas as pd
import logging

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

# main処理


def main():
  
    #########################
    nowTime = datetime.datetime.now()
    formatter = '%(asctime)s:%(message)s'
    #logレベルをINFOに設定し、logをファイルに出力する
    logging.basicConfig(filename='{0:%Y%m%d%H%M}_log.log'.format(nowTime), level=logging.INFO,format=formatter)
    # logging.info('info {} {}' .format(f,'件目会社名：'))
    # logging.info('info %s' % 'ロギング開始')
    logging.info('info {}' .format('ロギング開始'))
    ###########################
    # search_keyword = "高収入"
    print("検索キーワードを入力してください：")
    # 標準入力の値を取得
    search_keyword = input()
    logging.info('info {} {}' .format('検索キーワード：',search_keyword))
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    #5秒間処理を止める
    time.sleep(5)
 
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
    
    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

     # ページ終了まで繰り返し取得
    exp_name_list = []#会社名
    contents_list = []#仕事内容
    salary_list = []#給与

    #会社名のリストのインデックスを指定するためのカウンタ
    i = 0
    #ページ数のカウント
    pageCount = 1
    logging.info('info {} {}' .format(pageCount,'ページ目取得開始：'))
    #次のページが無くなるまで繰り返す
    while True:

        # 検索結果の一番上の会社名を取得
        # name_list = driver.find_elements_by_class_name("cassetteRecruit__name","cassetteRecruitRecommend__name")
        
        #cassetteRecruit__nameクラスの要素を取得
        name_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__name")
        #tableCondition__head(thタグ)の要素を取得
        th_list = driver.find_elements_by_css_selector(".cassetteRecruit__content .tableCondition__head")
        #(tdタグ)の要素を取得
        td_list = driver.find_elements_by_css_selector(".cassetteRecruit__content .tableCondition__body")
        try:
            #############################################
            #１ページに記載されている求人情報の数を取得
            print(len(name_list))
            
            #会社名を取得し、リストへ追加する
            for name in name_list:
                exp_name_list.append(name.text)
            #tableタグの<th>とついになる<td>の値を取得する(仕事内容と給与)
            for th,td in zip(th_list,td_list):
                if th.text == '仕事内容':
                    #<th>が仕事内容の時
                    if len(exp_name_list) > i:
                        #会社名をprintする
                        print('会社名：'+exp_name_list[i])
                        logging.info('info {} {} {}' .format(i+1,'件目会社名：',exp_name_list[i]))
                        # print('会社名：'+name.text)
                        # i += 1
                    #仕事内容をprintする
                    print(th.text+':'+td.text)
                    contents_list.append(td.text)
                    logging.info('info {} {} {}' .format(i+1,'件目仕事内容：',td.text))
                #<th>が給与の時
                elif th.text == '給与':
                    #給与をprintする
                    print(th.text+':'+td.text)
                    salary_list.append(td.text)
                    logging.info('info {} {} {}' .format(i+1,'件目給与：',td.text))
                    i += 1
            ############################################

            pages = driver.find_elements_by_class_name("iconFont--arrowLeft")
            # print(len(pages))
            #次へボタンがなくなったらwhile文を抜ける
            if len(pages) == 0:
                break
            else:
                #get_attribute("href")で次へボタンのリンクを取得
                next_page = pages[0].get_attribute("href")
                # print(next_page)
                #取得したurl先を開く
                driver.get(next_page)
                #相手側のサーバーに負荷をかけなように2秒間処理を止める
                time.sleep(2)
                
                pageCount += 1
                logging.info('info {} {}' .format(pageCount,'ページ目取得開始：'))

            

    #################
            # print(i)

            # 1ページ分繰り返し
            # print(len(name_list))
            # for name in name_list:
            #     exp_name_list.append(name.text)
            #     print(name.text)
        except Exception as e:
            logging.info('info {} {}' .format('例外発生：',e))
            print('例外発生'+e)

    logging.info('info {}' .format('CSVファイル書き込み開始：'))
    #抽出結果をcsvファイルへ書き込み保存する
    df = pd.DataFrame({"会社名":exp_name_list,
                "仕事内容":contents_list,
                "給与":salary_list})
    # print('dfを表示')
    df.to_csv("search_results.csv")
    logging.info('info {}' .format('CSVファイル書き込み成功：'))
  


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
