# Open Data AI Analytics

## Опис проєкту
Цей проєкт реалізує систему обробки відкритих даних із використанням Docker. У ньому побудовано повний цикл роботи з даними: від завантаження CSV-файлу до отримання готових результатів у вигляді звітів і графіків. Дані зберігаються у базі, проходять перевірку якості, аналізуються, візуалізуються та в кінцевому результаті відображаються через веб-інтерфейс.

Контейнеризація дозволяє ізолювати кожен модуль, спростити запуск і зробити систему зручною для розгортання в будь-якому середовищі.

---

## Структура проєкту
Проєкт поділений на окремі частини, кожна з яких відповідає за свою задачу:

- data/ — вхідні дані (CSV-файл)  
- data_load/ — завантаження даних у базу  
- data_quality_analysis/ — перевірка якості даних  
- data_research/ — аналітичний аналіз  
- visualization/ — побудова графіків  
- web/ — веб-інтерфейс  
- plots/ — збережені візуалізації  
- reports/ — сформовані звіти  
- compose.yaml — запуск усіх сервісів  
- .env — налаштування середовища  

---

## Сервіси
Система складається з кількох взаємопов’язаних сервісів:

- data_load — зчитує CSV-файл і завантажує дані у PostgreSQL  
- data_quality_analysis — перевіряє якість даних і формує звіт  
- data_research — аналізує дані та обчислює статистики  
- visualization — будує графіки та зберігає їх  
- web — показує результати у браузері  
- db — база даних PostgreSQL  

Кожен сервіс працює окремо, але разом вони формують єдину систему.

---

## Запуск

Для запуску достатньо однієї команди:

docker compose up --build

Запуск у фоновому режимі:
docker compose up -d

Зупинка:
docker compose down

Перегляд логів:
docker compose logs -f

---

## Порти
- 8000 — веб-інтерфейс → http://localhost:8000  
- 5432 — база даних PostgreSQL  

---

## Дані
Для збереження даних використовується Docker volume postgres_data, що дозволяє не втрачати дані після перезапуску контейнерів.  
Папки data/, reports/ і plots/ підключені як спільні, тому всі сервіси можуть обмінюватися результатами між собою.

---

## Мережа
Усі контейнери працюють у спільній мережі analytics_network, що дозволяє їм взаємодіяти між собою за іменами сервісів (наприклад, db).

---

## Вимоги
- Docker  
- Docker Compose  

---

## Примітка
Після запуску відкрий у браузері:
http://localhost:8000


# Open Data AI Analytics Deployment on Azure.

## Deployment Steps

### 1. Open Azure Cloud Shell

Open **Azure Portal** and start **Azure Cloud Shell**.

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/open-data-ai-analytics-docker.git
cd open-data-ai-analytics-docker/infra/terraform
```

### 3. Initialize and Deploy Terraform

```bash
terraform init
terraform fmt
terraform validate
terraform apply
```

Type `yes` to confirm resource creation.

## What Terraform Creates

* Resource Group
* Virtual Network
* Subnet
* Public IP
* Network Security Group
* Network Interface
* Linux Virtual Machine

## Automatic VM Configuration

Using **cloud-init**, the VM automatically:

* installs Docker
* clones the repository
* starts the application with:

```bash
docker compose up -d
```

This deploys:

* PostgreSQL database
* analytics services
* web interface

## Access the Application

After deployment, open:

```bash
http://PUBLIC_IP:8000
```

`PUBLIC_IP` is shown in Terraform output.

## Result

The project provides a fully automated cloud deployment workflow where infrastructure provisioning and application startup are completed without manual server configuration.
