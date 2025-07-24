from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

options = Options()  
options.add_argument("user-agent")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

links = []
theme_file = "themes.json"
link_theme = []

# varsa eski temaları yüklüyorum.
if os.path.exists(theme_file):
    with open(theme_file, "r", encoding="utf-8") as f:
        link_theme = json.load(f)
        existing_names = {entry["name"] for entry in link_theme}
else:
    existing_names = set()

# tüm sayfalarıdaki filmlerin linklerini alıyorum.
for page in range(1, 143):
    url = f"https://letterboxd.com/imthelizardking/list/all-the-movies-10k-views-4/page/{page}/"
    driver.get(url)
    try:
        ul = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "js-list-entries")))
        li_list = ul.find_elements(By.TAG_NAME, "li")
        for li in li_list:
            href = None
            try:
                a_tag = li.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")
            except:
                try:
                    div_tag = li.find_element(By.CSS_SELECTOR, "div.really-lazy-load")
                    data_link = div_tag.get_attribute("data-target-link")
                    if data_link:
                        href = "https://letterboxd.com" + data_link
                except:
                    continue
            if href:
                links.append(href)
    except:
        pass



# her film için tema bilgilerini çekiyorum.
count = 1
nan = 0

for link in links:
    link_split = link.strip("/").split("/")
    name = link_split[-1].replace("-", " ")
    if name in existing_names:
        print(f"{count}: {name} zaten var")
        count += 1
        continue

    themes = []
    genre_url = f"{link}genres/"
    driver.get(genre_url)

    try:
        tab_genres = wait.until(EC.presence_of_element_located((By.ID, "tab-genres")))
        divs = tab_genres.find_elements(By.TAG_NAME, "div")
        a_list = divs[1].find_elements(By.TAG_NAME, "a")
        for a in a_list[:-1]:
            themes.append(a.text)

        entry = {
            "name": name,
            "theme": themes
        }
    except:
        entry = {
            "name": name,
            "theme": "NaN"
        }
        nan += 1

    link_theme.append(entry)

    # temaları tek tek json dosyasına ekiliyorum.
    with open(theme_file, "w", encoding="utf-8") as f:
        json.dump(link_theme, f, indent=4, ensure_ascii=False)

    print(f"{count}: {name}")
    count += 1

driver.quit()
print(f"toplam NaN theme: {nan}")
