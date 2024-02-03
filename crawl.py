from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

options=Options()
# options.add_argument("--headless=new")
# options.set_preference('intl.accept_languages', 'en-US')
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

driver=webdriver.Chrome(options=options)
driver.get(r"https://www.imdb.com/chart/top/?ref_=nv_mv_250")
all_links=driver.find_elements(By.CLASS_NAME,"ipc-title-link-wrapper")
links=[]
for i in all_links:
    links.append(i.get_attribute("href"))

film_ids=[]
titles=[]
years=[]
parental_guides=[]
runtimes=[]
genres=[]
directors=[]
writers=[]
stars=[]
box_offices=[]
people={}

# links[:-8]
count=0
for link in links[:-8]:
    film_ids.append(link.split("/")[-2][2:])
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)

    title=driver.find_element(By.XPATH,"/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span")
    # print(title.text)
    titles.append(title.text)

    year=driver.find_element(By.XPATH,"/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a")
    # print(year.text)
    years.append(year.text)

    runtime=driver.find_element(By.XPATH,"/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]")
    # print(runtime.text)               "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[2]"
    h = (runtime.text.split())[0][:-1]
    m = (runtime.text.split())[1][:-1]
    runtime_min = int(h) * 60 + int(m)
    runtimes.append(runtime_min)
    # print(runtime_min)

    parental_guide=driver.find_element(By.XPATH,"//*[@id=\"__next\"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[2]/a")
    parental_guides.append(parental_guide.text)

    genre=driver.find_element(By.XPATH,"//*[@id=\"__next\"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]")
    # print(genre.text)
    g = []
    g.append(genre.text.split("\n"))
    genres.append(g)

    parent_ul = driver.find_element(By.XPATH,'/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]/div/ul')
    director_elements = parent_ul.find_elements(By.TAG_NAME, 'li')
    director = [elem.text for elem in director_elements]
    # print("directors: ",director)
    directors.append(director)
    d_link = parent_ul.find_elements(By.TAG_NAME, 'a')
    d_links = [i.get_attribute("href").split("/")[-2][2:] for i in d_link]
    for i in range(len(director)):
        people[d_links[i]] = director[i]

    parent_ul = driver.find_element(By.XPATH,'/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]/div/ul')
    writer_elements = parent_ul.find_elements(By.TAG_NAME, 'li')
    writer = [elem.text for elem in writer_elements]
    # print("writers: ",writer)
    writers.append(writer)
    w_link = parent_ul.find_elements(By.TAG_NAME, 'a')
    w_links = [i.get_attribute("href").split("/")[-2][2:] for i in w_link]
    for i in range(len(writer)):
        people[w_links[i]] = writer[i]

    parent_ul = driver.find_element(By.XPATH,'/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[3]/div/ul')
    star_elements = parent_ul.find_elements(By.TAG_NAME, 'li')
    star = [elem.text for elem in star_elements]
    # print("stars: ",star)
    stars.append(star)
    s_link = parent_ul.find_elements(By.TAG_NAME, 'a')
    s_links = [i.get_attribute("href").split("/")[-2][2:] for i in s_link]
    for i in range(len(star)):
        people[s_links[i]] = star[i]



    try:
        box = driver.find_element(By.XPATH,"//li[@data-testid='title-boxoffice-grossdomestic']//span[@class='ipc-metadata-list-item__list-content-item']")
        box = box.text.replace("$", "").replace(",", "")
    except:
        box=None

    # print(box)
    box_offices.append(box)

    count += 1
    print(count)




df={"film_ids":film_ids,
"titles":titles,
"years":years,
"parental_guides":parental_guides,
"runtimes":runtimes,
"genres":genres,
"directors":directors,
"writers":writers,
"stars":stars,
"box_offices":box_offices

}
data=pd.DataFrame(df)

people_df=pd.DataFrame({"artist_name":people.values(),"artist_id":people.keys()})

# print(data)
# print("-----------------------------------------------------------------")
# print(people)