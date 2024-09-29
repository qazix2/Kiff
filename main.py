import requests
import telebot
import openpyxl
from telebot import types

API_TOKEN = '7637139659:AAHLnsK7NNV8JnawgexmZd9K5RPcR6asfSA'  # Replace with your actual token
bot = telebot.TeleBot(API_TOKEN)

translations = {}
translation_enabled = True

@bot.message_handler(commands=['toggle_translation'])
def toggle_translation(message):
    global translation_enabled
    translation_enabled = not translation_enabled  # Переключаем состояние
    state = "включен" if translation_enabled else "выключен"
    bot.reply_to(message, f"Перевод сейчас {state}.")
    
# Load translations from an Excel file
def load_translations(file_path):
    global translations
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    translations = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming the first row is headers
        word = row[2]  # Column C
        translation = row[3]  # Column D
        translations[word.lower()] = translation
        translations[translation.lower()] = word  # Add reverse translation

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Kif Translator bot! Please upload an Excel file with translations.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file_path = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        
        # Download the file
        bot.send_message(message.chat.id, "Downloading your file...")
        with open('translations.xlsx', 'wb') as new_file:
            new_file.write(requests.get(file_path).content)
        
        # Load translations
        load_translations('translations.xlsx')
        bot.send_message(message.chat.id, "Translations loaded successfully!")

@bot.message_handler(func=lambda message: True)
def translate_message(message):
    if not translations:
        bot.reply_to(message, "Please upload an Excel file with translations first.")
        return

    search_term = message.text.lower()
    results = [f"{word} - {translation}" for word, translation in translations.items() if search_term in word]
    
    if results:
        response = "\n".join(results)
    else:
        response = "No results found."

    bot.reply_to(message, response)

if __name__ == '__main__':
    bot.polling(none_stop=True)


