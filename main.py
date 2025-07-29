import datetime
import aiohttp
from bs4 import BeautifulSoup
import json
import asyncio


def check_tipa(priority, sogl, true_priority, mode):
    if mode == 1:  # Все кроме забравших
        return True
    if mode == 2:  # Приоритет 1,2
        return priority <= 2
    if mode == 3:  # Проходной приоритет + согласие
        return true_priority and sogl


async def get_place_mpei(session, url, ids):
    req_url = f"https://pk.mpei.ru/inform/list{url}.html"
    try:
        async with session.get(req_url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
            else:
                return "Something went wrong ebana"
    except Exception:
        return "Error occurred"

    i1 = 1
    i2 = 1
    i3 = 1
    norm = {}
    tables = soup.find_all("table")
    lines = []
    for table in tables:
        lines.extend([tr for tr in table.find_all("tr") if tr.parent.name != "thead"])

    for line in lines:
        pars = [item.text for item in line.find_all("td")]
        id = pars[0]
        sogl = pars[-6] == "да"
        priority = int(pars[-5])
        true_priority = pars[-3] == "да"

        if id in ids:
            norm[ids[id]] = (i1, i2, i3)
            if len(norm) == len(ids.keys()):
                return norm

        true_priority = pars[-3] == "да"
        if id in ids:
            norm[ids[id]] = (i1, i2, i3)
            if len(norm) == len(ids):
                return norm
        if check_tipa(priority, sogl, true_priority, 1):
            i1 += 1
        if check_tipa(priority, sogl, true_priority, 2):
            i2 += 1
        if check_tipa(priority, sogl, true_priority, 3):
            i3 += 1

    return norm


async def get_places_mpei(urls, ids):
    places = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, name in urls.items():
            task = get_place_mpei(session, url, ids)
            tasks.append((name, task))

        for name, task in tasks:
            places[name] = await task

    good_data = make_data_good(places)
    time = datetime.datetime.now()
    good_data["time"] = time
    return good_data


async def get_place_mgsu(session, url, ids):
    req_url = f"https://mgsu.ru/2025/ks/bs/list.php?{url}"
    try:
        async with session.get(req_url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
            else:
                return "Something went wrong ebana"
    except Exception:
        return "Error occurred"
    lines = soup.find_all("tr", {"class": "data-row"})
    i1, i2, i3 = 1, 1, 1
    norm = {}
    for line in lines:
        pars = [item.text for item in line.find_all("td")]
        id_ = pars[1]
        sogl = pars[-9] == "✓"
        priority = int(pars[-8])
        true_priority = pars[-4] == "✓"
        if id_ in ids:
            norm[ids[id_]] = (i1, i2, i3)
            if len(norm) == len(ids):
                return norm
        if check_tipa(priority, sogl, true_priority, 1):
            i1 += 1
        if check_tipa(priority, sogl, true_priority, 2):
            i2 += 1
        if check_tipa(priority, sogl, true_priority, 3):
            i3 += 1
    return norm


async def get_places_mgsu(urls, ids):
    places = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, name in urls.items():
            task = get_place_mgsu(session, url, ids)
            tasks.append((name, task))

        for name, task in tasks:
            places[name] = await task

    good_data = make_data_good(places)
    time = datetime.datetime.now()
    good_data["time"] = time
    return good_data


def make_data_good(data):
    good_data = {}
    for direction in data:
        for name in data[direction]:
            if name not in good_data:
                good_data[name] = {}
            good_data[name][direction] = data[direction][name]
    return good_data


def user_friendly_data(data):
    output = ""
    for name in data:
        if name != "time":
            output += f"{name}\n"
            for faculty, values in data[name].items():
                output += f"    {faculty}: {values}\n"
    time = data["time"].strftime("%d.%m.%Y %H:%M")
    output += f"\nИнформация последний раз обновлялась: {time}"
    return output


def update_data_file(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4, default=repr)


def get_data_file():
    with open("data.json", "r") as f:
        data = json.load(f)
        data["time"] = eval(data["time"])
    return data


async def main():
    # urls = {"581bacc": "ПМИ", "1986bacc": "ФИ", "14bacc": "ИВТ", "35bacwe": "ПИ"}
    # ids = {"3844150": "Илья", "4216913": "Дима"}
    # data = await get_places(urls, ids)
    # output = user_friendly_data(data)
    # print(output, type(output))
    # update_data_file(data)
    # print(get_data_file())
    urls = {
        "p=000000012_08.03.01_Stroitelstvo_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Строительство",
        "p=000000012_23.05.01_Nazemnye_transportno-tekhnologicheskie_sredstva_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Наземные транспортно-технологические средства",
        "p=000000012_21.03.02_Zemleustroystvo_i_kadastry_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Землеустройство и кадастры",
        "p=000000012_20.03.01_Tekhnosfernaya_bezopasnost_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Техносферная безопасность",
        "p=000000012_15.03.04_Avtomatizatsiya_tekhnologicheskikh_protsessov_i_proizvodstv_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Автоматизация технологических процессов и производств",
        "p=000000012_08.03.01_Stroitelstvo_Filial_Ochnaya_Byudzhet_Obshchiy%20konkurs.html": "Строительство Филиал",
    }
    ids = {"4227920": "хачина"}
    data = await get_places_mgsu(urls, ids)
    output = user_friendly_data(data)
    print(output, type(output))
    update_data_file(data)
    print(get_data_file())


if __name__ == "__main__":
    asyncio.run(main())
