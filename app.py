import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


API_TOKEN = 'Токен бот'
GROUP_CHAT_ID = '-ID-Групового-чата'
logging.basicConfig(level=logging.INFO)

class FormStates(StatesGroup):
    Name = State()
    Phone = State()
    Topic = State()
    Account = State()


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
dp = Dispatcher(bot, storage=MemoryStorage())
message_counter = 1

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global message_counter
    await message.answer(f"Добро пожаловать!\n"
                         f"Для заполнения формы обратной связи, введите /feedback.")
   

# Обработчик команды /feedback
@dp.message_handler(commands=['feedback'])
async def feedback_start(message: types.Message):
    await FormStates.Name.set()
    await message.answer("Пожалуйста, укажите своё имя:")

# Обработчик ввода имени
@dp.message_handler(state=FormStates.Name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
         # Получаем имя пользователя из данных аккаунта
        data['account'] = message.from_user.username
    await FormStates.next()
    await message.answer("Введите ваш номер телефона:")

# Обработчик ввода телефона
@dp.message_handler(state=FormStates.Phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await FormStates.next()
    await message.answer("Укажите тему обращения:")

# Обработчик ввода темы обращения
@dp.message_handler(state=FormStates.Topic)
async def process_topic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['topic'] = message.text
    await message.answer("Получаю данные")
    await state.finish()
    await message.answer("Заявка принята")
    await bot.send_message(message.chat.id, text=f"Новое обращение #{message_counter}:\n\n"
                                                      f"Account: @{data['account']} \n"
                                                      f"Имя: {data['name']}\n"
                                                      f"Телефон: {data['phone']}\n"
                                                      f"Тема: {data['topic']}")
    await message.answer("Что бы создать новое обращение введите /feedback ")
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Новое обращение #{message_counter}:\n\n"
                                                      f"Account: @{data['account']} \n"
                                                      f"Имя: {data['name']}\n"
                                                      f"Телефон: {data['phone']}\n"
                                                      f"Тема: {data['topic']}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
