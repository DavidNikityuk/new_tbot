from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import calendar
import locale

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except:
        pass

def get_calendar_selection_text():
    return "Может быть, вы хотите выбрать удобную для вас дату? 📅"

def get_calendar_selection_keyboard():
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"📅 {now.strftime('%B %Y')}", 
                callback_data=f"calendar_month_{current_year}_{current_month}"
            ),
            InlineKeyboardButton(
                text=f"📅 {datetime(next_year, next_month, 1).strftime('%B %Y')}", 
                callback_data=f"calendar_month_{next_year}_{next_month}"
            )
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="calendar_cancel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_calendar_keyboard(year=None, month=None):
    now = datetime.now()
    
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    selected_date = datetime(year, month, 1)
    if selected_date.date() < now.date().replace(day=1):
        year = now.year
        month = now.month
    
    cal = calendar.monthcalendar(year, month)
    month_name = datetime(year, month, 1).strftime('%B %Y')
    keyboard = []
    header_row = []
    is_current_month = (year == now.year and month == now.month)
    
    if not is_current_month:
        if month > 1:
            prev_month = month - 1
            prev_year = year
        else:
            prev_month = 12
            prev_year = year - 1
        
        header_row.append(InlineKeyboardButton(
            text="◀", 
            callback_data=f"calendar_prev_{prev_year}_{prev_month}"
        ))
    
    header_row.append(InlineKeyboardButton(
        text=month_name, 
        callback_data="calendar_info"
    ))
    
    if month < 12:
        next_month = month + 1
        next_year = year
    else:
        next_month = 1
        next_year = year + 1
    
    header_row.append(InlineKeyboardButton(
        text="▶", 
        callback_data=f"calendar_next_{next_year}_{next_month}"
    ))
    keyboard.append(header_row)
    
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([InlineKeyboardButton(text=day, callback_data="calendar_weekday") for day in weekdays])
    
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="calendar_empty"))
            else:
                current_date = datetime(year, month, day)
                if current_date.date() < now.date():
                    row.append(InlineKeyboardButton(
                        text=f"·{day}·", 
                        callback_data="calendar_past"
                    ))
                else:
                    row.append(InlineKeyboardButton(
                        text=str(day), 
                        callback_data=f"calendar_date_{year}_{month}_{day}"
                    ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="calendar_cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_time_slots_keyboard(year, month, day):
    time_slots = [
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00"
    ]
    
    today = datetime.now()
    selected_date = datetime(year, month, day)
    
    if selected_date.date() < today.date():
        keyboard = [
            [InlineKeyboardButton(text="❌ Прошедшая дата", callback_data="calendar_error")],
            [InlineKeyboardButton(
                text="◀ Назад к календарю",
                callback_data=f"calendar_month_{year}_{month}"
            )],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="calendar_cancel")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    if selected_date.date() == today.date():
        current_time = today.time()
        filtered_slots = []
        for slot in time_slots:
            slot_time = datetime.strptime(slot, "%H:%M").time()
            if slot_time > current_time:
                filtered_slots.append(slot)
        time_slots = filtered_slots
    
    keyboard = []
    row = []
    
    for i, slot in enumerate(time_slots):
        row.append(InlineKeyboardButton(
            text=slot,
            callback_data=f"time_slot_{year}_{month}_{day}_{slot}"
        ))
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton(
            text="◀ Назад к календарю",
            callback_data=f"calendar_month_{year}_{month}"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="calendar_cancel"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_time_slots_text(year, month, day):
    selected_date = datetime(year, month, day)
    date_str = selected_date.strftime("%d.%m.%Y")
    return f"Отлично! Выбрана дата: {date_str}\n\nТеперь выберите удобное время для консультации:" 