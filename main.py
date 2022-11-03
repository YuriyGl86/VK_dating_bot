from bot.bot import Bot
from bot.bot_token import key
import configparser
# from DB.db import rec_favorites, rec_blocked, rec_vk_user

config = configparser.ConfigParser()
config.read('token_new.ini')
KEY = config['VK_API']['key_oauth']

def main():
    bot = Bot(KEY)  # Создаем объект класса Bot через который и будем управлять ботом
    candidate = None  # Переменная, хранящая id предложенного кандидата

    for event in bot.longpoll.listen():  # Запускаем бесконечный цикл, начинаем слушать сервер ВК
        if event.type == bot.VkEventType.MESSAGE_NEW and event.to_me and event.text:  # И если тип события это новое сообщение и оно для меня и в нем есть текст
            received_message = event.text.lower()  # Сохраняем полученное сообщение
            sender = event.user_id  # Получаем ID пользователя, с которым общаемся

            user = bot.get_user_info(sender)  # Получаем информацию о пользователе в виде json, который отправим в БД
            print(user)
            user_name = user['first_name']
            # rec_vk_user(user) здесь будет вызов функции от Артёма для записи юзера в БД

            if received_message in ('привет', 'начать'):
                bot.write_message(sender,
                                  f'Привет, {user_name}, я умный бот. Я могу найти для вас отличного кандидата '
                                  f'для знакомства. Воспользуйтесь одной из моих функций. Для этого '
                                  f'введите команду сами или нажмите на соответствующую кнопку. Я понимаю следующие '
                                  f'команды: \n"Предложить кандидата"\n"В избранное"\n"В черный список"\n'
                                  f'"Список избранных"')

            elif received_message == 'в избранное':
                if candidate:
                    #rec_favorites(sender, candidate) здесь будет вызов функции от Артёма для записи candidate в Избранное
                    bot.write_message(sender, 'Предложенный кандидат добавлен в избранное')
                    candidate = None
                else:
                    bot.write_message(sender, 'Сначала выберите кандидата, кого добавлять в избранное')

            elif received_message == 'предложить кандидата':
                candidate = bot.send_candidate(user)


            elif received_message == 'список избранных':
                bot.write_message(sender, 'Ваш список избранных:')
                bot.send_favorites_list(sender)

            elif received_message == 'в черный список':
                if candidate:
                    # rec_blocked(sender, candidate) здесь будет вызов функции от Артёма для записи candidate в ЧС
                    bot.write_message(sender, 'Предложенный кандидат добавлен в черный список')
                    candidate = None
                else:
                    bot.write_message(sender, 'Сначала выберите кандидата, кого добавлять в черный список')

            else:
                message = 'Ничего не понятно, но очень интересно!\nЛучше воспользуйтесь одной из моих возможностей'
                bot.write_message(sender, message=message)


if __name__ == '__main__':
    main()
