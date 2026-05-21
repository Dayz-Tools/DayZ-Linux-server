# 🧟 DayZ Linux Server — Automatic Setup (en_US)

> Automatic setup scripts for **DayZ servers on Linux**, designed to make it easier to create and maintain your own server.

This project is based on a **real server used daily**, already containing several ready-made configurations. This allows you to spin up a functional server with just a few commands.

---

## 📑 Table of Contents

- [How the project works](#-how-the-project-works)
- [Requirements](#-requirements)
- [Configuration variables](#-configuration-variables)
- [System configuration](#-system-configuration-prerequisite)
- [Step-by-step installation](#-step-by-step-installation)
- [Required ports](#-required-ports)
- [Project structure](#-project-structure)
- [Profiles configuration](#-mod-profiles-configuration)
- [Notes](#-notes)
- [Contributing](#-contributing)

---

## ⚙️ How the project works

Inside the `scripts_server` folder there is only one script:

### 🚀 `start_server.sh`

Responsible for installing, configuring and keeping the server running, as well as checking and notifying updates for the server and installed mods.

| Feature | Description |
|---|---|
| 📦 Automatic installation | Installs the server if it doesn't exist yet |
| 🔽 Mod download | Downloads and prepares the configured mods |
| ▶️ Startup | Starts the server automatically |
| 🔍 Monitoring | Monitors the process in real time |
| 🔄 Timed restart | Restarts automatically every **6 hours** |
| 💥 Crash restart | Restarts automatically in case of a **crash** |
| 🔍 Update check | Checks for server and mod updates |
| 🔔 Notification | Notifies when updates are available |
| 💬 Discord Webhook | Optional support for Discord notifications |
| 🤖 Discord Bot | Displays server status in real time on Discord (optional) |

---

## 📋 Requirements

Before starting, make sure you have:

- **Operating System:** Linux (tested on Ubuntu 24.04)
- **Git** installed
- An active **Steam account** with **DayZ** in your Steam library

> ⚠️ **Important:** To download Workshop mods, the Steam account used **must own DayZ**.

---

## 🔐 Configuration variables

When the script runs for the first time, it will ask for your credentials, which will be used by **SteamCMD** to download the server and Workshop mods.

All settings are automatically saved to the `scripts_server/config.env` file, which is shared between `start_server.sh` and `bot.py`.

---

### Optional — Discord Notifications

```bash
WEBHOOK_URL_SERVER=""   # Server restart notifications
WEBHOOK_URL_MOD=""      # Mod update notifications
```

You will receive notifications when:

- 🔄 The server **restarts** or **updates**
- ⬇️ A mod is **updated**

---

### Optional — Discord Bot (Server Status)

```bash
DISCORD_BOT_TOKEN=""   # Discord bot token
DISCORD_BOT_IP=""      # Public IP of the DayZ server (e.g. 177.123.456.234)
```

When configured, the Discord bot will display the **server status** as the bot's activity in real time, updating every 60 seconds:

- ✅ `12/60 - Server Name` — when the server is online
- ❌ `Server offline` — when the server is not responding

> ⚠️ **Important:** If `DISCORD_BOT_TOKEN` or `DISCORD_BOT_IP` are empty, the bot **will not start** and Python 3 and its modules **will not be installed**.

---

## ⚙️ System configuration (prerequisite)

On Linux, DayZ requires the `vm.max_map_count` kernel parameter to be set to a minimum value of `1048576`. Without this, the server will not start. It is recommended to configure this **once** before running the server for the first time, using one of the options below:

---

### Option 1 — Apply manually (temporary)

The value is lost when the VPS/machine restarts.

```bash
sudo sysctl -w vm.max_map_count=1048576
```

---

### Option 2 — Make it permanent (recommended)

Creates a configuration file that is loaded automatically every time the system starts. Done **once**, no need to repeat. If `99-dayzserver.conf` doesn't work, try `/etc/sysctl.conf` instead.

```bash
echo "vm.max_map_count=1048576" | sudo tee /etc/sysctl.d/99-dayzserver.conf
sudo sysctl --system
```

---

## 🚀 Step-by-step installation

**1. Create the server folder:**

```bash
mkdir $HOME/steamcmd/dayzserver
cd $HOME/steamcmd/dayzserver
```

**2. Clone the project:**

```bash
git clone https://github.com/Dayz-Tools/DayZ-Linux-server.git .
```

**3. Start the server:**

```bash
./scripts_server/start_server.sh
```

**4. (Optional) Configure:**

- Discord Webhook:

```bash
sed -i 's|^WEBHOOK_URL_MOD=.*|WEBHOOK_URL_MOD="your_discord_webhook_url"|' scripts_server/config.env
sed -i 's|^WEBHOOK_URL_SERVER=.*|WEBHOOK_URL_SERVER="your_discord_webhook_url"|' scripts_server/config.env
```

- Discord Bot:

```bash
sed -i 's|^DISCORD_BOT_TOKEN=.*|DISCORD_BOT_TOKEN="your_token_here"|' scripts_server/config.env
sed -i 's|^DISCORD_BOT_IP=.*|DISCORD_BOT_IP="your_ip_here"|' scripts_server/config.env
```

On the first run, the script will automatically:

1. Install **SteamCMD**
2. Download the **DayZ Server**
3. Download the **configured mods**
4. **Start** the server
5. Start the **Discord Bot** *(if configured)*

---

## 🤖 How to create a Discord bot

If you don't have a bot yet, follow the steps below:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and give your bot a name
3. Go to **Bot** in the side menu and click **Reset Token** to generate the token
4. Copy the token and paste it into `DISCORD_BOT_TOKEN` in `config.env`
5. Under **OAuth2 → URL Generator**, select the `bot` scope and the `Send Messages` permission
6. Use the generated link to invite the bot to your Discord server

---

## 🌐 Required ports

For the server to appear in the DayZ Launcher, open the following ports:

| Port | Protocol | Usage |
|---|---|---|
| `2302 - 2305` | UDP | DayZ Server |
| `27016` | UDP | Steam Query / Discord Bot (A2S) |

> ⚠️ Ports must be open in the **system firewall**, on the **server/VPS**, and on your **router** (if hosting at home).

---

## 📂 Project structure

```
DayZ-Linux-server/
│
├── scripts_server/
│   ├── logs/                # Server and Discord Bot logs
│   ├── mod_ids.txt          # List of mod IDs to be used on the server
│   ├── config.env           # Shared settings (Steam credentials, Discord Bot)
│   ├── bot.py               # Discord bot to display server status (optional)
│   └── start_server.sh      # Main startup and update-check script
│
├── serverDZ.cfg.example     # Basic server configuration
├── profiles/                # Server mod settings
├── keys/                    # Mod keys
├── servermod/               # Server-side only mods folder
├── mpmissions/              # Server mission folder (init.c, types.xml, events.xml)
└── README.md
```

---

## 🔧 Mod profiles configuration

After cloning the project, update the mod settings below via the command line (from the project root, e.g. `$HOME/steamcmd/dayzserver`).

> ⚠️ These files contain **passwords and API keys** — do not share or commit real values to Git. **Restart the server** after any change.

### GameLabs — `profiles/gamelabs.cfg`

```bash
sed -i 's|"connectionVerification": 0|"connectionVerification": 1|' profiles/gamelabs.cfg
sed -i 's|"serverId": ".*"|"serverId": "YOUR_SERVER_ID_HERE"|' profiles/gamelabs.cfg
sed -i 's|"apiKey": ".*"|"apiKey": "YOUR_API_KEY_HERE"|' profiles/gamelabs.cfg
```

| Field | Description |
|---|---|
| `connectionVerification` | `0` = off, `1` = GameLabs API verification enabled |
| `serverId` | Server ID from the GameLabs panel |
| `apiKey` | API key from the GameLabs panel |

Use `connectionVerification": 0` in the first command if you want verification disabled.

### BattlEye RCon — `profiles/BattlEye/BEServer_x64.cfg`

```bash
sed -i 's|^RConPassword.*|RConPassword "YOUR_RCON_PASSWORD_HERE"|' profiles/BattlEye/BEServer_x64.cfg
```

### VPP Admin Tools — `profiles/VPPAdminTools/Permissions/credentials.txt`

The file must contain **only one line** with the superadmin password (no blank lines).

```bash
echo -n 'YOUR_VPP_PASSWORD_HERE' > profiles/VPPAdminTools/Permissions/credentials.txt
```

### Apply changes (restart)

```bash
screen -S dayzserver -X quit
sleep 2 && screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

| File | What to update |
|---|---|
| `profiles/gamelabs.cfg` | `connectionVerification`, `serverId`, `apiKey` |
| `profiles/BattlEye/BEServer_x64.cfg` | `RConPassword` |
| `profiles/VPPAdminTools/Permissions/credentials.txt` | Single-line VPP password |

---

## ⚠️ Notes

- Tested on **Ubuntu 24.04**
- May not work directly on other Linux distributions
- Depending on your system's directory structure, adjustments may be needed
- The `config.env` file contains sensitive credentials — **do not share or commit** this file

---

## 💡 Project goals

This project was created to:

- ✅ Make it easier to run DayZ servers on Linux
- ✅ Automate mod updates
- ✅ Reduce manual maintenance
- ✅ Serve as a base for server administrators

---

## 🤝 Contributing

Suggestions, improvements and fixes are welcome!

1. **Fork** the project
2. Create a **branch** for your feature (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -m 'feat: my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. Open a **Pull Request**

---

## 🧟 Have fun!

Now just start the server and survive in Chernarus. Good luck, survivor!

---

## 🖥️ Keeping the server alive with Screen

By default, closing the terminal or disconnecting from the VPS terminates all running processes — including the DayZ server. **Screen** solves this by creating terminal sessions that keep running in the background.

### 📦 Installing Screen

```bash
# Ubuntu / Debian
sudo apt-get install screen -y
```

---

### ▶️ Starting the server with Screen

```bash
screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

| Parameter | Description |
|---|---|
| `-S dayzserver` | Sets the session name |
| `-dm` | Starts the session in the background (detached) |
| `bash -c '...'` | Command to run inside the session |

---

### 📋 Checking active sessions

```bash
screen -ls
```

Example output:
```
There is a screen on:
    12345.dayzserver    (Detached)
1 Socket in /run/screen/S-user.
```

---

### 🔍 Attaching to a session (view live logs)

```bash
screen -r dayzserver
```

> ⚠️ To **exit without stopping** the session, press `Ctrl + A` then `D`. This keeps the server running in the background.

---

### 🛑 Stopping the server

```bash
screen -S dayzserver -X quit
```

---

### 🔄 Restarting the server

```bash
# Stop the current session
screen -S dayzserver -X quit

# Wait 2 seconds and start again
sleep 2 && screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

---

### 📌 Quick reference

| Action | Command |
|---|---|
| Start server | `screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'` |
| List active sessions | `screen -ls` |
| Attach to session | `screen -r dayzserver` |
| Exit without stopping | `Ctrl + A` → `D` |
| Stop session | `screen -S dayzserver -X quit` |

---

# 🧟 DayZ Linux Server — Setup Automático (pt_BR)

> Scripts de configuração automática para servidores do **DayZ em Linux**, com o objetivo de facilitar a criação e manutenção do seu próprio servidor.

A base deste projeto é um **servidor real utilizado no dia a dia**, já contendo diversas configurações prontas. Com isso, é possível subir um servidor funcional com poucos comandos.

---

## 📑 Sumário

- [Como o projeto funciona](#-como-o-projeto-funciona)
- [Requisitos](#-requisitos)
- [Variáveis de configuração](#-variáveis-de-configuração)
- [Configuração do sistema](#-configuração-do-sistema-pré-requisito)
- [Instalação passo a passo](#-instalação-passo-a-passo)
- [Portas necessárias](#-portas-necessárias)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Configuração profiles](#-configuração-profiles)
- [Observações](#-observações)
- [Contribuições](#-contribuições)

---

## ⚙️ Como o projeto funciona

Dentro da pasta `scripts_server` possui apenas um script:

### 🚀 `start_server.sh`

Responsável por instalar, configurar e manter o servidor em execução, além de verificar e notificar atualizações do servidor e dos mods instalados.

| Funcionalidade | Descrição |
|---|---|
| 📦 Instalação automática | Instala o servidor caso ainda não exista |
| 🔽 Download de mods | Baixa e prepara os mods configurados |
| ▶️ Inicialização | Inicia o servidor automaticamente |
| 🔍 Monitoramento | Monitora o processo em tempo real |
| 🔄 Reinício por tempo | Reinicia automaticamente a cada **6 horas** |
| 💥 Reinício por crash | Reinicia automaticamente em caso de **crash** |
| 🔍 Verificação | Verifica atualizações do servidor e dos mods instalados |
| 🔔 Notificação | Notifica quando houver atualizações disponíveis |
| 💬 Discord Webhook | Suporte opcional para notificações via Discord |
| 🤖 Discord Bot | Exibe status do servidor em tempo real no Discord (opcional) |

---

## 📋 Requisitos

Antes de iniciar, certifique-se de que possui:

- **Sistema Operacional:** Linux (testado em Ubuntu 24.04)
- **Git** instalado
- **Conta Steam** ativa, com jogo **DayZ** na biblioteca da Steam

> ⚠️ **Importante:** Para baixar mods da Workshop, a conta Steam utilizada **precisa possuir o DayZ** na biblioteca.

---

## 🔐 Variáveis de configuração

Durante a execução do script, será solicitado suas credenciais que serão usadas pelo **SteamCMD** para baixar o servidor e os mods da Workshop.

Todas as configurações são salvas automaticamente no arquivo `scripts_server/config.env`, que é compartilhado entre o `start_server.sh` e o `bot.py`.

---

### Opcionais — Notificações via Discord

```bash
WEBHOOK_URL_SERVER=""   # Notificações de reinício do servidor
WEBHOOK_URL_MOD=""      # Notificações de atualização de mods
```

Com isso você receberá notificações quando:

- 🔄 O servidor **reiniciar** ou **atualizar**
- ⬇️ Um mod for **atualizado**

---

### Opcionais — Discord Bot (Status do servidor)

```bash
DISCORD_BOT_TOKEN=""   # Token do bot do Discord
DISCORD_BOT_IP=""      # IP público do servidor DayZ (ex: 177.123.456.234)
```

Quando configurado, o bot do Discord exibirá em tempo real o **status do servidor** como atividade do bot, atualizando a cada 60 segundos:

- ✅ `12/60 - Nome do Servidor` — quando o servidor está online
- ❌ `Server offline` — quando o servidor não responde

> ⚠️ **Importante:** Se `DISCORD_BOT_TOKEN` ou `DISCORD_BOT_IP` estiverem vazios, o bot **não será iniciado** e o Python 3 e seus módulos **não serão instalados**.

---

## ⚙️ Configuração do sistema (pré-requisito)
 
No linux, o DayZ exige que o parâmetro `vm.max_map_count` esteja com um valor mínimo de `1048576`. Sem isso, o servidor não inicializa. É recomendado configurar isso **uma única vez** antes de iniciar o servidor pela primeira vez, escolhendo uma das opções abaixo:
 
---
 
### Opção 1 — Aplicar manualmente (temporário)
 
O valor é perdido ao reiniciar a VPS/máquina.
 
```bash
sudo sysctl -w vm.max_map_count=1048576
```
 
---
 
### Opção 2 — Tornar permanente (recomendado)
 
Crie um arquivo de configuração que é carregado automaticamente toda vez que o sistema inicia. Feito **uma única vez**, não precisa repetir. Caso `99-dayzserver.conf` não funcione, tente em: `/etc/sysctl.conf`.
 
```bash
echo "vm.max_map_count=1048576" | sudo tee /etc/sysctl.d/99-dayzserver.conf
sudo sysctl --system
```

---

## 🚀 Instalação passo a passo

**1. Crie a pasta do servidor:**

```bash
mkdir $HOME/steamcmd/dayzserver
cd $HOME/steamcmd/dayzserver
```

**2. Clone o projeto:**

```bash
git clone https://github.com/Dayz-Tools/DayZ-Linux-server.git .
```

**3. Inicie o servidor:**

```bash
./scripts_server/start_server.sh
```

**4. (Opcional) Configure:**

- Webhook do Discord:

```bash
sed -i 's|^WEBHOOK_URL_MOD=.*|WEBHOOK_URL_MOD="webhook_discord_url"|' scripts_server/config.env
sed -i 's|^WEBHOOK_URL_SERVER=.*|WEBHOOK_URL_SERVER="webhook_discord_url"|' scripts_server/config.env
```

- Bot do Discord:

```bash
sed -i 's|^DISCORD_BOT_TOKEN=.*|DISCORD_BOT_TOKEN="seu_token_aqui"|' scripts_server/config.env
sed -i 's|^DISCORD_BOT_IP=.*|DISCORD_BOT_IP="seu_ip_aqui"|' scripts_server/config.env
```

Na primeira execução, o script irá automaticamente:

1. Instalar o **SteamCMD**
2. Baixar o **DayZ Server**
3. Baixar os **mods configurados**
4. **Iniciar** o servidor
5. Iniciar o **Bot do Discord** *(se configurado)*

---

## 🤖 Como criar um bot no Discord

Caso ainda não tenha um bot criado, siga os passos abaixo:

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em **New Application** e dê um nome ao bot
3. Vá em **Bot** no menu lateral e clique em **Reset Token** para gerar o token
4. Copie o token e cole em `DISCORD_BOT_TOKEN` no `config.env`
5. Em **OAuth2 → URL Generator**, selecione o escopo `bot` e a permissão `Send Messages`
6. Use o link gerado para convidar o bot ao seu servidor Discord

---

## 🌐 Portas necessárias

Para que o servidor apareça no Launcher do DayZ, libere as seguintes portas:

| Porta | Protocolo | Uso |
|---|---|---|
| `2302 - 2305` | UDP | Servidor DayZ |
| `27016` | UDP | Steam Query / Discord Bot (A2S) |

> ⚠️ As portas devem estar liberadas no **firewall do sistema**, no **servidor/VPS** e no **roteador** (caso esteja hospedando em casa).

---

## 📂 Estrutura do projeto

```
DayZ-Linux-server/
│
├── scripts_server/
│   ├── logs/                # Logs do servidor e do Discord Bot
│   ├── mod_ids.txt          # Lista com ids dos mods que serão utilizados no servidor
│   ├── config.env           # Configurações compartilhadas (credenciais Steam, Discord Bot)
│   ├── bot.py               # Bot do Discord para exibir status do servidor (opcional)
│   └── start_server.sh      # Script principal de inicialização e verificação de atualizações
│
├── serverDZ.cfg.example     # Configurações básicas do servidor
├── profiles/                # Configurações dos mods do servidor
├── keys/                    # Chaves dos mods
├── servermod/               # Pasta dos mods que são carregados apenas do lado servidor.
├── mpmissions/              # Pasta da missão do servidor (init.c, types.xml, events.xml)
└── README.md
```

---

## 🔧 Configuração profiles

Após clonar o projeto, atualize as configurações dos mods abaixo pela linha de comando (na raiz do projeto, ex.: `$HOME/steamcmd/dayzserver`).

> ⚠️ Esses arquivos contêm **senhas e chaves de API** — não compartilhe nem faça commit de valores reais no Git. **Reinicie o servidor** após qualquer alteração.

### GameLabs — `profiles/gamelabs.cfg`

```bash
sed -i 's|"connectionVerification": 0|"connectionVerification": 1|' profiles/gamelabs.cfg
sed -i 's|"serverId": ".*"|"serverId": "SEU_SERVER_ID_AQUI"|' profiles/gamelabs.cfg
sed -i 's|"apiKey": ".*"|"apiKey": "SUA_API_KEY_AQUI"|' profiles/gamelabs.cfg
```

| Campo | Descrição |
|---|---|
| `connectionVerification` | `0` = desligado, `1` = verificação via API GameLabs ativa |
| `serverId` | ID do servidor no painel GameLabs |
| `apiKey` | Chave de API do painel GameLabs |

Use `connectionVerification": 0` no primeiro comando se quiser manter a verificação desligada.

### BattlEye RCon — `profiles/BattlEye/BEServer_x64.cfg`

```bash
sed -i 's|^RConPassword.*|RConPassword "SUA_SENHA_RCON_AQUI"|' profiles/BattlEye/BEServer_x64.cfg
```

### VPP Admin Tools — `profiles/VPPAdminTools/Permissions/credentials.txt`

O arquivo deve conter **apenas uma linha** com a senha de superadmin (sem linhas em branco).

```bash
echo -n 'SUA_SENHA_VPP_AQUI' > profiles/VPPAdminTools/Permissions/credentials.txt
```

### Aplicar as mudanças (reiniciar)

```bash
screen -S dayzserver -X quit
sleep 2 && screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

| Arquivo | O que atualizar |
|---|---|
| `profiles/gamelabs.cfg` | `connectionVerification`, `serverId`, `apiKey` |
| `profiles/BattlEye/BEServer_x64.cfg` | `RConPassword` |
| `profiles/VPPAdminTools/Permissions/credentials.txt` | Senha VPP em uma única linha |

---

## ⚠️ Observações

- Testado em **Ubuntu 24.04**
- Pode não funcionar diretamente em outras distribuições Linux
- Dependendo da estrutura de diretórios do seu sistema, ajustes podem ser necessários
- O arquivo `config.env` contém credenciais sensíveis — **não o compartilhe nem faça commit** deste arquivo

---

## 💡 Objetivo do projeto

Este projeto foi criado para:

- ✅ Facilitar a criação de servidores DayZ no Linux
- ✅ Automatizar atualizações de mods
- ✅ Reduzir manutenção manual
- ✅ Servir como base para administradores de servidores

---

## 🤝 Contribuições

Sugestões, melhorias e correções são bem-vindas!

1. Faça um **fork** do projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/minha-feature`)
3. Faça o **commit** das suas alterações (`git commit -m 'feat: minha feature'`)
4. Faça o **push** para a branch (`git push origin feature/minha-feature`)
5. Abra um **Pull Request**

---

## 🧟 Divirta-se!

Agora é só iniciar o servidor e sobreviver em Chernarus. Boa sorte, sobrevivente!

---

## 🖥️ Mantendo o servidor ativo com Screen

Por padrão, ao fechar o terminal ou desconectar da VPS, todos os processos em execução são encerrados — incluindo o servidor DayZ. O **Screen** resolve isso permitindo criar sessões de terminal que continuam rodando em segundo plano.

### 📦 Instalação do Screen

```bash
# Ubuntu / Debian
sudo apt-get install screen -y
```

---

### ▶️ Iniciando o servidor com Screen

```bash
screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

| Parâmetro | Descrição |
|---|---|
| `-S dayzserver` | Define o nome da sessão |
| `-dm` | Inicia a sessão em segundo plano (detached) |
| `bash -c '...'` | Comando a ser executado na sessão |

---

### 📋 Verificando sessões ativas

```bash
screen -ls
```

Exemplo de saída:
```
There is a screen on:
    12345.dayzserver    (Detached)
1 Socket in /run/screen/S-user.
```

---

### 🔍 Acessando a sessão (visualizar logs em tempo real)

```bash
screen -r dayzserver
```

> ⚠️ Para **sair sem encerrar** a sessão, pressione `Ctrl + A` e depois `D`. Isso mantém o servidor rodando em segundo plano.

---

### 🛑 Encerrando o servidor

```bash
screen -S dayzserver -X quit
```

---

### 🔄 Reiniciando o servidor

```bash
# Encerra a sessão atual
screen -S dayzserver -X quit

# Aguarda 2 segundos e inicia novamente
sleep 2 && screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

---

### 📌 Referência rápida

| Ação | Comando |
|---|---|
| Iniciar servidor | `screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'` |
| Ver sessões ativas | `screen -ls` |
| Acessar sessão | `screen -r dayzserver` |
| Sair sem encerrar | `Ctrl + A` → `D` |
| Encerrar sessão | `screen -S dayzserver -X quit` |

---

### Webhooks dos Mods — Notificações via Discord

Abaixo estão os arquivos de configuração dos mods que suportam notificações via Discord Webhook. Todos são **opcionais**, mas recomendados para acompanhar eventos do servidor em tempo real.

> ⚠️ **Reinicie o servidor** após qualquer alteração.

| Arquivo | Campo |
|---|---|
| `profiles/BXDKoth/KothConfig.json` | `KOTH_Web_hook` |
| `profiles/BXD_InterceptFlag/config.json` | `eventWebhook` |
| `profiles/BXDHeli/HeliConfig.json` | `HELI_Web_hook` |
| `profiles/AC/Settings/KillFeed.json` | `m_Webhook` |
| `profiles/BXD_Sequestrador/BXD_Sequestrador_Settings.json` | `discordAddress` |

#### KOTH — `profiles/BXDKoth/KothConfig.json`

```bash
sed -i 's|"KOTH_Web_hook": ".*"|"KOTH_Web_hook": "SEU_WEBHOOK_AQUI"|' profiles/BXDKoth/KothConfig.json
```

#### Intercept Flag — `profiles/BXD_InterceptFlag/config.json`

```bash
sed -i 's|"eventWebhook": ".*"|"eventWebhook": "SEU_WEBHOOK_AQUI"|' profiles/BXD_InterceptFlag/config.json
```

#### Heli — `profiles/BXDHeli/HeliConfig.json`

```bash
sed -i 's|"HELI_Web_hook": ".*"|"HELI_Web_hook": "SEU_WEBHOOK_AQUI"|' profiles/BXDHeli/HeliConfig.json
```

#### AC Kill Feed — `profiles/AC/Settings/KillFeed.json`

```bash
sed -i 's|"m_Webhook": ".*"|"m_Webhook": "SEU_WEBHOOK_AQUI"|' profiles/AC/Settings/KillFeed.json
```

#### Sequestrador — `profiles/BXD_Sequestrador/BXD_Sequestrador_Settings.json`

```bash
sed -i 's|"discordAddress": ".*"|"discordAddress": "SEU_WEBHOOK_AQUI"|' profiles/BXD_Sequestrador/BXD_Sequestrador_Settings.json
```

#### Aplicar as mudanças (reiniciar)

```bash
screen -S dayzserver -X quit
sleep 2 && screen -S dayzserver -dm bash -c './scripts_server/start_server.sh'
```

---
