# 🔍 Etherscan Transactions Project

Un'app Django per monitorare e visualizzare le transazioni associate a un indirizzo Ethereum tramite l'API di Etherscan.

---

## 🌍 Link

L'app è online e si può accedere tramite [questo link](https://meno96.pythonanywhere.com/transactions/).

---

## 📋 Prerequisiti

- **Python** (>= 3.8)
- **Django** (installato tramite `requirements.txt`)
- **PostgreSQL** (per l'ambiente di sviluppo locale)
- **Etherscan API Key** per accedere alle transazioni

---

## 🚀 Setup del Progetto

### 1. Clona la Repository

```bash
git clone https://github.com/tuo-username/etherscan_project.git
cd etherscan_project
```

### 2. Configura l'Ambiente Virtuale

Crea e attiva un ambiente virtuale Python:

```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa le Dipendenze

```bash
pip install -r requirements.txt
```

---

## 🔑 Configurazione delle Variabili d'Ambiente

### Crea il file `.env`

Nella root del progetto, crea un file `.env` partendo dal file `.env.example` e completalo con tutti i relativi dati.

---

## ⚙️ Configurazione del Database PostgreSQL

1. **Avvia PostgreSQL** e crea il database:
   ```sql
   CREATE DATABASE etherscan_db;
   CREATE USER postgres WITH PASSWORD 'admin';
   ALTER ROLE postgres SET client_encoding TO 'utf8';
   ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
   ALTER ROLE postgres SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE etherscan_db TO postgres;
   ```

2. **Migra il Database**:
   Dopo aver configurato le variabili nel `.env`, esegui le migrazioni per creare le tabelle nel database.

   ```bash
   python manage.py migrate
   ```

---

## 🐞 Debug e Configurazione del Logging

Il progetto è configurato per usare il logging. Gli output di debug saranno registrati in `debug.log`. In locale, per visualizzare i log in console, assicurati che `DEBUG=True` sia impostato nel `.env`.

---

## 🧪 Esecuzione dei Test

Per eseguire i test unitari, usa:

```bash
python manage.py test
```

### Debugger

È configurato un debugger tramite Visual Studio Code. Per avviarlo, crea una cartella `.vscode` e un file `launch.json` al suo interno, utilizza la configurazione che si trova in `launch.json.example` apportando le relative modifiche.

---

## 🌐 Avvio del Server

Per avviare il server di sviluppo Django:

```bash
python manage.py runserver
```

Visita [http://localhost:8000/transactions/](http://localhost:8000/transactions/) per accedere all'applicazione.

---

## 📄 Struttura dei File

- **`config`**: Configurazioni principali dell'app Django.
- **`etherscan_app`**: App principale che contiene modelli, servizi e viste.
- **`static`** e **`templates`**: File CSS e HTML per il frontend.
- **`tests`**: Include test unitari per modelli, viste e servizi.

---
