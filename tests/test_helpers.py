from urllib.parse import parse_qs, urlparse

import helpers


def test_format_phone_number_remove_sufixo_decimal():
    assert helpers.format_phone_number(11999990001.0) == '11999990001'
    assert helpers.format_phone_number('11999990001,0') == '11999990001'
    assert helpers.format_phone_number(' 11999990001 ') == '11999990001'


def test_build_send_url_inclui_ddi_e_mensagem_codificada():
    url = helpers.build_send_url('11999990001', 'Olá, tudo bem?')
    query = parse_qs(urlparse(url).query)

    assert url.startswith('https://web.whatsapp.com/send?phone=+5511999990001&')
    assert query['text'] == ['Olá, tudo bem?']


class FakeElement:
    def __init__(self):
        self.clicked = False

    def click(self):
        self.clicked = True


class FakeBrowser:
    """Simula o navegador: devolve elementos conforme o XPath consultado."""

    def __init__(self, invalid=False, has_button=True):
        self.invalid = invalid
        self.button = FakeElement() if has_button else None
        self.visited = []

    def get(self, url):
        self.visited.append(url)

    def find_elements(self, by, xpath):
        if xpath == helpers.XPATH_INVALID_NUMBER:
            return [object()] if self.invalid else []
        if xpath == helpers.XPATH_SEND_BUTTON:
            return [self.button] if self.button else []
        return []


def test_send_message_clica_no_botao_de_enviar(monkeypatch):
    monkeypatch.setattr(helpers.time, 'sleep', lambda _: None)
    browser = FakeBrowser()

    assert helpers.send_message(browser, '11999990001', 'Teste') is True
    assert browser.button.clicked
    assert 'phone=+5511999990001' in browser.visited[0]


def test_send_message_numero_invalido(monkeypatch):
    monkeypatch.setattr(helpers.time, 'sleep', lambda _: None)
    assert helpers.send_message(FakeBrowser(invalid=True), '11999990001', 'Teste') is False


def test_send_message_sem_botao_apos_tentativas(monkeypatch):
    monkeypatch.setattr(helpers.time, 'sleep', lambda _: None)
    browser = FakeBrowser(has_button=False)
    assert helpers.send_message(browser, '11999990001', 'Teste', attempts=3) is False
