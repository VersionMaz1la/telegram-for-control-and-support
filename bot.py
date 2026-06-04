import asyncio
import os
import random

from dotenv import load_dotenv
from stages import *
from config import *
from texts import *
from keyboards import *
from callbacks import *

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
THREAD_ID = int(os.getenv("THREAD_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

def format_minutes(seconds):

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours} ч {minutes} мин"

    if minutes > 0:
        return f"{minutes} мин"

    return f"{seconds} сек"

async def timer_sleep():

    global day_pause
    global day_ended

    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return False

    await asyncio.sleep(1)

    if day_ended:
        return False

    return True

async def remove_keyboard(message):

    try:
        await message.edit_reply_markup(
            reply_markup=None
        )
    except:
        pass

# состояние

prep_skipped = False

current_stage = None
current_block = 4

break_taken = False

remaining_work_time = 0
remaining_prep_time = 0
prep_message = None
remaining_break_time = 0
remaining_catchup_time = 0

break_skipped = False

short_break_skipped = False

short_break_used = False

short_break_return_stage = None

end_day_return_stage = None

waiting_for_custom_reason = False

custom_reason_stage = None

catchup_time = 0
catchup_duration = 0

catchup_rest_skipped = False

day_ended = False

day_pause = False

async def preparation_flow():

    global prep_skipped

    global day_ended

    global remaining_prep_time

    remaining_prep_time = PREP_END

    warning_sent = False

    while remaining_prep_time > 0:

        if day_ended:
            return

        if prep_skipped:
            return

        if not await timer_sleep():
            return

        remaining_prep_time -= 1

        if (
                not warning_sent
                and remaining_prep_time <=
                (PREP_END - PREP_WARNING)
        ):
            warning_sent = True

            await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=THREAD_ID,
                text=PREPARATION_WARNING_TEXT
            )

    await remove_keyboard(
        prep_message
    )
    await start_work_block()


async def start_work_block():
    global break_taken
    global short_break_used
    global current_stage

    break_taken = False
    short_break_used = False


    current_stage = STAGE_WORK_FIRST_HALF

    block_duration = LONG_WORK_BLOCK if current_block <= 2 else SHORT_WORK_BLOCK

    if current_block == 1:

        block_text = WORK_BLOCK_1_TEXT

    elif current_block in (2, 3):

        block_text = WORK_BLOCK_2_3_TEXT

    else:

        block_text = WORK_BLOCK_4_TEXT

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            f"Ты уже должен заниматься.\n\n"
            f"Начинается рабочий блок №{current_block}.\n\n"
            f"Длительность блока: "
            f"{format_minutes(block_duration)}.\n\n"
            f"{block_text}"
        )
    )

    action_message = await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text="Доступные действия:",
        reply_markup=(
            work_keyboard_with_big_break()
            if current_block < 4
            else work_keyboard()
        )
    )
    global remaining_work_time

    remaining = LONG_WORK_BLOCK if current_block <= 2 else SHORT_WORK_BLOCK

    remaining_work_time = remaining
    step = 1  # шаг 1 секунда для теста

    while remaining > 0:

        if day_ended:
            return

        while day_pause:
            await asyncio.sleep(1)

        if break_taken:
            break

        await asyncio.sleep(step)

        remaining -= step
        remaining_work_time = remaining

    if break_taken:
        return

    await remove_keyboard(
        action_message
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=SELF_CONTROL_QUESTION,
        reply_markup=yes_no_keyboard()
    )

async def resume_work_block():

    global remaining_work_time
    global break_taken
    global current_stage
    global short_break_return_stage
    global catchup_duration

    break_taken = False

    if short_break_return_stage == STAGE_CATCHUP:

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="Возвращаемся к дополнительному блоку."
        )

        current_stage = STAGE_CATCHUP_SECOND_HALF

        asyncio.create_task(
            catchup_second_half()
        )

        return

    elif short_break_return_stage == STAGE_CATCHUP_SECOND_HALF:

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="Возвращаемся к дополнительному блоку."
        )

        current_stage = STAGE_CATCHUP_FINISH

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=(
                "Финальный вопрос.\n\n"
                "Удалось ли тебе наверстать недостающее время?\n\n"
                "Можешь ли ты честно сказать, что сегодня сделал всё возможное?"
            ),
            reply_markup=yes_no_keyboard()
        )

        return

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            f"Возвращаемся к работе.\n\n"
            f"Осталось работать: "
            f"{format_minutes(remaining_work_time)}."
        )
    )

    while remaining_work_time > 0:

        if not await timer_sleep():
            return

        remaining_work_time -= 1

    if short_break_return_stage == STAGE_WORK_FIRST_HALF:

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=SELF_CONTROL_QUESTION,
            reply_markup=yes_no_keyboard()
        )

    elif short_break_return_stage == STAGE_WORK_SECOND_HALF:

        if current_block == 4:

            await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=THREAD_ID,
                text=(
                    "Сколько часов ты сегодня занимался?\n\n"
                    "Формат:\n"
                    "07:00\n"
                    "05:30"
                )
            )

            current_stage = STAGE_FINISHED

        else:

            await start_big_break()

async def second_half_work_block():

    global short_break_used

    short_break_used = False

    block_duration = LONG_WORK_BLOCK if current_block <= 2 else SHORT_WORK_BLOCK

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            f"Начинается вторая половина рабочего блока №{current_block}.\n\n"
            f"Осталось работать: "
            f"{format_minutes(block_duration)}.\n\n"
            f"{SECOND_HALF_WORK_TEXT}"
        )
    )

    action_message = await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text="Доступные действия:",
        reply_markup=(
            work_keyboard_with_big_break()
            if current_block < 4
            else work_keyboard()
        )
    )

    global break_taken
    global remaining_work_time

    break_taken = False

    remaining = LONG_WORK_BLOCK if current_block <= 2 else SHORT_WORK_BLOCK

    remaining_work_time = remaining

    while remaining > 0:

        if break_taken:
            break

        if not await timer_sleep():
            return

        remaining -= 1
        remaining_work_time = remaining

    if break_taken:
        return

    if current_block == 4:

        await remove_keyboard(
            action_message
        )

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=(
                "Сколько часов ты сегодня занимался?\n\n"
                "Формат:\n"
                "07:00\n"
                "05:30"
            )
        )

        global current_stage
        current_stage = STAGE_FINISHED

    else:

        await start_big_break()

async def start_big_break():

    global current_stage
    global break_skipped

    break_skipped = False

    global remaining_break_time

    current_stage = STAGE_BIG_BREAK

    remaining_break_time = BREAK_END

    warning_message = None

    break_message = await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            f"Начинается большой перерыв.\n\n"
            f"Длительность перерыва: "
            f"{format_minutes(BREAK_END)}.\n\n"
            f"Ты хорошо поработал.\n\n"
            f"Сейчас самое время немного отдохнуть, восстановить силы и переключиться.\n\n"
            f"Постарайся вернуться к следующему этапу бодрым и готовым к работе."
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏳ Сколько осталось времени?",
                        callback_data="remaining_time"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⏭ Закончить перерыв раньше",
                        callback_data="skip_break"
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
    )

    warning_sent = False

    while remaining_break_time > 0:

        if break_skipped:
            return

        if not await timer_sleep():
            return

        remaining_break_time -= 1

        if (
                not warning_sent
                and remaining_break_time <=
                (BREAK_END - BREAK_WARNING)
        ):

            warning_sent = True

            await remove_keyboard(
                break_message
            )

            warning_message = await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=THREAD_ID,
                text=BIG_BREAK_WARNING_TEXT,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⏭ Закончить перерыв раньше",
                                callback_data="skip_break"
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
            )

    if warning_message:
        await remove_keyboard(
            warning_message
        )

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=BIG_BREAK_FINISHED_TEXT,
        reply_markup=continue_keyboard()
    )

@dp.callback_query(F.data == "start_day")
async def start_day(callback: CallbackQuery):

    global prep_skipped

    prep_skipped = False

    global day_ended

    day_ended = False

    global current_stage

    current_stage = STAGE_PREPARATION

    global prep_message

    await callback.message.edit_text(
        "Доброе утро!\n\n"
        "Пора начинать день."
    )

    prep_message = await callback.message.answer(
        (
            f"Сейчас я выделяю тебе время на подготовку к предстоящему дню.\n\n"
            f"На подготовку выделено: {format_minutes(PREP_END)}.\n\n"
            f"Возможно, некоторые задачи сегодня будут казаться сложными или неприятными, но ты ещё не представляешь, насколько приятно будет видеть результат своих усилий спустя время.\n\n"
            f"Поэтому просыпайся, умывайся, делай зарядку, пей воду, завтракай и готовься к отличному и продуктивному дню."
        ),
        reply_markup=InlineKeyboardMarkup(
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
    )

    asyncio.create_task(preparation_flow())

    await callback.answer()


@dp.callback_query(F.data == "skip_prep")
async def skip_prep(callback: CallbackQuery):

    global prep_skipped
    prep_skipped = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        PREP_SKIP_TEXT
    )

    await start_work_block()

    await callback.answer()


@dp.callback_query(F.data == "yes")
async def answer_yes(callback: CallbackQuery):

    global current_stage
    global current_block

    if current_stage == STAGE_CATCHUP:

        await callback.message.edit_text(
            "Выбрано: ✅ Да"
        )

        await callback.message.answer(
            random.choice(MOTIVATION_MESSAGES)
        )

        current_stage = STAGE_CATCHUP_SECOND_HALF

        asyncio.create_task(
            catchup_second_half()
        )

        await callback.answer()
        return

    if current_stage == STAGE_CATCHUP_FINISH:
        current_stage = None
        current_block = 1

        await callback.message.edit_text(
            "Выбрано: ✅ Да"
        )

        await callback.message.answer(
            "Хорош, чел.\n\n"

            "Сегодня ты действительно постарался.\n"

            "Ты сделал всё, что было необходимо, и можешь быть доволен собой.\n\n"

            "Теперь тебя ждёт заслуженный отдых.\n"

            "Помни: всё, что делает нас сильнее через трудности, остаётся с нами навсегда.\n\n"

            "Этот день завершён.\n\n"

            "Спокойной ночи. Хорошо выспись и наберись сил перед новым днём."
        )
        await callback.message.answer(
            "🕵️ Система находится в режиме ожидания.\n\n"
            "Ждём вашего пробуждения и кодового слова для начала дня."
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "Выбрано: ✅ Да"
    )

    await callback.message.answer(
        random.choice(MOTIVATION_MESSAGES),
        reply_markup=continue_keyboard()
    )

    current_stage = STAGE_WORK_SECOND_HALF

    await callback.answer()


@dp.callback_query(F.data == "no")
async def answer_no(callback: CallbackQuery):

    global current_stage
    global current_block

    if current_stage == STAGE_CATCHUP:

        await callback.message.edit_text(
            "Выбрано: ❌ Нет"
        )

        await callback.message.answer(
            "Подумай, из-за чего это произошло.",
            reply_markup=no_reason_keyboard()
        )

        await callback.answer()
        return

    if current_stage == STAGE_CATCHUP_FINISH:
        current_stage = None
        current_block = 1
        await callback.message.edit_text(
            "Выбрано: ❌ Нет"
        )

        await callback.message.answer(
            "Сегодня времени уже не осталось.\n\n"
            "Отдохни и восстановись.\n\n"
            "Завтра нужно выложиться сильнее."
        )

        await callback.message.answer(
            "🕵️ Система находится в режиме ожидания.\n\n"
            "Ждём вашего пробуждения и кодового слова для начала дня."
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "Выбрано: ❌ Нет"
    )

    await callback.message.answer(
        "Из-за чего это произошло?",
        reply_markup=no_reason_keyboard()
    )

    current_stage = STAGE_WORK_SECOND_HALF

    await callback.answer()

@dp.callback_query(F.data == "skip_break")
async def skip_break(callback: CallbackQuery):

    global break_skipped

    break_skipped = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        BIG_BREAK_SKIP_TEXT,
        reply_markup=continue_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "short_break")
async def short_break_handler(callback: CallbackQuery):
    global break_taken
    global current_stage
    global short_break_skipped
    global short_break_used
    global short_break_return_stage

    if current_stage not in (
            STAGE_WORK_FIRST_HALF,
            STAGE_WORK_SECOND_HALF,
            STAGE_CATCHUP,
            STAGE_CATCHUP_SECOND_HALF
    ):
        await callback.answer(
            "Сейчас нельзя взять короткий перерыв.",
            show_alert=True
        )

        return

    short_break_return_stage = current_stage

    if short_break_used:
        await callback.answer(
            "Перерыв уже был использован.",
            show_alert=True
        )

        return

    short_break_used = True

    short_break_skipped = False

    current_stage = STAGE_SHORT_BREAK
    break_taken = True

    await callback.message.edit_reply_markup(reply_markup=None)
    short_break_message = await callback.message.answer(
        "Начался короткий перерыв на 15 минут.",
        reply_markup=skip_short_break_keyboard()
    )

    await asyncio.sleep(SHORT_BREAK_WARNING_TIME)  # предупреждение за 5 секунд

    if short_break_skipped:
        return

    await remove_keyboard(
        short_break_message
    )

    await callback.message.answer("Короткий перерыв подходит к концу.")
    await asyncio.sleep(SHORT_BREAK_END_TIME)

    if short_break_skipped:
        return

    await callback.message.answer(SHORT_BREAK_END_TEXT, reply_markup=continue_keyboard())

@dp.callback_query(F.data == "skip_short_break")
async def skip_short_break(callback: CallbackQuery):

    global short_break_skipped

    short_break_skipped = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        SHORT_BREAK_SKIP_TEXT,
        reply_markup=continue_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "end_day")
async def end_day_handler(callback: CallbackQuery):

    global current_stage
    global end_day_return_stage
    global day_pause

    end_day_return_stage = current_stage

    current_stage = STAGE_CONFIRM_END_DAY

    day_pause = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Ты уверен, что хочешь завершить сегодняшний день?\n\n"
        "На это есть действительно веская причина?\n\n"
        "Помни:\n"
        "каждый пропущенный день отдаляет тебя от цели.",
        reply_markup=confirm_end_day_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "confirm_end_day")
async def confirm_end_day(callback: CallbackQuery):

    global current_stage
    global current_block

    global day_ended
    global day_pause

    day_ended = True
    day_pause = False

    current_stage = None
    current_block = 1

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        CONFIRM_END_DAY_TEXT
    )

    await callback.message.answer(
        "🕵️ Система находится в режиме ожидания.\n\n"
        "Ждём вашего пробуждения и кодового слова для начала дня."
    )

    await callback.answer()

@dp.callback_query(F.data == "cancel_end_day")
async def cancel_end_day(callback: CallbackQuery):

    global current_stage
    global end_day_return_stage
    global day_pause

    current_stage = end_day_return_stage

    day_pause = False

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        CANCEL_END_DAY_TEXT
    )

    await callback.answer()

@dp.callback_query(F.data == "reason_tired")
async def reason_tired(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Выбрана причина: Устал\n\n"
        "Подумай, из-за чего это произошло и запиши это в дневник.",
        reply_markup=continue_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "reason_distracted")
async def reason_distracted(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Выбрана причина: Отвлекался\n\n"
        "Подумай, из-за чего это произошло и запиши это в дневник.",
        reply_markup=continue_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "reason_other")
async def reason_other(callback: CallbackQuery):

    global waiting_for_custom_reason
    global custom_reason_stage
    global current_stage

    waiting_for_custom_reason = True

    custom_reason_stage = current_stage

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Напиши, из-за чего это произошло."
    )

    await callback.answer()

@dp.callback_query(F.data == "continue")
async def continue_handler(callback: CallbackQuery):

    global current_stage
    global current_block
    global remaining_work_time

    await callback.message.edit_reply_markup(reply_markup=None)

    # Если сейчас короткий перерыв, возвращаемся в рабочий блок
    if current_stage == STAGE_SHORT_BREAK:

        current_stage = STAGE_WORK_SECOND_HALF if current_stage == STAGE_SHORT_BREAK else current_stage

        await resume_work_block()
        await callback.answer()
        return

    # Если мы в конце второй половины блока — запускаем start_big_break() или вопрос после блока 4
    if current_stage == STAGE_WORK_SECOND_HALF:

        await callback.message.answer(
            (
                f"Отлично.\n\n"
                f"Продолжаем рабочий блок №{current_block}.\n\n"
                f"Не сбавляй темп.\n\n"
                f"Ты уже движешься вперёд и становишься лучше, чем был вчера."
            )
        )

        asyncio.create_task(
            second_half_work_block()
        )
        await callback.answer()
        return

    if current_stage == STAGE_CATCHUP:

        asyncio.create_task(
            catchup_second_half()
        )

        await callback.answer()
        return

    # Если мы в большом перерыве
    if current_stage == STAGE_BIG_BREAK:

        current_block += 1

        if current_block <= 4:

            await callback.message.answer(
                f"Начинается блок №{current_block}"
            )

            asyncio.create_task(
                start_work_block()
            )

        else:

            await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=THREAD_ID,
                text=(
                    "Сколько часов ты сегодня занимался?\n\n"
                    "Формат:\n"
                    "07:00\n"
                    "05:30"
                )
            )

            current_stage = STAGE_FINISHED

    await callback.answer()

@dp.callback_query(F.data == "day_pause")
async def day_pause_handler(callback: CallbackQuery):

    await callback.message.answer(
        "Ты уверен?\n\n"
        "Как ты думаешь, заслужил ли ты сегодня паузу?\n\n"
        "Ответь честно.",
        reply_markup=day_pause_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "confirm_day_pause")
async def confirm_day_pause(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Хорошо.\n\n"
        "Используй этот день с пользой.\n\n"
        "Не превращай отдых в бесконечную прокрастинацию."
    )

    await callback.answer()

@dp.callback_query(F.data == "cancel_day_pause")
async def cancel_day_pause(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Тогда начинаем работать.",
        reply_markup=start_day_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "start_big_break_early")
async def start_big_break_early(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Ты уверен, что хочешь завершить текущий рабочий блок и перейти к большому перерыву?",
        reply_markup=confirm_big_break_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "confirm_big_break")
async def confirm_big_break(callback: CallbackQuery):

    global break_taken

    break_taken = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Рабочий блок завершён досрочно.\n\n"
        "Начинаем большой перерыв."
    )

    asyncio.create_task(
        start_big_break()
    )

    await callback.answer()

@dp.callback_query(F.data == "cancel_big_break")
async def cancel_big_break(callback: CallbackQuery):

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Продолжаем работу.",
        reply_markup=(
            work_keyboard_with_big_break()
            if current_block < 4
            else work_keyboard()
        )
    )

    await callback.answer()

@dp.callback_query(F.data == "skip_catchup_rest")
async def skip_catchup_rest(callback: CallbackQuery):

    global catchup_rest_skipped

    catchup_rest_skipped = True

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "Отдых завершён досрочно."
    )

    await callback.answer()

@dp.callback_query(F.data == "remaining_time")
async def remaining_time(callback: CallbackQuery):

    global current_stage

    global remaining_work_time
    global remaining_break_time
    global remaining_prep_time
    global remaining_catchup_time

    if current_stage in (
            STAGE_WORK_FIRST_HALF,
            STAGE_WORK_SECOND_HALF
    ):

        await callback.answer(
            f"До конца рабочего блока осталось:\n"
            f"{format_minutes(remaining_work_time)}",
            show_alert=True
        )

        return

    if current_stage == STAGE_BIG_BREAK:

        await callback.answer(
            f"До конца большого перерыва осталось:\n"
            f"{format_minutes(remaining_break_time)}",
            show_alert=True
        )

        return

    if current_stage == STAGE_PREPARATION:

        await callback.answer(
            f"До конца подготовки осталось:\n"
            f"{format_minutes(remaining_prep_time)}",
            show_alert=True
        )

        return

    if current_stage in (
            STAGE_CATCHUP,
            STAGE_CATCHUP_SECOND_HALF
    ):

        await callback.answer(
            f"До конца дополнительного блока осталось:\n"
            f"{format_minutes(remaining_catchup_time)}",
            show_alert=True
        )

        return

    await callback.answer(
        "Сейчас нет активного таймера.",
        show_alert=True
    )

@dp.message()
async def process_custom_reason(message: Message):
    print("MESSAGE RECEIVED:", message.text)
    if (
            current_stage is None
            and message.text
    ):

        if message.text and message.text.strip().lower() in (
                "я готов",
                "я готов!"
        ):

            global day_ended
            global current_block

            day_ended = False

            current_block = (
                TEST_START_BLOCK
                if TEST_MODE
                else REAL_START_BLOCK
            )

            await message.answer(
                (
                    "Привет, будущий ML-инженер.\n\n"
                    "Сейчас начинается твой день. Надеюсь, ты хорошо выспался и готов к продуктивной работе.\n\n"
                    "Сегодня тебя ждёт много задач, но помни: каждая минута вложенного времени приближает тебя к той жизни, которую ты хочешь построить для себя и своих близких.\n\n"
                    "Настраивайся на качественную работу, не бойся трудностей и двигайся вперёд. Всё получится."
                ),
                reply_markup=start_day_keyboard()
            )

        else:

            await message.answer(
                "Неверное кодовое слово."
            )

        return

    print("PROCESS_CUSTOM_REASON")

    global waiting_for_custom_reason
    global custom_reason_stage

    if not waiting_for_custom_reason:
        await process_study_time(message)
        return

    waiting_for_custom_reason = False

    await message.answer(
        f"Выбрана причина:\n\n"
        f"{message.text}\n\n"
        f"Подумай, из-за чего это произошло и запиши это в дневник.",
        reply_markup=continue_keyboard()
    )
    return

@dp.message()
async def process_study_time(message: Message):

    print("PROCESS_STUDY_TIME")

    global current_stage

    if current_stage != STAGE_FINISHED:
        return

    try:

        text = message.text.strip()

        parts = text.split(":")

        if len(parts) != 2:
            raise ValueError

        hours_part, minutes_part = parts

        if len(hours_part) != 2:
            raise ValueError

        if len(minutes_part) != 2:
            raise ValueError

        hours = int(hours_part)
        minutes = int(minutes_part)

        if hours < 0 or hours > 12:
            raise ValueError

        if minutes < 0 or minutes > 59:
            raise ValueError

    except:

        await message.answer(
            "Неверный формат времени.\n\n"
            "Используй формат:\n"
            "07:00\n"
            "05:30\n\n"
            "Максимум: 12:00"
        )

        return
    total_minutes = hours * 60 + minutes

    target_minutes = TARGET_STUDY_HOURS * 60

    if total_minutes >= target_minutes:

        current_stage = None
        current_block = 1

        await message.answer(
            "Ты большой молодец.\n\n"
            "Теперь отдохни.\n\n"
            "Загляни в дневник и запиши свои мысли.",
            reply_markup=skip_catchup_rest_keyboard()
        )

        await callback.message.answer(
            "🕵️ Система находится в режиме ожидания.\n\n"
            "Ждём вашего пробуждения и кодового слова для начала дня."
        )
    else:

        remaining_minutes = target_minutes - total_minutes

        global catchup_time

        global catchup_time
        global catchup_duration

        catchup_time = remaining_minutes

        catchup_duration = int(
            remaining_minutes * 1.5
        )

        remaining_hours = remaining_minutes // 60

        remaining_mins = remaining_minutes % 60

        # Задаём тестовое время отдыха (для проверки MVP)

        rest_seconds = CATCHUP_REST_TIME  # тут можно поставить любое количество секунд

        rest_message = await message.answer(

            "Привет. Тебя тоже оставляли после уроков?\n\n"

            "Не переживай.\n\n"

            f"До выполнения сегодняшнего плана осталось:\n"
            f"{remaining_hours:02}:{remaining_mins:02}\n\n"

            f"На навёрстывание потребуется:\n"
            f"{format_minutes(catchup_duration)}\n\n"

            "Сейчас я выделяю тебе время на отдых перед следующим этапом.",

            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⏳ Сколько осталось до следующего блока?",
                            callback_data="remaining_time"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⏭ Закончить отдых раньше",
                            callback_data="skip_catchup_rest"
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
        )

        # Через rest_seconds выдаём сообщение, что пора наверстывать

        asyncio.create_task(
            catchup_break(
                rest_seconds,
                rest_message
            )
        )


async def catchup_break(
        rest_seconds,
        rest_message
):
    global catchup_rest_skipped
    global remaining_catchup_time

    catchup_rest_skipped = False

    global catchup_time

    global day_ended

    global day_pause

    if day_ended:
        return

    remaining = rest_seconds

    while remaining > 1:

        if catchup_rest_skipped:
            break

        await asyncio.sleep(1)

        remaining -= 1

    if catchup_rest_skipped:

        await remove_keyboard(
            rest_message
        )

    else:

        await remove_keyboard(
            rest_message
        )

        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="Отдых подходит к концу. Пора возвращаться к работе."
        )

        await asyncio.sleep(1)


    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return

    await asyncio.sleep(1)

    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return

    if day_ended:
        return

    # остаток времени * 1.5

    action_message = await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
                "Пора наверстывать.\n\n"
                "Сегодня ты ещё не выполнил запланированный объём работы.\n\n"
                "Но это не проблема, потому что сейчас у тебя есть возможность исправить ситуацию.\n\n"
                "Начинается дополнительный блок (1/2).\n\n"
                f"Длительность этапа: "
                f"{format_minutes(catchup_duration // 2)}."
        ),
        reply_markup=work_keyboard()
    )

    global short_break_used

    short_break_used = False

    global current_stage

    current_stage = STAGE_CATCHUP

    remaining = catchup_duration // 2

    remaining_catchup_time = remaining

    while remaining > 0:

        if break_taken:
            return

        await asyncio.sleep(1)

        remaining -= 1

        remaining_catchup_time = remaining

    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return

    await remove_keyboard(
        action_message
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            "Вопрос к тебе.\n\n"
            "Выкладываешься ли ты на полную?\n"
            "Делаешь ли ты всё необходимое для достижения результата?\n"
            "Не тратишь ли время впустую?\n"
            "Проводишь ли ты его с пользой?\n"
            "Ответь себе честно: доволен ли ты собой прямо сейчас?\n"
            f"Тебе ещё нужно доработать: "
            f"{catchup_time // 60:02}:{catchup_time % 60:02}"
        ),
        reply_markup=yes_no_keyboard()
    )

    return

async def catchup_second_half():

    global current_stage
    global day_ended
    global day_pause
    global catchup_duration
    global break_taken

    remaining = catchup_duration // 2

    while remaining > 0:

        if break_taken:
            return

        if not await timer_sleep():
            return

        remaining -= 1

        remaining_catchup_time = remaining

    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return

    global short_break_used

    short_break_used = False

    action_message = await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            "ВПЕРЁЁЁЁД!!!\n\n"

            "Остался последний рывок.\n\n"

            "Не дай себе потом жалеть о том, что ты мог дожать, но остановился.\n\n"

            "Совсем немного усилий сейчас могут сильно повлиять на твоё будущее.\n\n"

            "Заканчиваем этот день достойно.\n\n"

            f"Длительность этапа: "
            f"{format_minutes(catchup_duration // 2)}."
        ),
        reply_markup=work_keyboard()
    )

    remaining = catchup_duration // 2

    while remaining > 0:

        if break_taken:
            return

        if not await timer_sleep():
            return

        remaining -= 1

    while day_pause:
        await asyncio.sleep(1)

    if day_ended:
        return

    await remove_keyboard(
        action_message
    )

    current_stage = STAGE_CATCHUP_FINISH

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            "Финальный вопрос.\n\n"
            "Удалось ли тебе наверстать недостающее время?\n\n"
            "Можешь ли ты честно сказать, что сегодня сделал всё возможное?"
        ),
        reply_markup=yes_no_keyboard()
    )

async def main():

    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=(
            "🕵️ Система находится в режиме ожидания.\n\n"
            "Ждём вашего пробуждения и кодового слова для начала дня."
        )
    )

    await dp.start_polling(bot)

import time

if __name__ == "__main__":

    while True:

        try:

            asyncio.run(main())

        except Exception as e:

            print(
                f"Ошибка соединения: {e}"
            )

            print(
                "Повторная попытка через 10 секунд..."
            )

            time.sleep(10)