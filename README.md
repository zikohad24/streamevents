# StreamEvents
Aplicació Django per gestionar esdeveniments i usuaris (extensible): base educativa amb bones pràctiques (entorns, estructura, separació de templates/static, etc.).  
Opcionalment es pot integrar MongoDB (via Django) més endavant.

## ✨ Objectius
- Practicar un projecte Django modular.  
- Treballar amb un usuari personalitzat (app `users`).  
- Organitzar `templates`, `static` i `media` correctament.  
- Introduir fitxers d'entorn (`.env`) i bones pràctiques Git.  
- Preparar el terreny per a futures funcionalitats (API, auth avançada, etc.).

## 🧱 Stack Principal

## 📂 Estructura Simplificada
streamevents/
├── config/
├── users/
├── templates/
├── static/
│ ├── css/
│ ├── js/
│ └── img/
├── media/
├── fixtures/
├── seeds/
├── requirements.txt
├── README.md
├── env.example
└── manage.py

## ✅ Requisits previs
## 🚀 Instal·lació ràpida
## 🔐 Variables d'entorn (env.example)
## 👤 Superusuari
## 🗃️ Migrar a MongoDB (opcional futur)
## 🛠️ Comandes útils
## 💾 Fixtures (exemple)
Les **fixtures** s’utilitzen per carregar dades inicials com grups i usuaris.

### 📁 Fitxers
users/fixtures/
├── 01_groups.json
└── 02_users.json
## 🧩 Carregar dades

### 💾 Carregar grups
```bash
python manage.py loaddata users/fixtures/01_groups.json
```
### Carregar usuaris
```bash
python manage.py loaddata users/fixtures/02_users.json
```
🔍 Verificar
```bash
python manage.py shell -c "from django.contrib.auth.models import Group; print(Group.objects.all())"
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print(User.objects.all())
```
## 🌱 Seeds (exemple d'script)
El Seeder permet generar usuaris de prova automàticament amb dades realistes.

📄 Fitxer principal
users/management/commands/seed_users.py

▶️ Ús bàsic
# Crear 10 usuaris nous
```bash
python manage.py seed_users
```
# Crear 25 usuaris nous
```bash
python manage.py seed_users --users 25
```
# Esborrar usuaris antics i crear-ne de nous
```bash
python manage.py seed_users --clear
```
👥 Què crea

Grups: Organitzadors, Participants, Moderadors

Superusuari admin (admin@streamevents.com / admin123)

Usuaris de prova amb contrasenya password123
