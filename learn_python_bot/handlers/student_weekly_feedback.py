from telegram import Update
from telegram.ext import CallbackContext

from learn_python_bot.utils.students import get_student_by_tg_nickname


def process_feedback(update: Update, context: CallbackContext) -> None:
    answers_map = {'yay': True, 'fuu': False}
    student = get_student_by_tg_nickname(
        update._effective_chat.username,
        context.bot_data['students'],
    )
    if student is None:
        update.message.reply_text(
            f'Кажется, ты не учишься на текущем наборе. Если это не так, то покажите '
            f'это сообщение кому-нибудь из администрации ({update._effective_chat.username})',
        )
        return None
    raw_response_text = update.callback_query.data
    week_num_str, raw_answer = raw_response_text.lstrip('w').split('_')
    week_num = int(week_num_str)
    if context.bot_data['airtable_api'].student_has_feedback_for_week(
        week_num,
        student.airtable_pk,
    ):
        response_text = f'Кажется, у нас уже есть твой фидбек за неделю {week_num}'
    else:
        context.bot_data['airtable_api'].save_feedback(
            student.airtable_id,
            week_num,
            answers_map[raw_answer],
        )
        answer_text = 'понравилась' if answers_map[raw_answer] else 'не понравилась'
        response_text = f'Записал, что тебе {answer_text} неделя {week_num}. Спасибо за честность.'
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=response_text)
