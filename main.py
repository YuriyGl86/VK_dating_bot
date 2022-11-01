from bot.bot import Bot
from bot.bot_token import key


def main():
    bot = Bot(key)  # Создаем объект класса Bot через который и будем управлять ботом
    candidate = None  # Переменная, хранящая id предложенного кандидата

    for event in bot.longpoll.listen():  # Запускаем бесконечный цикл, начинаем слушать сервер ВК
        if event.type == bot.VkEventType.MESSAGE_NEW and event.to_me and event.text:  # И если тип события это новое сообщение и оно для меня и в нем есть текст
            received_message = event.text.lower()  # Сохраняем полученное сообщение
            sender = event.user_id  # Получаем ID пользователя, с которым общаемся

            user = bot.get_user_info(sender)  # Получаем информацию о пользователе в виде json, который отправим в БД
            print(user)
            user_name = user['first_name']
            # здесь будет вызов функции от Артёма для записи юзера в БД

            if received_message in ('привет', 'начать'):
                bot.write_message(sender,
                                  f'Добрый день, {user_name}, я умный бот. Воспользуйтесь одной из моих функций')

            elif received_message == 'в избранное':
                if candidate:
                    # здесь будет вызов функции от Артёма для записи candidate в Избранное
                    bot.write_message(sender, 'Вызываем функцию добавления в избранное')
                    candidate = None
                else:
                    bot.write_message(sender, 'Сначала выберите кандидата, кого добавлять в избранное')

            elif received_message == 'предложить кандидата':
                candidate = bot.send_candidate(user)

            elif received_message == 'список избранных':
                bot.write_message(sender, 'Вызываем функцию вывода списка избранных')
                bot.send_favorites_list(sender)

            elif received_message == 'в черный список':
                if candidate:
                    # здесь будет вызов функции от Артёма для записи candidate в ЧС
                    bot.write_message(sender, 'Вызываем функцию добавления в ЧС')
                    candidate = None
                else:
                    bot.write_message(sender, 'Сначала выберите кандидата, кого добавлять в черный список')

            else:
                message = 'Ничего не понятно, но очень интересно!\nЛучше воспользуйтесь одной из моих возможностей'
                bot.write_message(sender, message=message)


if __name__ == '__main__':
    main()
