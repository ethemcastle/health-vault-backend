# Django App Setup on macOS with MySQL

## 1. Install Prerequisites
Make sure you have the following installed:
- **Python** (≥ 3.10) → check:
```bash
python3 --version
```
- **pip** → check:
```bash
pip3 --version
```
- **MySQL** → install via Homebrew if not present:
```bash
brew install mysql
```

---

## 2. Start MySQL Server
On macOS (Homebrew installation):
```bash
brew services start mysql
```

Verify it’s running:
```bash
mysqladmin -u root -p version
```

---

## 3. Create the Database
Open MySQL shell:
```bash
mysql -u root -p
```
Enter password: `root`

Then run:
```sql
CREATE DATABASE health_vault_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON health_vault_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 4. Clone the Project
```bash
git clone <your-repo-url>
cd <your-project-folder>
```

---

## 5. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 6. Install Requirements
```bash
pip install -r requirements.txt
```

If you don’t have `mysqlclient` installed yet:
```bash
brew install mysql-client
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
pip install mysqlclient
```

---

## 7. Set Environment Variables
Create a `.env` file in your project root:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=health_vault_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
```

---

## 8. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py backfill_default_group
```

---

## 9. Run the Development Server
```bash
python manage.py runserver
```
Visit:  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Common Issues & Fixes
- **`mysqlclient` not installing** → Make sure MySQL client headers are installed:
```bash
brew install mysql-client
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
```
- **Can't connect to DB** → Check MySQL is running and `.env` credentials match.
- **Permission denied on DB** → Run `GRANT ALL PRIVILEGES` again for your user.