"""Funções auxiliares para automatizar o envio de mensagens no WhatsApp Web.

Os XPaths abaixo dependem do layout do WhatsApp Web no momento em que o
robô foi escrito. Se o WhatsApp mudar a interface, eles precisam ser
revisados.
"""
import os
import time
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WHATSAPP_URL = 'https://web.whatsapp.com/'
COUNTRY_CODE = '55'  # Brasil

# Lista de conversas: indica que o login (QR Code) foi concluído.
XPATH_CHAT_LIST = '//*[@id="side"]/div[1]/div/div/div[2]/div/div[1]'

# Aviso exibido quando o número da URL não tem WhatsApp (inglês ou português).
XPATH_INVALID_NUMBER = (
    '//div[text()="Phone number shared via url is invalid."]'
    ' | //div[text()="O número de telefone compartilhado por url é inválido."]'
)

# Botão de enviar da conversa (duas variações do layout).
XPATH_SEND_BUTTON = (
    '/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]'
    '/div/div[2]/div[2]/button'
    ' | //*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span'
)

# Ícone de relógio exibido enquanto a mensagem ainda não saiu do aparelho.
XPATH_PENDING_MESSAGE = '//span[@data-testid="msg-time"]'


def format_phone_number(phone_number):
    """Converte o número para texto, removendo o sufixo '.0' ou ',0'.

    O sufixo aparece quando o Excel/pandas lê a coluna como número decimal.
    """
    phone_str = str(phone_number).strip()
    if phone_str.endswith('.0') or phone_str.endswith(',0'):
        phone_str = phone_str[:-2]
    return phone_str


def build_send_url(phone_number, message, country_code=COUNTRY_CODE):
    """Monta a URL do WhatsApp Web que abre a conversa com a mensagem preenchida."""
    query = urlencode({'text': message})
    return f'{WHATSAPP_URL}send?phone=+{country_code}{format_phone_number(phone_number)}&{query}'


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_browser(browser_name='edge'):
    """Abre o navegador controlado pelo Selenium.

    A partir do Selenium 4.6 o Selenium Manager localiza (ou baixa) o driver
    compatível com o navegador instalado, então não é preciso versionar o
    msedgedriver/chromedriver no repositório.
    """
    if browser_name == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')
        browser = webdriver.Chrome(options=options)
    else:
        options = webdriver.EdgeOptions()
        options.add_argument('--log-level=3')
        browser = webdriver.Edge(options=options)

    browser.maximize_window()
    return browser


def open_whatsapp(browser, login_timeout=999):
    """Abre o WhatsApp Web e aguarda o usuário ler o QR Code."""
    browser.get(WHATSAPP_URL)
    print('Aguardando autenticação no WhatsApp Web...')

    WebDriverWait(browser, login_timeout).until(
        EC.presence_of_element_located((By.XPATH, XPATH_CHAT_LIST))
    )

    clear_console()
    print('Autenticação confirmada!')
    time.sleep(3)


def wait_message_leave(browser, timeout=60):
    """Aguarda o ícone de 'mensagem pendente' sumir (envio concluído)."""
    deadline = time.time() + timeout
    while browser.find_elements(By.XPATH, XPATH_PENDING_MESSAGE):
        if time.time() > deadline:
            print('A mensagem ainda aparece como pendente; seguindo para o próximo número.')
            return
        time.sleep(0.5)


def send_message(browser, number, message, attempts=20, interval=2):
    """Abre a conversa com `number` e envia `message`.

    Retorna True quando o botão de enviar foi clicado e False quando o número
    é inválido ou o botão não apareceu dentro das tentativas.
    """
    try:
        phone_str = format_phone_number(number)
        print(phone_str)
        browser.get(build_send_url(phone_str, message))

        for _ in range(attempts):
            if browser.find_elements(By.XPATH, XPATH_INVALID_NUMBER):
                print('Número não existe ou é inválido. Indo para o próximo número.')
                return False

            send_buttons = browser.find_elements(By.XPATH, XPATH_SEND_BUTTON)
            if send_buttons:
                print('Enviando mensagem')
                send_buttons[0].click()
                break

            time.sleep(interval)
        else:
            print(f'Não foi possível enviar a mensagem para {phone_str} após '
                  f'{attempts} tentativas. Indo para o próximo número.')
            return False

        wait_message_leave(browser)
        time.sleep(1)
        return True
    except Exception as e:
        print(f'Ocorreu uma exceção durante o envio da mensagem: {e}')
        return False
