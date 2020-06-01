from typing import Any, Callable

import wrapt

from learn_python_bot.typical_responses import not_a_student
from learn_python_bot.utils.students import get_student_by_tg_nickname


@wrapt.decorator
def for_students_only(wrapped: Callable, instance: Any, args: Any, kwargs: Any) -> Any:
    update, context = args[:2]
    student = get_student_by_tg_nickname(
        update._effective_chat.username,
        context.bot_data['students'],
    )
    if student is None:
        update.message.reply_text(not_a_student(update))
        return None
    kwargs['student'] = student
    return wrapped(*args, **kwargs)
