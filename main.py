import telegram
from telegram.ext import Updater, CommandHandler
import os
import requests
import time
import json


def __make_request(currency):
    return requests.get('https://wex.nz/api/3/ticker/' + currency + '_usd')


def __get_rate(currency):
    req = __make_request(currency)
    if req.status_code != 200:
        return False, req.status_code
    else:
        data = req.json()
        rate = data[currency + '_usd']['last']
        return True, rate


def __send_rate(currency, update):
    cur = __get_rate(currency)
    if cur[0]:
        update.message.reply_text(currency.upper() + ' to USD is ' + str(cur[1]))
    else:
        update.message.reply_text('Failed to load the ' + currency.upper() + ' to USD rate with code ' + str(cur[1]))


def btc_current(bot, update):
    __send_rate('btc', update)


def eth_current(bot, update):
    __send_rate('eth', update)


alert_chats = {}
try:
    with open('tmp/alerts.txt') as input_file:
        alert_chats = json.load(input_file)
except IOError:
    print('No config found')
except json.decoder.JSONDecodeError:
    print('Malformed config, ignoring')


DEFAULT_THRESHOLD = 100


def alert_btc(bot, update):
    global alert_chats
    if update.message.text.endswith('disable'):
        del alert_chats[update.message.chat.id]
        update.message.reply_text('Got it, the alert is disabled 👻')
    else:
        threshold = DEFAULT_THRESHOLD
        tokens = update.message.text.split(' ')
        if len(tokens) > 1:
            try:
                threshold = int(tokens[-1])
            except:
                update.message.reply_text('Please send a valid threshold option')

        alert_chats[update.message.chat.id] = threshold
        update.message.reply_text('OK, the alert is set up 👍\nThe threshold is ' + str(threshold))

    with open('tmp/alerts.txt', 'w') as tmp_file:
        json.dump(alert_chats, tmp_file)


updater = Updater(os.environ['WEX_AGENT_TOKEN'])

updater.dispatcher.add_handler(CommandHandler('btc', btc_current))
updater.dispatcher.add_handler(CommandHandler('eth', eth_current))

updater.dispatcher.add_handler(CommandHandler('alert_btc', alert_btc))

updater.start_polling()

bot = updater.bot

last_btc_rate = None


def refresh():
    global bot, alert_chats, last_btc_rate
    print('refreshing...')

    rate_btc = __get_rate('btc')
    if rate_btc[0]:
        for chat in alert_chats.keys():
            if last_btc_rate is None or abs(last_btc_rate - rate_btc[1]) > 1:
                alert_text = 'BTC to USD is *' + str(rate_btc[1]) + '* '
                if last_btc_rate is not None:
                    alert_text += '📈' if last_btc_rate < rate_btc[1] else '📉'
                bot.send_message(chat, alert_text, parse_mode=telegram.ParseMode.MARKDOWN)

        last_btc_rate = rate_btc[1]
    else:
        for chat in alert_chats.keys():
            bot.send_message(chat, 'Oops, failed to refresh the rate ☠️')


for chat in alert_chats.keys():
    bot.send_message(chat, 'Uh-oh, just booted up...️ 🤖')

while True:
    refresh()
    time.sleep(60)
