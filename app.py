from flask import Flask, render_template, request, redirect, jsonify
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

import os
import bcrypt
import asyncio
import json
import uuid

# =========================
# LOAD ENV
# =========================

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# SESSION FILE
# =========================

SESSIONS_FILE = "sessions.json"

if not os.path.exists(SESSIONS_FILE):

    with open(SESSIONS_FILE, "w") as f:
        json.dump({}, f)

# =========================
# PASSWORD & CODE
# =========================

PASSWORD = "IpanSodong"
CODE = "01042007"

PASSWORD_HASH = bcrypt.hashpw(
    PASSWORD.encode(),
    bcrypt.gensalt()
)

CODE_HASH = bcrypt.hashpw(
    CODE.encode(),
    bcrypt.gensalt()
)

# =========================
# LOGIN PAGE
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    error = False

    if request.method == "POST":

        user_password = request.form["password"]

        if bcrypt.checkpw(
            user_password.encode(),
            PASSWORD_HASH
        ):

            return redirect("/code")

        else:
            error = True

    return f"""
<!DOCTYPE html>
<html>

<head>

<title>Secure Vault</title>

<style>

body{{
margin:0;
height:100vh;

display:flex;
justify-content:center;
align-items:center;

background:#dfe5ec;

font-family:Arial;
}}

.box{{

width:90%;
max-width:290px;

padding:24px;

border-radius:24px;

background:#dfe5ec;

box-shadow:
10px 10px 20px #c3c9cf,
-10px -10px 20px #fbffff;

text-align:center;

}}

@media(max-width:480px){{

.box{{

max-width:260px;
padding:20px;

}}

h1{{

font-size:22px;

}}

input{{

padding:14px;
font-size:14px;

}}

button{{

padding:14px;
font-size:14px;

}}

}}

h1{{
color:#5f6770;
font-weight:600;
margin-bottom:25px;
}}

input{{

box-sizing:border-box;

width:100%;

padding:16px;

border:none;

outline:none;

border-radius:18px;

background:#dfe5ec;

box-shadow:
inset 6px 6px 12px #c8ced4,
inset -6px -6px 12px #f6fcff;

font-size:15px;

margin-top:14px;
}}

button{{

width:100%;

padding:16px;

margin-top:18px;

border:none;

border-radius:18px;

background:#dfe5ec;

font-size:16px;

font-weight:600;

cursor:pointer;

color:#5f6770;

box-shadow:
6px 6px 12px #c3c9cf,
-6px -6px 12px #fbffff;

transition:0.2s;
}}

button:hover{{
transform:translateY(-2px);
}}

button:active{{
box-shadow:
inset 4px 4px 8px #c3c9cf,
inset -4px -4px 8px #fbffff;
}}

.error{{
margin-top:12px;
color:#d14b4b;
}}

</style>

</head>

<body>

<div class="box">

<h1>[ passwd ]</h1>

<form method="POST">

<input
type="password"
name="password"
placeholder="Masukkan password">

<button type="submit">
ENTER
</button>

{"<p class='error'>⚠ password anda salah</p>" if error else ""}

</form>

</div>

</body>
</html>
"""

# =========================
# CODE PAGE
# =========================

@app.route("/code", methods=["GET", "POST"])
def code():

    error = False

    if request.method == "POST":

        user_code = request.form["code"]

        if bcrypt.checkpw(
            user_code.encode(),
            CODE_HASH
        ):

            return redirect("/granted")

        else:
            error = True

    return render_template(
        "code.html",
        error=error
    )

# =========================
# REQUEST ACCESS
# =========================

@app.route("/request-access", methods=["POST"])
def request_access():

    session_id = str(uuid.uuid4())[:8]

    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)

    sessions[session_id] = "waiting"

    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

    async def send_telegram():

        keyboard = [
            [
                InlineKeyboardButton(
                    "YA",
                    url=f"http://127.0.0.1:5000/approve/{session_id}"
                ),

                InlineKeyboardButton(
                    "TIDAK",
                    url=f"http://127.0.0.1:5000/deny/{session_id}"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(
            keyboard
        )

        bot_app = Application.builder()\
            .token(BOT_TOKEN)\
            .build()

        await bot_app.bot.send_message(
            chat_id=CHAT_ID,
            text=f"""
Secure Vault Access Request

Unknown device attempting authentication.

Session ID:
{session_id}
""",
            reply_markup=reply_markup
        )

    asyncio.run(send_telegram())

    return jsonify({
    "success": True,
    "session_id": session_id
})

# =========================
# APPROVE
# =========================

@app.route("/approve/<session_id>")
def approve(session_id):

    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)

    sessions[session_id] = "approved"

    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

    return """
    <body style='
    background:black;
    color:lime;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    font-family:Arial;
    '>

   <h1>ACCESS VERIFIED</h1>

<p style='
color:#8a8a8a;
margin-top:10px;
font-size:18px;
'>
Identity successfully confirmed.
</p>

    </body>
    """

# =========================
# DENY
# =========================

@app.route("/deny/<session_id>")
def deny(session_id):

    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)

    sessions[session_id] = "denied"

    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

    return """
    <body style='
    background:red;
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    font-family:Arial;
    '>

<h1>ACCESS BLOCKED</h1>

<p style='
color:#ffd4d4;
margin-top:10px;
font-size:18px;
'>
Unauthorized access attempt detected.
</p>

    </body>
    """

# =========================
# CHECK SESSION
# =========================

@app.route("/check-session/<session_id>")
def check_session(session_id):

    with open(SESSIONS_FILE, "r") as f:
        sessions = json.load(f)

    status = sessions.get(session_id, "waiting")

    return jsonify({
        "status": status
    })

## =========================
# GRANTED PAGE
# =========================

@app.route("/granted")
def granted():

    return """
<body style='
background:black;
color:lime;
display:flex;
flex-direction:column;
justify-content:center;
align-items:center;
height:100vh;
font-family:Arial;
'>

<h1>WELCOME BACK</h1>

<p style='
color:#8a8a8a;
margin-top:10px;
font-size:18px;
'>
Secure session established.
</p>

<script>

setTimeout(() => {

window.location="/database"

},2000)

</script>

</body>
"""
# =========================
# DATABASE PAGE
# =========================

@app.route("/database")
def database():

    return render_template(
        "database.html"
    )
# =========================
# INTRUDER PAGE
# =========================

@app.route("/intruder")
def intruder():

    with open("bug.html", "r", encoding="utf-8") as f:
        return f.read()

    return """
<body style='
background:red;
color:white;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
font-family:Arial;
'>

<h1>
🚨 ANDA TERDETEKSI
SEBAGAI PENYUSUP 🚨
</h1>

</body>
"""

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False
    )