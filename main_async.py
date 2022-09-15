import datetime
import aiohttp
from datetime import date, datetime, timedelta
import asyncio
from bs4 import BeautifulSoup
import time
from sqlalchemy import  insert
from models import models
from schemas.schemas import ItemSchemas
from core.db import db

books_data = []
start_time = time.time()


async def get_datetime_from_string(date_string) -> date:
    now = date.today()
    if "minutes ago" in date_string:
        time = date_string.strip().replace("minutes ago", '')
        date_string = datetime.strptime(str(now - timedelta(minutes=int(time))).strip(), "%Y-%m-%d").date()
    elif "minute ago" in date_string:
        time = date_string.strip().replace("minute ago", '')
        date_string = datetime.strptime(str(now - timedelta(minutes=int(time))).strip(), "%Y-%m-%d").date()
    elif "hours ago" in date_string:
        times = date_string.strip().replace("hours ago", '')
        date_string = datetime.strptime(str(now - timedelta(hours=int(times))).strip(), "%Y-%m-%d").date()
    elif "Yesterday" in date_string:
        date_string = datetime.strptime(str(now - timedelta(days=1)).strip(), "%Y-%m-%d").date()
    else:
        date_string = datetime.strptime(str(date_string).strip(), "%d/%m/%Y").date()
    return date_string


async def get_page_data(session, page):
    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273"
    async with session.get(url=url) as response:
        response_text = await response.text()
        print(url)
        soup = BeautifulSoup(response_text, "lxml")
        list_items = soup.find_all("div", class_="search-item")
        for i in list_items:
            item = ItemSchemas(
                photo=i.find('div', class_="image").find('img').get('src'),
                title=i.find('div', class_="title").find('a').get_text().strip(),
                location=i.find('div', class_="location").find('span').get_text().strip(),
                date_posted=await get_datetime_from_string(
                    i.find('div', class_="location").find('span', class_="date-posted").get_text().strip('<')),
                beds=i.find('div', class_="rental-info").find('span', class_="bedrooms").get_text().replace("\n",
                                                                                                            " ").strip(),
                description=i.find('div', class_="description").get_text().replace("\n", " ").strip(),
                price=i.find('div', class_="price").get_text().strip()
            )

            books_data.append(item)
        print(f"[INFO] Обработал страницу {page}")


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, 10):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def save_data(data:list):
    await db.connect()

    with open(f'{1}.html', 'w') as file:
        file.write(str(data))
    for i in data:
        item_dict = i.dict()
        query = insert(models.Item).values(**item_dict)
        await db.execute(query)

    await db.disconnect()


def main():
    asyncio.run(gather_data())
    asyncio.run(save_data(data=books_data))
    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")


if __name__ == "__main__":
    main()
