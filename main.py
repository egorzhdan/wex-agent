from telegram.ext import Updater, CommandHandler
import os
import requests


def __get_current(currency, update):
    req = requests.get('https://wex.nz/api/3/ticker/' + currency + '_usd')
    if req.status_code != 200:
        update.message.reply_text('Failed to load the ' + currency.upper() + ' to USD rate with code '
                                  + str(req.status_code))
    else:
        data = req.json()
        update.message.reply_text(currency.upper() + ' to USD is ' + str(data[currency + '_usd']['last']))


def btc_current(bot, update):
    __get_current('btc', update)


def eth_current(bot, update):
    __get_current('eth', update)


updater = Updater(os.environ['WEX_AGENT_TOKEN'])

updater.dispatcher.add_handler(CommandHandler('btc', btc_current))
updater.dispatcher.add_handler(CommandHandler('eth', eth_current))

updater.start_polling()
updater.idle()
