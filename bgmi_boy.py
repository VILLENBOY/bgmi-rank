import logging
from telebot import TeleBot
import socket
import time

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the Telegram bot with your bot token
BOT_TOKEN = '7478798497:AAGPkqSnpY-Guoj65AWt_VRkx4LjPoWDB7I'
bot = TeleBot(BOT_TOKEN)

# Function to perform the stress test
def perform_test(ip, port, duration, chat_id):
    end_time = time.time() + duration
    count = 0
    while time.time() < end_time:
        send_udp(ip, port)
        count += 1
    bot.send_message(chat_id, f'Test completed! Sent {count} packets.')

# Function to send a UDP packet to the target
def send_udp(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = 'Test packet'
        sock.sendto(message.encode(), (ip, int(port)))
        sock.close()
    except Exception as e:
        logging.error(f'Error sending packet: {e}')

# Handlers to get user inputs
@bot.message_handler(commands=['start_test'])
def start_test(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Please enter the target IP address:')
    bot.register_next_step_handler(message, get_ip)

def get_ip(message):
    ip = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Got the IP! Now enter the port number:')
    bot.register_next_step_handler(message, get_port, ip)

def get_port(message, ip):
    port = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Got the port! Now enter the duration of the test in seconds:')
    bot.register_next_step_handler(message, get_duration, ip, port)

def get_duration(message, ip, port):
    chat_id = message.chat.id
    try:
        duration = int(message.text)
        bot.send_message(chat_id, f'Starting test on {ip}:{port} for {duration} seconds...')
        logging.info(f'Starting test on {ip}:{port} for {duration} seconds...')
        perform_test(ip, port, duration, chat_id)
    except ValueError:
        bot.send_message(chat_id, 'Please enter a valid number for the duration.')
        bot.register_next_step_handler(message, get_duration, ip, port)

@bot.message_handler(commands=['stop'])
def stop_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Stopping operations.')
    bot.clear_step_handler_by_chat_id(chat_id)

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Operation canceled!')
    bot.clear_step_handler_by_chat_id(chat_id)

# Start polling for Telegram bot commands
bot.infinity_polling()

