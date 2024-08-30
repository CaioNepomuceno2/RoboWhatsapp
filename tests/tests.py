import context  # noqa
from whatsappbot.helpers import get_browser
from whatsappbot.helpers import open_whatsapp
from whatsappbot.helpers import send_message
from datetime import datetime
import os
import random
import requests
import pandas as pd

current_path = os.path.dirname(os.path.abspath(__file__))

current_time = datetime.now().strftime('%d_%m_%Y-%H_%M')

pd.DataFrame()

browser = get_browser()

open_whatsapp(browser)

image_path = os.path.abspath(F'{current_path}/random_image.png')

with open(F'{current_path}/afi-top-100-quotes.csv', 'r') as f:
    messages = f.readlines()


mensagens = [send_message(browser, '67998616161', message),
send_message(browser, '67998617397', message),
send_message(browser, '67998616161', message),
send_message(browser, '67998617397', message),
send_message(browser, '67998616161', message),
send_message(browser, '67998617397', message),
send_message(browser, '67998616161', message)]

for mensagem in mensagens:
    random_number = random.randint(0, 99)
    message = messages[random_number]

    resultado = mensagem

    if resultado:
        





# for i in range(0, 5):
#     random_number = random.randint(0, 99)
#     message = messages[random_number]

#     random_image = requests.get('https://source.unsplash.com/random')

#     with open('random_image.png', 'wb') as f:
#         f.write(random_image.content)

#     send_message(browser, '67998617397', message, [image_path])

browser.quit()
