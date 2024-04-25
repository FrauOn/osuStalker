import csv
import time
from ossapi import Ossapi


def get_players_ids(match_id):
    try:
        # Получение объекта MatchResponse для указанного match_id
        match_response = api.match(match_id)
    except Exception as e:
        if "Permission denied" in str(e):
            print("Произошла ошибка доступа при получении информации о матче:", e)
            return [0]
        else:
            print("Произошла ошибка при получении информации о матче:", e)
            return []

    # Проверка наличия объекта MatchResponse
    if match_response is None:
        print("Ошибка: Невозможно получить информацию о матче.")
        return []

    # Проверка, что список пользователей не пустой
    if not match_response.users:
        print("Пустой список игроков для матча с ID", match_id)
    else:
        # Инициализация списка для хранения id игроков
        players_ids = []

        # Извлечение id каждого игрока из списка пользователей
        for user in match_response.users:
            players_ids.append(str(user.id))

        # Вывод списка id игроков
        print("Список id игроков в матче с ID", match_id, ":", players_ids)
        return players_ids

    return match_response.users



if __name__ == "__main__":
    # Чтение настроек из файла settings.txt
    with open('settings.txt', 'r') as settings_file:
        settings = settings_file.readlines()

    # Парсинг настроек
    for setting in settings:
        key, value = setting.strip().split(': ')
        if key == 'client_id':
            client_id = value
        elif key == 'client_secret':
            client_secret = value
        elif key == 'last_id':
            last_id = int(value)  # Преобразуем last_id в целое число

    # Создание объекта Ossapi с указанием клиентских данных
    api = Ossapi(client_id, client_secret)


    # Чтение id игроков из файла players.csv
    with open('players.csv', 'r') as players_file:
        reader = csv.reader(players_file, delimiter=';')
        players_idsM = [id.strip() for row in reader for id in row]

    # Счетчик попыток получения списка игроков
    retry_count = 0

    while True:
        players_ids = get_players_ids(last_id)

        # Если список игроков пустой
        if not players_ids:
            # Увеличиваем счетчик попыток
            retry_count += 1

            # Если было 5 неудачных попыток, пропускаем текущий ID и увеличиваем last_id на 1
            if retry_count >= 5:
                last_id += 1
                retry_count = 0
            else:
                # Ждем одну минуту перед следующей попыткой
                time.sleep(60)
        else:
            with open("output.txt", "a") as output_file:
                if any(player_id in players_ids for player_id in players_idsM):
                    output_file.write(
                        f"Хотя бы один из игроков {', '.join(players_ids)} найден в матче с ID {last_id}\n")
                    print("SUS", last_id)
            # Увеличиваем last_id на 1
            last_id += 1
            retry_count = 0
            # Ждем секунду перед следующей попыткой
