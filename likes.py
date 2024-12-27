from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    time.sleep(3)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)  # 로그인 대기

# 특정 태그 검색 및 게시물 좋아요 포함 크롤링
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

    # 게시물 내용, 사용자 정보 및 좋아요 수 수집
    posts_data = []
    for link in list(links)[:max_posts]:
        driver.get(link)
        time.sleep(3)

        # 게시물 내용
        try:
            content = driver.find_element(By.XPATH, "//div[contains(@class, '_a9zs')]").text
        except Exception as e:
            print(f"Error fetching content for {link}: {e}")
            content = "No text available"

        # 사용자 프로필 정보
        try:
            user_tag = driver.find_element(By.XPATH, "//a[contains(@class, '_a6hd')]").text
            profile_url = driver.find_element(By.XPATH, "//a[contains(@class, '_a6hd')]").get_attribute("href")
        except Exception as e:
            print(f"Error fetching user info for {link}: {e}")
            user_tag = "Unknown"
            profile_url = "Unknown"

        # 좋아요 수
        try:
            likes_element = driver.find_element(By.XPATH, "//span[contains(text(), 'likes') or contains(text(), 'like')]")
            likes = likes_element.text
        except Exception as e:
            print(f"Error fetching likes for {link}: {e}")
            likes = "0"

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
