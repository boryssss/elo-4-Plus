import re
from funkcje import *
import schedule
import time
import time
from fbchat_muqit import Client, ThreadType
import asyncio


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def wiadomosc(zastepstwa, zastepstwa_bez, klasy):
    odbiorcy = []
    cookies_path = "dane.json"
    bot = await Client.startSession(cookies_path)
    time.sleep(5)
    print('Logowanie')
    if await bot.isLoggedIn():
        lista_odbiorcow = await bot.fetchThreadList()
        print(lista_odbiorcow)
        time.sleep(5)
        print('Odbiorcy')
        for odbiorca in lista_odbiorcow:
            nick = odbiorca.nickname
            thread = odbiorca.uid
            message_count = odbiorca.message_count
            if nick is None:
                wiadomosci = await bot.fetchThreadMessages(thread_id=thread)
                time.sleep(2)
                wiadomosc = wiadomosci[-1]
                nick = wiadomosc.text
                await bot.changeNickname(nick.upper(), thread, thread_id=thread)
                await bot.changeNickname('Zastępstwa - LO4', '61571933631388', thread_id=thread)
                odbiorcy.append([thread, nick, 1, odbiorca.name])
                time.sleep(2)

            else:
                if odbiorca.own_nickname is None:
                    await bot.changeNickname('Zastępstwa - LO4', '61571933631388', thread_id=thread)

                else:
                    odbiorcy.append([thread, nick, 0, odbiorca.name])

        print('Wysyłanie')
        time.sleep(10)
        for odbiorca in odbiorcy:
            uid = odbiorca[0]
            klasa = odbiorca[1]
            czy_doslac = odbiorca[2]
            name = odbiorca[3]
            if klasa in klasy:
                wiadomosc = zastepstwa[klasa]
                if wiadomosc != 'Br.Zm':
                    print('Wysyłam - ', uid, name, datetime.now())
                    print(wiadomosc)
                    await bot.sendMessage(wiadomosc, uid, ThreadType.USER)
                else:
                    if czy_doslac == 1:
                        print('Wysyłam - warunek - ', name, uid, datetime.now())
                        print(zastepstwa_bez[klasa])
                        await bot.sendMessage(zastepstwa_bez[klasa], uid, ThreadType.USER)

                    else:
                        print('Nie wysłam - ', uid, name, datetime.now())

            time.sleep(3)

        print('Stop')
        await bot.stopListening()


def poniedzialek_piatek():
    godziny = ['06:30', '07:00', '07:30', '07:55', '08:50', '09:45', '10:40', '11:45', '12:40', '13:35', '14:30', '15:25']
    for hour in range(16, 22):
        godziny.append(f'{hour:02}:00')
        godziny.append(f'{hour:02}:30')

    for godzina in godziny:
        schedule.every().monday.at(godzina).do(zastepstwa_calosc)
        schedule.every().tuesday.at(godzina).do(zastepstwa_calosc)
        schedule.every().wednesday.at(godzina).do(zastepstwa_calosc)
        schedule.every().thursday.at(godzina).do(zastepstwa_calosc)
        schedule.every().friday.at(godzina).do(zastepstwa_calosc)


def niedziela():
    godziny = []
    for hour in range(14, 24):
        godziny.append(f'{hour}:30')
        godziny.append(f'{hour}:00')

    for godzina in godziny:
        schedule.every().sunday.at(godzina).do(zastepstwa_calosc)


def uwagi_odczyt():
    file_path = "uwagi.txt"
    with open(file_path, 'r', encoding="utf-8") as uwagi_odczyt:
        uwagi_odczyt = uwagi_odczyt.readlines()

    uwagi_temp = []
    for linijka in uwagi_odczyt:
        if linijka[-1] == '\n':
            uwagi_temp.append(linijka[:-1])

        else:
            uwagi_temp.append(linijka)

    uwagi_temp.remove(uwagi_temp[0])
    uwagi = []
    for uwaga in uwagi_temp:
        uwaga = uwaga.split("_")
        if len(uwaga[1]) == 2:
            uwagi.append(uwaga)

        else:
            klasy = uwaga[1].split(',')
            for klasa in klasy:
                uwagi.append([uwaga[0], klasa, uwaga[2], uwaga[3]])

    return uwagi


def uwagi_klasa(data, klasa, uwagi):
    uwagi_klasa = []
    for uwaga in uwagi:
        if uwaga[0] == data and (uwaga[1] == klasa or uwaga[1] == ''):
            if uwaga[2] == '':
                uwaga = ['0', f"{uwaga[3]}"]

            else:
                uwaga = [uwaga[2], f"l.{uwaga[2]} - {uwaga[3]}"]

            uwagi_klasa.append(uwaga)

    return uwagi_klasa


def sprawdz_uwagi(data, klasa):
    uwagi = uwagi_odczyt()
    return uwagi_klasa(data, klasa, uwagi)


def zastepstwa(zast, dzien_tygodnia, uwagi):
    zast_final = []; zast_temp_f = []; uwagi_final = []; uwagi_temp_f = []
    for zastepstwo in zast:
        dzien = zastepstwo[0]
        zastepstwo.remove(zastepstwo[0])
        zastepstwo_dzien = zastepstwo
        if zastepstwo_dzien[0] != 'Brak':
            if len(zastepstwo_dzien[0]) == 2:
                if dzien == num_to_day(dzien_tygodnia):
                    zastepstwo = ['9', f"{zastepstwo_dzien[0][1]}"]
                    uwagi.append(zastepstwo)

            else:
                zastepstwo_zlozone = zastepstwo_dzien[0]
                temp_nr = zastepstwo_dzien[1]
                temp_zastepstwo_s = zastepstwo_dzien[2]
                if zastepstwo_zlozone[1] != '':
                    temp_lekcja = f"{zastepstwo_zlozone[0]} / {zastepstwo_zlozone[1]}"

                else:
                    temp_lekcja = zastepstwo_zlozone[0]

                temp_lekcja = ' '.join(temp_lekcja.split())
                temp_lekcja = re.sub(r'(?<=[a-zA-Z])\.(?=[a-zA-Z])', '. ', temp_lekcja)
                temp_zastepstwo_s = ' '.join(temp_zastepstwo_s.split())
                temp_zastepstwo_s = re.sub(r'(?<=[a-zA-Z])\.(?=[a-zA-Z])', '. ', temp_zastepstwo_s)
                zastepstwo = [temp_nr, f"l.{temp_nr} - {temp_lekcja} - {temp_zastepstwo_s}"]
                if dzien == num_to_day(dzien_tygodnia):
                    zast_temp_f.append(zastepstwo)

        else:
            zastepstwo = 'Brak'

            if dzien == num_to_day(dzien_tygodnia):
                zast_temp_f.append(zastepstwo)

    if len(zast_temp_f) >= 1 and zast_temp_f[0] != "Brak":
        zast_temp = sorted(zast_temp_f, key=lambda x: int(x[0]))
        for x in zast_temp:
            x.remove(x[0])
            zast_final.append(x[0])

    if len(uwagi) >= 1 and uwagi[0] != '':
        uwagi_temp_f = sorted(uwagi, key=lambda x: int(x[0]))
        for x in uwagi_temp_f:
            x.remove(x[0])
            uwagi_final.append(x[0])

    return zast_final, uwagi_final


def zapis_zastepstwa_plik(zastepstwa_wszystkie_klasy):
    with open('zastepstwa.txt', "w", encoding="utf-8") as plik:
        for klasa, tresc in zastepstwa_wszystkie_klasy:
            zastepstwa_koniec = tresc.strip()
            plik.write(f"!{klasa}\n")
            plik.write(zastepstwa_koniec)
            plik.write("\n\n")


def odczyt_zastepstwa_plik():
    odczytane_zastepstwa = {}
    with open('zastepstwa.txt', "r", encoding="utf-8") as plik:
        zawartosc = plik.read()

    sekcje = zawartosc.split("!")
    for sekcja in sekcje:
        if sekcja.strip():
            linie = sekcja.split("\n", 1)
            klasa = linie[0].strip()
            if len(linie) > 1:
                tresc = linie[1].strip()
            else:
                tresc = ""

            odczytane_zastepstwa[klasa] = tresc

    return odczytane_zastepstwa


def odczyt_odbiorcy():
    odbiorcy = []
    with open('odbiorcy.txt', 'r') as plik:
        for linia in plik:
            linia = linia.strip()
            if linia:
                klasa, im_naz = linia.split('_', 1)
                odbiorcy.append([klasa, im_naz])
    return odbiorcy


def zastepstwa_calosc():
    print('Start')
    klasy_kod = {}; schowek = {}
    klasy_lista = []; klasy_lista_final = []; klasy = []; nauczyciele = []; nauczyciele_schowel = [{}, {}, {}]
    przyciski = pobierz_przyciski(); przyciski = zrub_przyciski(przyciski)
    last = 1
    for i, cell in enumerate(przyciski[0]):
        if last < int(cell[0]):
            klasy.append(schowek)
            schowek = {}
            last = int(cell[0])
        schowek[cell] = przyciski[0][cell]

    klasy.append(schowek)
    for klasa in klasy:
        klasy_kod.update(klasa)


    klasy_lista = list(map(list, klasy_kod.items()))
    klasy_lista_final = []; klasy_same = []
    for item in klasy_lista:
        klasy_lista_final.append(f"{item[0]} {item[1]}")
        klasy_same.append(item[0])


    zmiana = False
    odczytane_zastepstwa = odczyt_zastepstwa_plik()
    zastepstwa_wszystkie_klasy = []; zastepstwa_klasa_zmienione = {}; zastepstwa_wszystkie_klasy_d = {}
    data = ''; dzien_tygodnia = None; data_r = ''
    data_check = True
    for klasa in klasy_lista_final:
        klasa_1 = klasa.split(" ")[0]
        zast, wyniki, daty = zast_and_plan(klasa)
        if data_check is True:
            for i, wynik in enumerate(wyniki):
                if wynik.status_code == 200:
                    teraz = datetime.now()
                    data = daty[i]
                    print('Data: ', data)
                    data_r = datetime.strptime(data, '%y%m%d')
                    print(data_r)
                    dzien_tygodnia_temp = data_r.weekday()
                    if dzien_tygodnia_temp == teraz.weekday() or dzien_tygodnia_temp == 0:
                        if teraz.hour >= 8 and teraz.weekday() != 6:
                            data_r += timedelta(days=1)

                        print('Data_r: ', data_r)
                        dzien_tygodnia = data_r.weekday()
                        print('Dzien tygodnia: ', dzien_tygodnia)
                        data = data_r.strftime('%y%m%d')
                        data_r = data_r.strftime('%d-%m-%y')
                        data_check = False
                        break

        if data == '':
            return

        if [num_to_day(dzien_tygodnia), 'XXX'] in zast:
            return

        else:
            for spr in zast[:]:
                if 'XXX' in spr:
                    zast.remove(spr)

        uwagi = sprawdz_uwagi(data, klasa_1)
        zast_final, klasa_uwagi = zastepstwa(zast, dzien_tygodnia, uwagi)

        if not zast_final:
            zast_final = ['Brak']

        zastepstwa_koniec = f'{num_to_day(dzien_tygodnia)} / {data_r} // {klasa_1} \n\nZastępstwa:'

        for informacja in zast_final:
            zastepstwa_koniec += f'\n{informacja}\n'

        if not not klasa_uwagi:
            zastepstwa_koniec += f'\n\nUwaga:'
            for uwaga in klasa_uwagi:
                zastepstwa_koniec += f'\n{uwaga}'

        zastepstwa_koniec_klasa = [klasa_1, zastepstwa_koniec]
        zastepstwa_wszystkie_klasy.append(zastepstwa_koniec_klasa)
        zastepstwa_wszystkie_klasy_d[klasa_1] = zastepstwa_koniec
        if " ".join(zastepstwa_wszystkie_klasy_d[klasa_1].split()) != " ".join(odczytane_zastepstwa[klasa_1].split()):
            zmiana = True
            zastepstwa_klasa_zmienione[klasa_1] = zastepstwa_koniec
        else:
            zastepstwa_klasa_zmienione[klasa_1] = 'Br.Zm'

    if zmiana:
        zapis_zastepstwa_plik(zastepstwa_wszystkie_klasy)

    print('Wiadomosci')
    asyncio.run(wiadomosc(zastepstwa_klasa_zmienione, zastepstwa_wszystkie_klasy_d, klasy_same))


poniedzialek_piatek()
niedziela()

while True:
    schedule.run_pending()
    time.sleep(1)
