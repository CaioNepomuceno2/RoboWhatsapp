# Robô de envio de mensagens no WhatsApp Web

Automação em **Python + Selenium** que lê uma lista de contatos em planilha (Excel ou CSV) e envia uma mensagem personalizada para cada número pelo **WhatsApp Web**, registrando o status de cada envio em uma nova planilha.

> Parte da minha trilha de estudos e de automações em Python — [github.com/CaioNepomuceno2](https://github.com/CaioNepomuceno2)

## O que o robô faz

1. Lê a planilha `message_list.xlsx` (ou `.csv`) com as colunas `Number` e `Message`.
2. Abre o navegador (Microsoft Edge por padrão, ou Chrome) controlado pelo Selenium e acessa o WhatsApp Web.
3. Aguarda a leitura do QR Code pelo celular.
4. Para cada linha pendente, abre a conversa via `https://web.whatsapp.com/send?phone=+55<número>&text=<mensagem>` e clica em **Enviar**.
5. Grava o resultado (`Enviada` ou `Erro`) em `result_<dd_mm_aaaa-hh_mm>.xlsx` **após cada mensagem**, para não perder o progresso se a execução for interrompida.

Números sem WhatsApp (aviso "O número de telefone compartilhado por url é inválido") são marcados como `Erro` e o robô segue para o próximo.

## Tecnologias

- Python 3.9+
- [Selenium 4](https://www.selenium.dev/) (o *Selenium Manager* baixa/localiza o driver do navegador automaticamente)
- pandas + openpyxl (leitura e escrita das planilhas)
- pytest (testes automatizados sem abrir navegador)

## Como executar

### 1. Pré-requisitos

- Python 3.9 ou superior
- Microsoft Edge ou Google Chrome instalado
- Uma conta de WhatsApp com acesso ao WhatsApp Web

### 2. Instalação

```bash
git clone https://github.com/CaioNepomuceno2/whatsapp-bot-automacao.git
cd whatsapp-bot-automacao

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Prepare a lista de mensagens

Copie o modelo e preencha com seus contatos:

```bash
cp message_list.example.xlsx message_list.xlsx   # Windows: copy message_list.example.xlsx message_list.xlsx
```

| Coluna    | Conteúdo                                                        | Exemplo                 |
|-----------|-----------------------------------------------------------------|-------------------------|
| `Number`  | DDD + número, só dígitos, **sem** o código do país (+55 é adicionado pelo robô) | `11999990001` |
| `Message` | Texto da mensagem                                               | `Olá! Tudo bem?`        |
| `Status`  | Opcional. Se existir, só as linhas `Pendente` são enviadas      | `Pendente`              |

Os números dos arquivos de exemplo (`message_list.example.xlsx` / `.csv`) são fictícios. A planilha real (`message_list.xlsx`) e os arquivos `result_*.xlsx` estão no `.gitignore` para que dados de contatos não sejam versionados.

### 4. Execute

```bash
python whatsappbot/whatsappbot.py
```

Opções:

```bash
python whatsappbot/whatsappbot.py --entrada minha_lista.csv   # outra planilha (.xlsx ou .csv)
python whatsappbot/whatsappbot.py --navegador chrome          # usa o Chrome em vez do Edge
```

Leia o QR Code quando o WhatsApp Web abrir. Ao final, o caminho do arquivo de resultado é exibido no terminal.

**Retomar um envio interrompido:** como o arquivo `result_*.xlsx` já contém a coluna `Status`, basta passá-lo como entrada (`--entrada result_18_10_2026-14_30.xlsx`); somente as linhas ainda `Pendente` serão enviadas.

### Atalho no Windows e executável

- `whatsappbot/whatsappbot.bat`: atalho para executar o robô com um duplo clique (usa o `python` do PATH ou do ambiente virtual ativo).
- `whatsappbot/whatsappbot.spec`: configuração do [PyInstaller](https://pyinstaller.org/) usada para gerar um executável Windows (está em modo de depuração, `debug=True`). Para gerar: `pip install pyinstaller` e, dentro de `whatsappbot/`, `pyinstaller whatsappbot.spec`. No executável, a planilha padrão é procurada na mesma pasta do `.exe`.

## Testes

Os testes usam um navegador simulado (não abrem o WhatsApp nem enviam mensagens):

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Cobrem a formatação dos números, a montagem da URL, o fluxo de envio (botão encontrado, número inválido, botão ausente) e o controle de status da planilha.

## Estrutura

```
whatsapp-bot-automacao/
├── whatsappbot/
│   ├── whatsappbot.py      # script principal: lê a planilha, envia e grava o status
│   ├── helpers.py          # funções Selenium: abrir navegador, login, enviar mensagem
│   ├── whatsappbot.bat     # atalho para Windows
│   └── whatsappbot.spec    # configuração do PyInstaller
├── tests/                  # testes com pytest (navegador simulado)
├── message_list.example.xlsx
├── message_list.example.csv
├── requirements.txt
└── requirements-dev.txt
```

## Uso responsável e limitações

- **Termos de uso:** o WhatsApp não oferece suporte a automação do WhatsApp Web e seus [Termos de Serviço](https://www.whatsapp.com/legal/terms-of-service) proíbem envio em massa e mensagens automatizadas não autorizadas. O uso pode levar ao **bloqueio do número**. Este projeto tem finalidade de estudo de automação web; para uso comercial, a alternativa oficial é a [WhatsApp Business Platform (API)](https://developers.facebook.com/docs/whatsapp).
- Envie mensagens apenas para pessoas que **consentiram** em recebê-las e respeite a **LGPD** no tratamento dos contatos.
- Os seletores (XPaths) dependem do layout atual do WhatsApp Web; mudanças na interface podem exigir ajustes em `helpers.py`.
- O robô envia apenas texto (anexos não são suportados) e usa o código do país +55 (Brasil) fixo.
- É necessário ler o QR Code a cada execução, pois o navegador abre com um perfil novo.

## Autor

**Caio Henrique Nepomuceno Santos** — [github.com/CaioNepomuceno2](https://github.com/CaioNepomuceno2)
