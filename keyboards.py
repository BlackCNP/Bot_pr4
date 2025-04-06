
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import get_genres, get_movies_by_genre

# Головне меню 
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Обрати Жанр")],
        [KeyboardButton(text="🌤️ Дізнатись погоду")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Виберіть дію..."
)



def genres_inline_kb():
    """Створює Inline клавіатуру для вибору жанру."""
    builder = InlineKeyboardBuilder()
    genres = get_genres()
    for genre in genres:
        builder.button(text=genre.capitalize(), callback_data=f"genre_{genre}")
    
    builder.adjust(2) 
    return builder.as_markup()

def movies_inline_kb(genre: str):
    """Створює Inline клавіатуру для вибору фільму в жанрі."""
    builder = InlineKeyboardBuilder()
    movies = get_movies_by_genre(genre)
    if not movies:
       
        builder.button(text="Фільмів немає", callback_data="no_movies")
    else:
        for movie in movies:
            
            callback_title = movie['title'][:30] 
            builder.button(text=movie['title'], callback_data=f"movie_{genre}_{callback_title}") 

    builder.button(text="⬅️ Назад до Жанрів", callback_data="back_to_genres")
    builder.adjust(1) 
    return builder.as_markup()

def movie_details_inline_kb(genre: str, title: str):
    """Створює Inline клавіатуру для дій з фільмом."""
    builder = InlineKeyboardBuilder()
    callback_title = title[:30] 
    builder.button(text="✅ Замовити (60 грн)", callback_data=f"order_{genre}_{callback_title}")
    builder.button(text="⬅️ Назад до фільмів", callback_data=f"back_to_movies_{genre}")
    builder.adjust(1)
    return builder.as_markup()

def confirm_order_inline_kb():
    """Клавіатура підтвердження (можна прибрати, якщо одразу питаємо email)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Підтвердити", callback_data="confirm_order_final")
    builder.button(text="❌ Скасувати", callback_data="cancel_order")
    builder.adjust(2)
    return builder.as_markup()

def back_to_genres_inline_kb():
    """Кнопка Назад до жанрів"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад до Жанрів", callback_data="back_to_genres")
    return builder.as_markup()