import requests
from bs4 import BeautifulSoup
import re
import os


class Scraper:
    """Scrape text data from wikipedia top 50 report per year"""

    def __init__(self, url: str) -> None:
        self.url = url
        self.titles = []
        self.result = []

    def get_titles(self):
        page = requests.get(self.url)
        if page.status_code != 200:
            raise Exception(f"Error get request: {self.url}")
        soup = BeautifulSoup(page.content, "html.parser")
        soup = soup.find_all(class_="wikitable")[0]
        soup = soup.find_all(["tr"])
        for row in soup[1:]:
            title, article_type = row.find_all("td")[1:3]
            title = title.a.get("href")
            article_type = article_type.select("img")[0].parent.get("title")
            if article_type != "List-Class article":
                self.titles.append(title.replace("/wiki/", ""))
        print(f"Number of wikipages: {len(self.titles)}")
        return self.titles

    def get_text(self, url: str) -> str:
        url = f"https://en.wikipedia.org/wiki/{url}"
        print(url)
        page = requests.get(url)
        if page.status_code != 200:
            raise Exception(f"Error get request: {url}")
        soup = BeautifulSoup(page.content, "html.parser")
        soup = soup.find_all("p")
        articles = []
        for article in soup[1:]:
            article = article.text.strip()
            article = re.sub(r"\[[0-9]+\]", "", article)  # noqa
            articles.append(article)
        return articles

    def save(self, file_path, articles: list[str]) -> bool:
        try:
            with open(file_path, mode="w") as f:
                for article in articles:
                    f.write(article)
            return True
        except Exception as e:
            print(f"Error {e} save: {file_path}")
            return False

    def run(self, folder_path: str, index_start: int):
        print(f"Start scrape: {self.url}\n\n")
        self.get_titles()
        for i, title in enumerate(self.titles):
            articles = self.get_text(title)
            file_path = os.path.join(folder_path, f"{i+index_start}-{title}.txt")
            self.save(file_path, articles)
        print("Done\n\n")


if __name__ == "__main__":
    urls = [
        "https://en.wikipedia.org/wiki/Wikipedia:2020_Top_50_Report",
        "https://en.wikipedia.org/wiki/Wikipedia:2021_Top_50_Report",
        "https://en.wikipedia.org/wiki/Wikipedia:2022_Top_50_Report",
        "https://en.wikipedia.org/wiki/Wikipedia:2023_Top_50_Report",
    ]
    index = 1
    for url in urls:
        scraper = Scraper(url=url)
        scraper.run("../data", index)
        index += len(scraper.titles)
