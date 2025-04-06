
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
from data import get_genres, get_movies_by_genre, find_movie_by_title
from weather import get_weather

router = Router()

# Стани
class OrderState(StatesGroup):
    waiting_for_email = State()

class WeatherState(StatesGroup):
    waiting_for_city = State()

# Команди 

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
   
    await message.answer(
        f"👋 Вітаю, {message.from_user.first_name}, в нашому магазині фільмів!\n"
        "Я допоможу вам обрати та замовити фільм або дізнатись погоду.\n\n"
        "Скористайтесь командами або кнопками меню:\n"
        "/help - отримати допомогу\n"
        "/genres - показати жанри фільмів\n"
        "/weather - дізнатись погоду\n"
        "/info - інформація про бота",
        reply_markup=kb.main_kb
    )

@router.message(Command('help'))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
   
    help_text = (
        "ℹ️ <b>Довідка по боту:</b>\n\n"
        "Я допоможу вам обрати фільм та дізнатись погоду.\n\n"
        "<b>Основні команди:</b>\n"
        "🔹 /start - почати роботу з ботом\n"
        "🔹 /help - показати це повідомлення\n"
        "🔹 /info - коротка інформація про бота\n"
        "🔹 /genres - показати список жанрів фільмів\n"
        "🔹 /weather - дізнатись погоду\n\n"
        "Також ви можете використовувати кнопки меню для навігації."
    )
    
    await message.answer(help_text, reply_markup=kb.main_kb)

@router.message(Command('info'))
async def cmd_info(message: Message, state: FSMContext):
    await state.clear()
    
    info_text = (
        "🤖 <b>Про бота:</b>\n\n"
        "Це демонстраційний бот-магазин фільмів.\n"
        "Він дозволяє переглядати фільми за жанрами, бачити їх опис та рейтинг, "
        "а також імітувати процес замовлення (збирає email).\n"
        "Також інтегровано функцію перегляду погоди через OpenWeatherMap.\n\n"
        "Версія: 1.1"
    )
    await message.answer(info_text, reply_markup=kb.main_kb)

@router.message(Command('genres'))
async def cmd_genres(message: Message, state: FSMContext):
    await state.clear()
    genres = get_genres()
    if not genres:
         await message.answer("На жаль, наразі немає доступних жанрів.", reply_markup=kb.main_kb)
         return
    await message.answer("Будь ласка, оберіть жанр:", reply_markup=kb.genres_inline_kb())


@router.message(Command('weather'))
async def cmd_weather(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введіть назву міста, для якого хочете дізнатись погоду:")
    await state.set_state(WeatherState.waiting_for_city)



@router.message(F.text == "📜 Обрати Жанр")
async def process_select_genre(message: Message, state: FSMContext):
    await state.clear()
    genres = get_genres()
    if not genres:
         await message.answer("На жаль, наразі немає доступних жанрів.")
         return
    await message.answer("Будь ласка, оберіть жанр:", reply_markup=kb.genres_inline_kb())

@router.message(F.text == "🌤️ Дізнатись погоду")
async def process_get_weather(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введіть назву міста, для якого хочете дізнатись погоду:")
    await state.set_state(WeatherState.waiting_for_city)

# Обробник міста для погоди

@router.message(WeatherState.waiting_for_city)
async def process_city_weather(message: Message, state: FSMContext):
    if not message.text or message.text.startswith('/'):
        await message.answer("Будь ласка, введіть назву міста текстом.")
        return

    city_name = message.text
    await state.update_data(city=city_name)
    weather_info = await get_weather(city_name)
    
    await message.answer(weather_info, reply_markup=kb.main_kb, parse_mode=None) 
    await state.clear()


# Обробники Inline кнопок

@router.callback_query(F.data == "back_to_genres")
async def process_back_to_genres(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "Будь ласка, оберіть жанр:",
        reply_markup=kb.genres_inline_kb()
    )

@router.callback_query(F.data.startswith("genre_"))
async def process_genre_select(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    genre = callback.data.split("_")[1]
    await callback.answer(f"Ви обрали жанр: {genre.capitalize()}")
    movies = get_movies_by_genre(genre)
    if not movies:
        await callback.message.edit_text(
            f"На жаль, у жанрі '{genre.capitalize()}' фільмів поки немає.",
            reply_markup=kb.back_to_genres_inline_kb()
        )
        return

    await callback.message.edit_text(
        f"Фільми в жанрі '{genre.capitalize()}':",
        reply_markup=kb.movies_inline_kb(genre)
    )

@router.callback_query(F.data.startswith("back_to_movies_"))
async def process_back_to_movies(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    genre = callback.data.split("_")[-1]
    await callback.answer()
    await callback.message.edit_text(
        f"Фільми в жанрі '{genre.capitalize()}':",
        reply_markup=kb.movies_inline_kb(genre)
    )


@router.callback_query(F.data.startswith("movie_"))
async def process_movie_select(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        _, genre, title_part = callback.data.split("_", 2)
        movies_in_genre = get_movies_by_genre(genre)
        selected_movie = None
        for movie in movies_in_genre:
            if movie['title'].startswith(title_part):
                 selected_movie = movie
                 break

        if not selected_movie:
            logging.warning(f"Не вдалося знайти фільм за частиною назви: {title_part} в жанрі {genre}")
            await callback.answer("Помилка: Фільм не знайдено.", show_alert=True)
            await callback.message.edit_text(
                f"Фільми в жанрі '{genre.capitalize()}':",
                reply_markup=kb.movies_inline_kb(genre)
            )
            return

        await callback.answer()

        
        movie_info = (
            f"🎬 <b>{selected_movie['title']}</b>\n\n"
            f"📝 <b>Опис:</b> {selected_movie['description']}\n\n"
            f"⭐ <b>Рейтинг:</b> {selected_movie['rating']}/10\n"
            f"💰 <b>Ціна:</b> {selected_movie['price']} грн"
        )
        await callback.message.edit_text(
            movie_info,
           
            reply_markup=kb.movie_details_inline_kb(genre, selected_movie['title'])
        )
    except Exception as e:
        logging.exception("Помилка обробки вибору фільму:")
        await callback.answer("Виникла помилка при показі фільму.", show_alert=True)


@router.callback_query(F.data.startswith("order_"))
async def process_order_start(callback: CallbackQuery, state: FSMContext):
    try:
        _, genre, title_part = callback.data.split("_", 2)
        movies_in_genre = get_movies_by_genre(genre)
        selected_movie = None
        for movie in movies_in_genre:
            if movie['title'].startswith(title_part):
                 selected_movie = movie
                 break

        if not selected_movie:
            await callback.answer("Помилка: Фільм для замовлення не знайдено.", show_alert=True)
            return

        await state.update_data(movie_title=selected_movie['title'], genre=genre, price=selected_movie['price'])
        await callback.answer("Починаємо оформлення замовлення...")
        
        await callback.message.answer(
            f"Для завершення замовлення фільму '{selected_movie['title']}', будь ласка, введіть вашу <b>електронну пошту</b>:",
        )
        await state.set_state(OrderState.waiting_for_email)

    except Exception as e:
        logging.exception("Помилка початку оформлення замовлення:")
        await callback.answer("Виникла помилка при оформленні замовлення.", show_alert=True)
        await state.clear()




@router.message(OrderState.waiting_for_email)
async def process_email_input(message: Message, state: FSMContext):
    if not message.text or '@' not in message.text or message.text.startswith('/'):
        await message.answer("Будь ласка, введіть коректну адресу електронної пошти.")
        return

    user_email = message.text
    order_data = await state.get_data()
    movie_title = order_data.get('movie_title', 'Невідомий фільм')

    
    confirmation_message = (
        f"✅ <b>Замовлення прийнято!</b>\n\n"
        f"<b>Фільм:</b> {movie_title}\n"
        f"<b>Ваша пошта:</b> {user_email}\n"
        f"<b>Ціна:</b> 60 грн\n\n"
        f"Дякуємо за замовлення! ✨\n"
        f"Незабаром наш менеджер зв'яжеться з вами для уточнення деталей оплати та доставки."
    )
    await message.answer(confirmation_message, reply_markup=kb.main_kb)
    logging.info(f"Нове замовлення: Фільм='{movie_title}', Email='{user_email}'")
    await state.clear()