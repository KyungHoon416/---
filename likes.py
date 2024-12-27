from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd

# ChromeDriver 설정
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=service, options=options)

# 인스타그램 로그인
def login_instagram(username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)

# 특정 태그 크롤링
def crawl_hashtag_with_likes(hashtag, max_posts=10):
    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
    time.sleep(5)

    # 게시물 링크 수집
    links = set()
    while len(links) < max_posts:
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        for post in posts:
            links.add(post.get_attribute("href"))
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    # 게시물 정보 수집
    posts_data = []
    for link in list(links)[:max_posts]:
        driver.get(link)
        time.sleep(3)

        # BeautifulSoup로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # print(f"driver.page_source {driver.page_source}")
        # print(f"soup {soup}")

        # 게시물 텍스트
        try:
            content = soup.find('div', {'class': '_a9zs'}).text
        except AttributeError:
            content = "No text available"

        # 사용자 정보
        try:
            user_tag = soup.find('a', {'class': '_a6hd'}).text
            profile_url = "https://www.instagram.com" + soup.find('a', {'class': '_a6hd'})['href']
        except AttributeError:
            user_tag = "Unknown"
            profile_url = "Unknown"

        # 좋아요 수 (수정된 접근 방식)
        try:
            likes_element = soup.find('span', string=lambda text: 'like' in text.lower())
            if likes_element:
                likes = likes_element.text
            else:
                likes = "Could not retrieve"
        except Exception:
            likes = "Could not retrieve"

        posts_data.append({
            "post_link": link,
            "content": content,
            "user": user_tag,
            "profile_url": profile_url,
            "likes": likes
        })

    return pd.DataFrame(posts_data)

# 실행
try:
    login_instagram("kyunghoon416", "1q2w3e4r!@")  # 인스타그램 계정 입력
    hashtag_data = crawl_hashtag_with_likes("python", max_posts=10)
    hashtag_data.to_csv("instagram_posts_with_likes.csv", index=False)
    print("Data saved to instagram_posts_with_likes.csv")
finally:
    driver.quit()
