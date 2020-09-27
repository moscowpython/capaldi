from telegram import Update, ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters

from learn_python_bot.decorators import for_admins_only
from learn_python_bot.utils.students import get_group_types


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([['Show students', 'Message students', 'Reload students', 'Restart bot']])


@for_admins_only
def admin_keyboard(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello admin', reply_markup=get_admin_keyboard())


@for_admins_only
def admin_show_students(update: Update, context: CallbackContext) -> None:
    course_students: str = ''
    for student in context.dispatcher.bot_data['students']:
        course_students += f'{student.first_name} {student.last_name} {student.telegram_account}\n'

    update.message.reply_text(course_students)


@for_admins_only
def admin_message_students_1(update: Update, context: CallbackContext) -> None:
    group_types = get_group_types(context.dispatcher.bot_data['students'])
    keyboard = ReplyKeyboardMarkup([group_types])
    update.message.reply_text('Выберите тип группы', reply_markup=keyboard)
    return 'message_group_type'


@for_admins_only
def admin_message_students_2(update: Update, context: CallbackContext) -> None:
    group_type = update.message.text
    if group_type not in get_group_types(context.dispatcher.bot_data['students']):
        update.message.reply_text('Выберите тип группы')
    else:
        context.user_data['admin_message'] = {}
        context.user_data['admin_message']['group_type'] = group_type
        if group_type == 'Все студенты':
            students_to_send = context.dispatcher.bot_data['students']
        else:
            students_to_send = [s for s in context.dispatcher.bot_data['students'] if s.group_type == group_type]
        context.user_data['admin_message']['recipients'] = students_to_send
        update.message.reply_text(
            f'Количество адресатов: {len(students_to_send)}, введите текст сообщения',
            reply_markup=ReplyKeyboardRemove(),
        )
        return 'message_text'


@for_admins_only
def admin_message_students_3(update: Update, context: CallbackContext) -> None:
    context.user_data['admin_message']['text'] = update.message.text
    user_text = f"""Проверьте рассылку:
<b>Тип группы:</b> {context.user_data['admin_message']['group_type']}
<b>Кол-во получателей:</b> {len(context.user_data['admin_message']['recipients'])}
<b>Текст:</b> {context.user_data['admin_message']['text']}"""
    keyboard = ReplyKeyboardMarkup([['Разослать', 'Отмена']])
    update.message.reply_text(user_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return 'message_send_or_cancel'


@for_admins_only
def admin_message_students_send(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Рассылка начата', reply_markup=ReplyKeyboardRemove())
    for student in context.user_data['admin_message']['recipients']:
        if student.telegram_chat_id:
            context.bot.send_message(
                chat_id=student.telegram_chat_id,
                text=context.user_data['admin_message']['text'],
            )
    update.message.reply_text('Рассылка завершена', reply_markup=get_admin_keyboard())
    return ConversationHandler.END


@for_admins_only
def admin_message_students_cancel(update: Update, context: CallbackContext) -> None:
    context.user_data['admin_message'] = {}
    update.message.reply_text('Отправка отменена', reply_markup=get_admin_keyboard())
    return ConversationHandler.END


def get_admin_announce_command_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Message students)$'), admin_message_students_1)],

        states={
            'message_group_type': [
                MessageHandler(Filters.text, admin_message_students_2),
            ],
            'message_text': [
                MessageHandler(Filters.text, admin_message_students_3),
            ],
            'message_send_or_cancel': [
                MessageHandler(Filters.regex('^(Разослать)$'), admin_message_students_send),
                MessageHandler(Filters.regex('^(Отмена)$'), admin_message_students_cancel),
            ],
        },
        fallbacks=[MessageHandler(Filters.text, admin_message_students_1)],
    )
