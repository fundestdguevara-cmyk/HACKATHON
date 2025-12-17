import subprocess
import os
import sys

def main():
    # 🔹 Detectar ruta del Python activo (el de .venv)
    python_exe = sys.executable

    # 🔹 Ejecutar API FastAPI
    api_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.api:app", "--port", "8001"]
    )

    # 🔹 Detectar automáticamente el archivo del bot
    bot_file = None
    if os.path.exists("bot.py"):
        bot_file = "bot.py"
    elif os.path.exists("app/telegram_bot.py"):
        bot_file = "app/telegram_bot.py"
    else:
        print("⚠️ No se encontró el archivo del bot (busqué bot.py y app/telegram_bot.py)")
        api_process.terminate()
        return

    print(f"🤖 Ejecutando bot desde: {bot_file}")

    # 🔹 Ejecutar Bot de Telegram con el mismo Python
    bot_process = subprocess.Popen([python_exe, bot_file])

    try:
        api_process.wait()
        bot_process.wait()
    except KeyboardInterrupt:
        print("🛑 Deteniendo servicios...")
        api_process.terminate()
        bot_process.terminate()

if __name__ == "__main__":
    main()