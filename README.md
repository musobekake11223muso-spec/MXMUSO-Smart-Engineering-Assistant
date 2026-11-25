# MXMUSO — Smart Engineering Assistant

Flask asosidagi o‘zbek tilidagi muhandislik o‘quv platformasi.

## Modullar
1. Kompyuter texnikasi katalogi
2. Sanoq sistemalari konvertori (2, 8, 10, 16; manfiy va katta butun sonlar)
3. Algoritmlar laboratoriyasi
4. Operatsion tizimlar taqqoslanishi
5. Xavfsiz matematik kalkulyator
6. O‘quv markazi
7. Bilimlar bazasiga asoslangan AI yordamchi (generativ model hozircha ulanmagan)

## macOS ishga tushirish
```bash
cd ~/SMART_ENGINEERING_ASSISTANT
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Brauzerda: http://127.0.0.1:5000

## Ma’lumotlar bazasi
SQLite bazasi birinchi ishga tushishda `instance/mxmuso.db` manzilida avtomatik yaratiladi. Hisoblash tarixi va test natijalari saqlanadi.

## API
- `GET /api/health` — server holati
- `POST /api/calculate` — xavfsiz matematik hisoblash
- `GET /api/history` — oxirgi hisoblashlar
- `POST /api/quiz/score` — test natijasini saqlash
- `GET /api/quiz/score` — test natijalari
- `POST /api/ask` — lokal bilimlar bazasidan javob

## Eslatma
AI moduli hozircha kalit so‘zlarga asoslangan lokal bilimlar bazasidir. Tashqi AI yoki lokal LLM bilan integratsiya alohida sozlanadi; API kalitlarini kod ichiga yozmang.
