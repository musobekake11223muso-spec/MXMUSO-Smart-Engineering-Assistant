from __future__ import annotations

import ast
import math
import operator
import sqlite3
import json
import urllib.request
import urllib.error
from pathlib import Path
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "mxmuso.db"

app = Flask(__name__)
app.config.update(JSON_SORT_KEYS=False, MAX_CONTENT_LENGTH=1 * 1024 * 1024)

MODULES = {
    "catalog": "Kompyuter texnikasi katalogi",
    "converter": "Sanoq sistemalari konvertori",
    "algorithms": "Algoritmlar laboratoriyasi",
    "systems": "Operatsion tizimlar",
    "calculator": "Muhandislik kalkulyatori",
    "learning": "O‘quv markazi",
    "ai": "AI muhandis yordamchisi",
}

CATALOG_ITEMS = [
    {"name": "Protsessor (CPU)", "category": "Protsessor", "icon": "🧠", "purpose": "Kompyuter buyruqlarini bajaradi va hisob-kitob qiladi.", "specs": "Yadro, oqim, takt chastotasi, kesh va soket."},
    {"name": "Videokarta (GPU)", "category": "Grafika", "icon": "🎮", "purpose": "Grafika, video va parallel hisoblashni bajaradi.", "specs": "GPU, VRAM, chastota va quvvat sarfi."},
    {"name": "Operativ xotira (RAM)", "category": "Xotira", "icon": "💾", "purpose": "Ishlayotgan dasturlar ma’lumotlarini vaqtincha saqlaydi.", "specs": "Sig‘im, DDR avlodi, tezlik va kechikish."},
    {"name": "SSD disk", "category": "Xotira", "icon": "📀", "purpose": "Fayllar va operatsion tizimni doimiy saqlaydi.", "specs": "Sig‘im, o‘qish-yozish tezligi, SATA yoki NVMe."},
    {"name": "Ona plata", "category": "Plata", "icon": "🖥️", "purpose": "Kompyuter qismlarini o‘zaro bog‘laydi.", "specs": "Chipset, soket, RAM slotlari va portlar."},
    {"name": "Quvvat bloki (PSU)", "category": "Quvvat", "icon": "⚡", "purpose": "Kompyuter qismlarini elektr quvvati bilan ta’minlaydi.", "specs": "Vatt, samaradorlik va ulagichlar."},
    {"name": "Monitor", "category": "Periferiya", "icon": "🖥️", "purpose": "Tasvir va ma’lumotlarni ekranda ko‘rsatadi.", "specs": "Diagonal, ruxsat, yangilanish chastotasi va panel."},
    {"name": "Sovutish tizimi", "category": "Sovutish", "icon": "❄️", "purpose": "Kompyuter qismlarining haroratini me’yorda saqlaydi.", "specs": "Ventilyator, radiator va sovutish turi."},
    {"name": "Klaviatura", "category": "Periferiya", "icon": "⌨️", "purpose": "Matn va buyruqlarni kompyuterga kiritadi.", "specs": "Mexanik yoki membranali, ulanish turi va layout."},
    {"name": "Sichqoncha", "category": "Periferiya", "icon": "🖱️", "purpose": "Kursorni boshqarish va buyruqlarni tanlashga xizmat qiladi.", "specs": "DPI, sensor turi, tugmalar va ulanish."},
]

SYSTEMS = [
    {"name": "Windows", "maker": "Microsoft", "type": "Yopiq kodli", "pros": "Dastur va o‘yinlar bilan keng moslik.", "cons": "Litsenziya talab qilishi mumkin; ayrim qurilmalarda resurs talabchan."},
    {"name": "macOS", "maker": "Apple", "type": "Yopiq kodli", "pros": "Apple qurilmalari bilan yaxshi integratsiya.", "cons": "Asosan Apple kompyuterlarida ishlaydi."},
    {"name": "Linux", "maker": "Ochiq hamjamiyat", "type": "Ochiq kodli", "pros": "Moslashuvchan, ko‘plab distributivlari bepul.", "cons": "Ayrim dasturlarni sozlash qo‘shimcha bilim talab qiladi."},
]

LESSONS = [
    {"title": "Kompyuter arxitekturasi", "body": "Kompyuter protsessor, xotira, ona plata va kiritish-chiqarish qurilmalaridan tashkil topadi."},
    {"title": "Sanoq sistemalari", "body": "Ikkilik sistema 0 va 1 raqamlariga asoslanadi. O‘nlik sistema kundalik hisoblashda ishlatiladi."},
    {"title": "Algoritm tushunchasi", "body": "Algoritm — masalani yechish uchun belgilangan aniq va tartibli ko‘rsatmalar ketma-ketligi."},
    {"title": "Operatsion tizim", "body": "Operatsion tizim kompyuter resurslarini boshqaradi va foydalanuvchi bilan qurilma o‘rtasida aloqa yaratadi."},
    {"title": "Xotira turlari", "body": "RAM vaqtinchalik ishchi xotira, SSD va HDD esa ma’lumotlarni uzoq muddat saqlash uchun ishlatiladi."},
    {"title": "Dasturlash asoslari", "body": "Dasturlash — kompyuter bajarishi uchun algoritm va ko‘rsatmalarni dasturlash tilida ifodalash jarayoni."},
]

FAQ = [
    (("cpu", "protsessor"), "CPU — kompyuterning asosiy hisoblash qurilmasi. U dastur buyruqlarini bajaradi."),
    (("gpu", "videokarta"), "GPU — grafikani qayta ishlaydi va parallel hisoblash vazifalarida ishlatiladi."),
    (("ram", "operativ xotira"), "RAM — dasturlar ishlayotgan paytda kerakli ma’lumotlarni vaqtincha saqlaydi. Elektr uzilganda undagi ma’lumot yo‘qoladi."),
    (("ssd", "disk"), "SSD — ma’lumotlarni doimiy saqlaydigan tezkor xotira qurilmasi."),
    (("algoritm",), "Algoritm — masalani yechish uchun aniq tartibda bajariladigan ko‘rsatmalar ketma-ketligi."),
    (("python",), "Python — o‘qilishi oson sintaksisga ega, avtomatlashtirish, tahlil va dastur yaratishda ishlatiladigan dasturlash tili."),
    (("linux",), "Linux — ochiq kodli yadro asosidagi operatsion tizimlar oilasi."),
    (("windows",), "Windows — Microsoft ishlab chiqqan operatsion tizim."),
    (("macos", "mac os"), "macOS — Apple kompyuterlari uchun ishlab chiqilgan operatsion tizim."),
    (("ikkilik", "binary"), "Ikkilik sanoq sistemasi faqat 0 va 1 raqamlaridan foydalanadi."),
    (("salom",), "Salom! Men MXMUSO muhandis yordamchisiman. Kompyuter texnikasi yoki muhandislik bo‘yicha savol bering."),
]


def get_db():
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS calculation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


        db.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response


@app.route("/")
def home():
    return render_template("index.html", modules=MODULES)


@app.route("/module/<name>")
def module(name):
    if name not in MODULES:
        return render_template("404.html"), 404
    return render_template("module.html", title=MODULES[name], name=name,
                           items=CATALOG_ITEMS, systems=SYSTEMS, lessons=LESSONS)


ALLOWED_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def safe_calculate(node, depth=0):
    if depth > 20:
        raise ValueError("Ifoda juda murakkab.")
    if isinstance(node, ast.Expression):
        return safe_calculate(node.body, depth + 1)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = safe_calculate(node.left, depth + 1)
        right = safe_calculate(node.right, depth + 1)
        if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1_000_000):
            raise ValueError("Daraja yoki asos juda katta.")
        result = ALLOWED_OPERATORS[type(node.op)](left, right)
        if not math.isfinite(float(result)) or abs(result) > 10**100:
            raise ValueError("Natija ruxsat etilgan chegaradan katta.")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](safe_calculate(node.operand, depth + 1))
    raise ValueError("Faqat sonlar, qavslar va +, -, *, /, %, ** amallariga ruxsat beriladi.")


@app.post("/api/calculate")
def calculate():
    data = request.get_json(silent=True) or {}
    expression = str(data.get("expression", "")).strip()
    if not expression or len(expression) > 100:
        return jsonify(error="Ifodani kiriting (100 belgigacha)."), 400
    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 60:
            raise ValueError("Ifoda juda uzun.")
        result = safe_calculate(tree)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 10)
        with get_db() as db:
            db.execute("INSERT INTO calculation_history(expression, result) VALUES (?, ?)",
                       (expression, str(result)))
        return jsonify(result=result)
    except ZeroDivisionError:
        return jsonify(error="Nolga bo‘lish mumkin emas."), 400
    except (ValueError, SyntaxError, OverflowError, TypeError):
        return jsonify(error="Ifoda noto‘g‘ri yoki ruxsat etilmagan."), 400


@app.get("/api/history")
def history():
    with get_db() as db:
        rows = db.execute("SELECT expression, result, created_at FROM calculation_history ORDER BY id DESC LIMIT 10").fetchall()
    return jsonify(items=[dict(row) for row in rows])


@app.post("/api/quiz/score")
def save_quiz_score():
    data = request.get_json(silent=True) or {}
    try:
        score, total = int(data.get("score", 0)), int(data.get("total", 0))
    except (TypeError, ValueError):
        return jsonify(error="Ball qiymati noto‘g‘ri."), 400
    if total < 1 or total > 100 or score < 0 or score > total:
        return jsonify(error="Ball chegarasi noto‘g‘ri."), 400
    with get_db() as db:
        db.execute("INSERT INTO quiz_results(score, total) VALUES (?, ?)", (score, total))
    return jsonify(saved=True, score=score, total=total)


@app.get("/api/quiz/score")
def quiz_history():
    with get_db() as db:
        rows = db.execute("SELECT score, total, created_at FROM quiz_results ORDER BY id DESC LIMIT 10").fetchall()
    return jsonify(items=[dict(row) for row in rows])



@app.post("/api/ask")
def ask():
    data = request.get_json(silent=True) or {}
    original_question = str(data.get("question", "")).strip()
    question = original_question.lower()

    if not question:
        return jsonify(answer="Savolingizni yozing."), 400

    if len(original_question) > 500:
        return jsonify(answer="Savol 500 belgidan oshmasin."), 400

    def save_message(role, content):
        with get_db() as db:
            db.execute(
                "INSERT INTO chat_messages (role, content) VALUES (?, ?)",
                (role, content)
            )

    # FAQ javoblarini tekshirish
    for keywords, faq_answer in FAQ:
        if any(word in question for word in keywords):
            save_message("user", original_question)
            save_message("assistant", faq_answer)
            return jsonify(answer=faq_answer, mode="knowledge-base")

    # Oxirgi 20 ta xabarni olish
    with get_db() as db:
        rows = db.execute(
            "SELECT role, content FROM chat_messages "
            "ORDER BY id DESC LIMIT 20"
        ).fetchall()

    history = [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]

    payload = {
        "model": "qwen3.5:2b",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen MXMUSO nomli o'zbek tilidagi muhandislik "
                    "va dasturlash yordamchisisan. "
                    "Ravon va tushunarli o'zbek tilida javob ber. "
                    "Takrorlardan qoch. Texnik masalalarni bosqichma-bosqich "
                    "tushuntir. Bilmagan narsangni to'qib chiqarmagin."
                )
            },
            *history,
            {"role": "user", "content": original_question}
        ],
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("message", {}).get("content", "").strip()

        if not answer:
            return jsonify(
                answer="AI hozircha javob qaytarmadi.",
                mode="ollama"
            ), 502

        save_message("user", original_question)
        save_message("assistant", answer)

        return jsonify(answer=answer, mode="ollama")

    except urllib.error.URLError:
        return jsonify(
            answer="Ollama bilan bog'lanib bo'lmadi. Ollama ishlayotganini tekshiring.",
            mode="error"
        ), 503

    except TimeoutError:
        return jsonify(
            answer="AI javob berishi uchun vaqt yetmadi. Qayta urinib ko'ring.",
            mode="error"
        ), 504

    except Exception:
        app.logger.exception("MXMUSO AI xatosi")
        return jsonify(
            answer="AI ishlashida xatolik yuz berdi.",
            mode="error"
        ), 500

@app.get("/api/chat/history")
def chat_history():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, role, content, created_at "
            "FROM chat_messages ORDER BY id ASC LIMIT 100"
        ).fetchall()
    return jsonify(items=[dict(row) for row in rows])


@app.delete("/api/chat/history")
def clear_chat_history():
    with get_db() as db:
        db.execute("DELETE FROM chat_messages")
    return jsonify(cleared=True)


@app.get("/api/health")
def health():
    return jsonify(status="online", app="MXMUSO SMART ENGINEERING ASSISTANT", database="sqlite")


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
