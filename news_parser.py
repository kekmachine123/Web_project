from bs4 import BeautifulSoup
import requests


class NewsFromInternet:
    def get_vl_ru_news(self):
        res = requests.get("https://www.newsvl.ru/")
        if not res:
            return f"Ошибка выполнения запроса Http статус:", {res.status_code}, "(", {res.reason}, ")"
        soup = BeautifulSoup(res.content, 'html.parser')

        news = soup.find_all('div', class_='story-list__item-content')

        articles = []
        for i in news[:14]:
            articles.append((i.find('a').get('href')))

        allnws = []
        news_p = ['https://www.newsvl.ru' + i for i in articles]
        for i in news_p:
            allnws.append(self.f(i))
        for i in range(len(allnws)):
            allnws[i]["id"] = str(i + 1)
        return allnws

    def f(self, url):
        req = requests.get(url)
        if not req:
            return url, f"Http статус:", {req.status_code}, "(", {req.reason}, ")"
        soup = BeautifulSoup(req.content, "html.parser")
        news_info = {"heading": soup.find('h1', class_='story__title').text,
                     "text": soup.find('div', class_='story__text').text,
                     "date": soup.find('span', class_="story__info-date").text,
                     "img_src": soup.find('img', class_="story__image_main").get('src')}
        return news_info



