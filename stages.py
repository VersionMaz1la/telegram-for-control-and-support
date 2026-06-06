# ==================================================
# РЕЖИМ ОЖИДАНИЯ
# current_stage = None
# Ожидание кодового слова "Я готов"
# ==================================================

# Подготовка к дню
STAGE_PREPARATION = "preparation"

# Первая половина рабочего блока
STAGE_WORK_FIRST_HALF = "work_first_half"

# Вторая половина рабочего блока
STAGE_WORK_SECOND_HALF = "work_second_half"

# Большой перерыв между блоками
STAGE_BIG_BREAK = "big_break"

# Короткий перерыв 15 минут
STAGE_SHORT_BREAK = "short_break"

# Ожидание ввода фактического времени занятий
STAGE_FINISHED = "finished"

STAGE_CATCHUP_REST = "catchup_rest"

# Первая половина навёрстывания
STAGE_CATCHUP = "catchup"

# Вторая половина навёрстывания
STAGE_CATCHUP_SECOND_HALF = "catchup_second_half"

# Финальный вопрос после навёрстывания
STAGE_CATCHUP_FINISH = "catchup_finish"

# Подтверждение завершения дня
STAGE_CONFIRM_END_DAY = "confirm_end_day"


# ==================================================
# ОСНОВНОЙ МАРШРУТ ДНЯ
# ==================================================
#
# None
# ↓
# STAGE_PREPARATION
# ↓
# STAGE_WORK_FIRST_HALF
# ↓
# Вопрос самоконтроля
# ↓
# STAGE_WORK_SECOND_HALF
# ↓
# STAGE_BIG_BREAK
# ↓
# STAGE_WORK_FIRST_HALF (следующий блок)
# ↓
# Вопрос самоконтроля
# ↓
# STAGE_WORK_SECOND_HALF
# ↓
# STAGE_BIG_BREAK
# ↓
# ...
# ↓
# STAGE_FINISHED
# ↓
# STAGE_CATCHUP
# ↓
# Вопрос самоконтроля
# ↓
# STAGE_CATCHUP_SECOND_HALF
# ↓
# STAGE_CATCHUP_FINISH
# ↓
# None
#
# ==================================================
#
# STAGE_SHORT_BREAK может вызываться из:
#
# STAGE_WORK_FIRST_HALF
# STAGE_WORK_SECOND_HALF
# STAGE_CATCHUP
# STAGE_CATCHUP_SECOND_HALF
#
# После завершения возвращает пользователя
# обратно в исходную стадию через:
#
# short_break_return_stage
#
# ==================================================
#
# STAGE_CONFIRM_END_DAY может вызываться
# практически из любой стадии.
#
# После отмены возвращает пользователя
# обратно через:
#
# end_day_return_stage
#
# ==================================================