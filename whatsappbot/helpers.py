import os
import time
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import TimeoutException

def wait_for_xpath_or_refresh(browser, xpath, timeout=30):
    try:
        # Aguarda até que o elemento seja encontrado
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        # Em caso de timeout, atualiza a página e retorna False
        print(f"Elemento não encontrado em {timeout} segundos, atualizando a página.")
        browser.refresh()
        return False

def handle_alert(browser, timeout=5):
    try:
        # Espera até que um alerta esteja presente
        WebDriverWait(browser, timeout).until(EC.alert_is_present(), 'Aguardando pelo alerta aparecer.')
        alert = browser.switch_to.alert
        alert_text = alert.text
        print(f"Alerta encontrado com o texto: {alert_text}")
        alert.accept()
    except (NoAlertPresentException, TimeoutException):
        print("Nenhum alerta encontrado dentro do período de tempo estipulado.")
        
# Formata o número de telefone para remover sufixos .0 ou ,0
def format_phone_number(phone_number):
    phone_str = str(phone_number)
    if phone_str.endswith(".0") or phone_str.endswith(",0"):
        phone_str = phone_str[:-2]
    return phone_str


def clear_console():
    return os.system('cls')


def get_browser():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    webdriver_path = os.path.abspath(F'{current_directory}/../webdriver/msedgedriver.exe')

    options = EdgeOptions()
    options.use_chromium = True
    #options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')

    browser = Edge(executable_path=webdriver_path, options = options)

    browser.maximize_window()
    return browser


def open_whatsapp(browser):
    browser.get('https://web.whatsapp.com/')

    print('Aguardando autenticação no WhatsApp Web...')
    
    find_chat_open = EC.presence_of_element_located(
            (By.XPATH, '//*[@id="side"]/div[1]/div/div/div[2]/div/div[1]'))
    WebDriverWait(browser, 999).until(find_chat_open)
    
    clear_console()

    print('Autenticação confirmada!')
    
    time.sleep(3)

    return None

def send(browser, minimum_send_buttons):
    find_send_button = EC.presence_of_all_elements_located(
        (By.XPATH, '/html/body/div[1]/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span'))

    send_button = WebDriverWait(browser, 60).until(
            find_send_button
        )

    while len(send_button) < minimum_send_buttons:
        send_button = WebDriverWait(browser, 60).until(
            find_send_button
        )

    send_button[0].click()
    

def check_phone(browser):
    while True:
        # time.sleep(0.5)
        english_error_message = browser.find_elements(
            By.XPATH, '//div[text()="Phone number shared via url is invalid."]'
        )

        portuguese_error_message = browser.find_elements(
            By.XPATH, '//div[text()="O número de telefone compartilhado por url é inválido."]'
        )

        phone_error = english_error_message + portuguese_error_message

        phone_ok = browser.find_elements(By.XPATH, '//span[@data-icon="send"]')

        if len(phone_error) > 0:
            return False
        elif len(phone_ok) > 0:
            return True


from selenium.webdriver.common.keys import Keys
import time

# Outras definições e funções aqui...

def send_message(browser, number, message, attachments=[]):
    try:
        minimum_send_buttons = 1
        phone_str = format_phone_number(number)
        print(phone_str)
        message = urlencode({'text': message})
        browser.get(f'https://web.whatsapp.com/send?phone=+55{phone_str}&{message}')
        
        # Loop principal para tentar enviar a mensagem
        for attempt in range(20):
            # Verificando se há mensagens de erro ou se o botão de envio está presente
            english_error_message = browser.find_elements(
                By.XPATH, '//div[text()="Phone number shared via url is invalid."]'
            )
            portuguese_error_message = browser.find_elements(
                By.XPATH, '//div[text()="O número de telefone compartilhado por url é inválido."]'
            )
            phone_error = english_error_message + portuguese_error_message
            send_button = browser.find_elements(
                By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')
            
            # Tenta encontrar um dos elementos especificados 
            send_buttons = browser.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button') + browser.find_elements(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')
            text_box = browser.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]')            

            if len(phone_error) > 0:
                print('Número não existe ou é inválido. Indo para o próximo número.')
                return False 
            elif len(send_button) >= minimum_send_buttons:
                if send_buttons and len(send_buttons) >= minimum_send_buttons:
                    print('Enviando Mensagem')
                    send_buttons[0].click()
                elif text_box:
                    print('Encontrou a caixa de texto, enviando com ENTER')
                    text_box[0].send_keys(Keys.ENTER)
                else:
                    print('Nenhum botão de envio ou caixa de texto encontrada, verificando novamente...')
                    # Aguarda um momento e tenta novamente até encontrar um elemento válido
                    time.sleep(2)
                break
            else:
                # Aguardando 10 segundos antes de tentar novamente
                time.sleep(2)

        if attempt == 19 and len(send_button) < minimum_send_buttons:
            print(f"Não foi possível enviar a mensagem para {phone_str} após as tentativas. Indo para o próximo número.")
            return False

        while True:
            msg_wait = browser.find_elements(By.XPATH, '//span[@data-testid="msg-time"]')
            if len(msg_wait) == 0:
                break
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Ocorreu uma exceção durante o envio da mensagem: {e}")
        return False
