from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import urllib.request
import os

# 검색쿼리
searchKey = input('검색할 키워드 입력 :')
cnt_num = input('받을 이미지 개수: ')

# 폴더 생성
def createFolder(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError:
        print('Error')

createFolder(f'train_dataset/{searchKey}')

driver = webdriver.Chrome()

# 이미지 스크롤링
i = 0
all_count = 0
e_count = 0

print(int(cnt_num))

while True:
    driver.get('https://www.google.co.kr/search?q=Economy&sca_esv=f874127852d0764a&sca_upv=1&biw=929&bih=917&udm=2&ei=2QxTZorlCb-Mvr0P7IOP6AQ&start='+str(i)+'&sa=N')
    count = 0

# 이미지 수집 및 저장
    while True:
        image = driver.find_elements(By.XPATH, 
                    '/html/body/div[4]/div/div[13]/div/div[2]/div[2]/div/div/div/div/div[1]/div/div/div['+str(count+1)+']/div[2]/h3/a')
        if image:
            print(count, image)
            
            try:
                image[0].click()
                time.sleep(3)

                imgUrl = driver.find_element(By.XPATH,
                        '/html/body/div[6]/div/div/div/div/div/div/c-wiz/div/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div/div[3]/div[1]/a/img[1]').get_attribute("src")
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(imgUrl, f'train_dataset/{searchKey}/{searchKey}_{str(all_count)}.jpg') # url을 
                all_count += 1
                print(f'--{all_count}번째 이미지 저장 완료--')
                count += 1
            
            except Exception as e:
                e_count += 1
                print('Error: ', e_count)
                pass
        else:
            break

        if all_count >= int(cnt_num):
            break

    if all_count >= int(cnt_num):
        break
    else:
        i += 10

print(f'--작업이 끝났습니다--')
driver.close()