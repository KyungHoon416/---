from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd

# ChromeDriver 경로 설정
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # 브라우저 최대화
driver = webdriver.Chrome(service=service, options=options)

# 인스타그램 로그인
def login_instagram(username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)  # 로그인 대기

# 특정 태그 검색 및 크롤링
def crawl_hashtag_with_likes(hashtag, max_posts=10):
    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
    time.sleep(5)

    # 게시물 링크 수집
    links = set()
    while len(links) < max_posts:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for link in soup.find_all('a', href=True):
            if '/p/' in link['href']:
                links.add("https://www.instagram.com" + link['href'])
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    # 게시물 내용, 사용자 정보 및 좋아요 수 수집
    posts = []
    for link in list(links)[:max_posts]:
        driver.get(link)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 게시물 내용
        try:
            content = soup.find('div', {'class': '_a9zr'}).text
        except AttributeError:
            content = "No text available"

        # 사용자 프로필 정보
        try:
            user_tag = soup.find('a', {'class': '_a6hd'}).text
            profile_url = "https://www.instagram.com" + soup.find('a', {'class': '_a6hd'})['href']
        except AttributeError:
            user_tag = "Unknown"
            profile_url = "Unknown"

        # 좋아요 수
        try:
            like_element = soup.find('div', {'class': '_aacl _aaco _aacw _aacx _aad7 _aade'}).text
            likes = like_element.split(' ')[0]  # 숫자만 가져옴
        except AttributeError:
            likes = "0"

        # 팔로워 수 확인
        followers = "N/A"
        try:
            driver.get(profile_url)
            time.sleep(3)
            profile_soup = BeautifulSoup(driver.page_source, 'html.parser')
            followers = profile_soup.find('a', href=f"/{user_tag}/followers/").find('span').text
        except Exception:
            followers = "Could not retrieve"

        posts.append({
            "post_link": link,
            "content": content,
            "user": user_tag,
            "profile_url": profile_url,
            # "likes": likes,
            "followers": followers
        })

    return pd.DataFrame(posts)

# 실행
try:
    login_instagram("kyunghoon416", "1q2w3e4r!@")  # 인스타그램 계정 입력
    hashtag_data = crawl_hashtag_with_likes("python", max_posts=10)
    hashtag_data.to_csv("instagram_user_data_with_likes.csv", index=False)
    print("Data saved to instagram_user_data_with_likes.csv")
finally:
    driver.quit()
