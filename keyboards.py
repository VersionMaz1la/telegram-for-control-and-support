from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def work_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Сколько осталось времени?",
                    callback_data="remaining_time"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☕ Перерыв 15 минут",
                    callback_data="short_break"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛑 Завершить день",
                    callback_data="end_day"
                )
            ]
        ]
    )

def work_keyboard_with_big_break():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Сколько осталось времени?",
                    callback_data="remaining_time"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☕ Перерыв 15 минут",
                    callback_data="short_break"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🥗 Начать большой перерыв",
                    callback_data="start_big_break_early"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛑 Завершить день",
                    callback_data="end_day"
                )
            ]
        ]
    )

def start_day_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌅 Начать день",
                    callback_data="start_day"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😴 Сегодня пауза",
                    callback_data="day_pause"
                )
            ]
        ]
    )


def skip_prep_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Сколько осталось времени?",
                    callback_data="remaining_time"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⏭ Закончить подготовку раньше",
                    callback_data="skip_prep"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛑 Завершить день",
                    callback_data="end_day"
                )
            ]
        ]
    )


def yes_no_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data="yes"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="no"
                )
            ]
        ]
    )

def no_reason_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔋 Устал",
                    callback_data="reason_tired"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Отвлекался",
                    callback_data="reason_distracted"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✍ Другое",
                    callback_data="reason_other"
                )
            ]
        ]
    )


def continue_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="▶ Продолжаем",
                    callback_data="continue"
                )
            ]
        ]
    )

def remaining_time_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Сколько осталось времени?",
                    callback_data="remaining_time"
                )
            ]
        ]
    )

def end_day_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛑 Завершить день",
                    callback_data="end_day"
                )
            ]
        ]
    )

def confirm_end_day_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, завершить день",
                    callback_data="confirm_end_day"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет, продолжаем",
                    callback_data="cancel_end_day"
                )
            ]
        ]
    )

def short_break_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="☕ Перерыв 15 минут",
                    callback_data="short_break"
                )
            ]
        ]
    )

def skip_break_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏭ Закончить перерыв раньше",
                    callback_data="skip_break"
                )
            ]
        ]
    )

def start_big_break_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="☕ Начать большой перерыв",
                    callback_data="start_big_break_early"
                )
            ]
        ]
    )

def skip_short_break_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏭ Закончить короткий перерыв раньше",
                    callback_data="skip_short_break"
                )
            ]
        ]
    )

def day_pause_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data="confirm_day_pause"
                ),
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="cancel_day_pause"
                )
            ]
        ]
    )

def skip_catchup_rest_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏭ Закончить отдых раньше",
                    callback_data="skip_catchup_rest"
                )
            ]
        ]
    )

def confirm_big_break_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data="confirm_big_break"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data="cancel_big_break"
                )
            ]
        ]
    )