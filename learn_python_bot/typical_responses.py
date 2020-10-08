from telegram import Update


def not_a_student(update: Update) -> str:
    return (
        f'Кажется, ты не учишься на текущем наборе. Если это не так, то покажите '
        f'это сообщение кому-нибудь из администрации ({update.effective_chat.username})'
    )
