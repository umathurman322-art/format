import os
import json
import random
import asyncio

# 1. СТРОГО ПЕРЕД ИМПОРТОМ PYROGRAM:
# Этот костыль отключает проблемную часть библиотеки, которая не дружит с Python 3.14
os.environ["PYROGRAM_NO_SYNC"] = "1"

from hydrogram import Client, filters
from hydrogram.errors import FloodWait

# --- БИБЛИОТЕКИ СТИЛЕЙ (оставляем как были) ---
class Styles:
    CUTE = [
        "(( * ^ ω ^)) __ня__ {text} ⋆ ˚", "{text} ~~кавай~~ (≧◡≦) ♡",
        "ଘ(੭ˊᵕˋ)੭* ੈ✩‧₊ {text} ✨ ня-ня!", "{text} (◕‿◕✿) *аригато*",
        "✨ {text} ✨ ~десу!", "{text} ૮꒰ ˶• ༝ •˶꒱ა ♡ ня!",
        "⋆ ˚｡⋆୨୧˚ {text} ˚୨୧⋆｡˚ ⋆", "꧁ {text} ꧂ ✧.*", "{text} (´｡• ᵕ •｡`) ♡"
    ]
    RUDE = [
        "**{text}**, ты че, **тупой?**", "{text} **(удали интернет)**", 
        "**{text}** | **рот закрой**", "Слышь, **{text}**, ты кто?"
    ]

class Transformers:
    @staticmethod
    def translit(text):
        chars = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'}
        return "".join(chars.get(c.lower(), c) if c.lower() in chars else c for c in text)

    @staticmethod
    def chaos(text):
        formats = ['**', '__', '~~', '`']
        return "".join(f"{random.choice(formats)}{char}{random.choice(formats)}" for char in text)

    @staticmethod
    def hacker(text):
        reps = {'a':'4','e':'3','i':'1','o':'0','t':'7','s':'5','b':'8'}
        return "".join(reps.get(c.lower(), c) for c in text)

# --- ГЛАВНЫЙ КЛАСС ---
class UltimateBot:
    def __init__(self, config):
        self.conf = config
        self.app = Client(
            "my_account",
            api_id=self.conf['api_id'],
            api_hash=self.conf['api_hash'],
            ipv6=False,
            # Добавляем прокси, чтобы бот шел через твой v2RayN
#            proxy=dict(
 #               hostname="127.0.0.1",
#                port=10801,          # Проверь порт в настройках v2RayN (обычно 10808 для SOCKS5)
 #               scheme="socks5"      # Тип прокси
 #   )
)
        self.mode = config.get('default_mode', 'off')
        self.dynamic = False
        self.speeds = {"fast": 0.2, "medium": 0.6, "slow": 1.2}
        self.current_speed = self.speeds[config.get("speed", "medium")]

    async def get_transformed(self, text, mode):
        if mode == 'translit': return Transformers.translit(text)
        if mode == 'chaos': return Transformers.chaos(text)
        if mode == 'hacker': return Transformers.hacker(text)
        if mode == 'cute': return random.choice(Styles.CUTE).format(text=text)
        if mode == 'rude': return random.choice(Styles.RUDE).format(text=text)
        if mode == 'bold': return f"**{text}**"
        if mode == 'italic': return f"__{text}__"
        if mode == 'mono': return f"`{text}`"
        if mode == 'strike': return f"~~{text}~~"
        return text

    async def run_bot(self):
        # Команда .mode
        @self.app.on_message(filters.me & filters.command("mode", prefixes=self.conf['prefix']))
        async def set_mode(_, message):
            cmd = message.command
            if len(cmd) < 2: return await message.edit("Используй: `.mode [имя] [dyn/static]`")
            self.mode = cmd[1].lower()
            self.dynamic = (len(cmd) > 2 and cmd[2] == "dyn")
            await message.edit(f"✨ Режим: **{self.mode}** | Dyn: **{self.dynamic}**")
            await asyncio.sleep(2); await message.delete()

        # Команда .del
        @self.app.on_message(filters.me & filters.command("del", prefixes=self.conf['prefix']))
        async def delete_msgs(_, message):
            n = int(message.command[1]) if len(message.command) > 1 else 1
            async for msg in self.app.get_chat_history(message.chat.id, limit=n+1):
                await msg.delete()

        # Обработчик сообщений
        @self.app.on_message(filters.me & ~filters.command(["mode", "del"], prefixes=self.conf['prefix']))
        async def handler(_, message):
            if self.mode == 'off' or not message.text: return
            original = message.text
            
            if not self.dynamic:
                new_t = await self.get_transformed(original, self.mode)
                if new_t != original: await message.edit(new_t)
            else:
                for _ in range(6):
                    new_t = await self.get_transformed(original, self.mode)
                    try:
                        await message.edit(new_t)
                        await asyncio.sleep(self.current_speed)
                    except FloodWait as e: await asyncio.sleep(e.value); break
                    except Exception: break

        await self.app.start()
        print("🔥 Бот запущен! Напиши .mode в любом чате.")
        await asyncio.Event().wait()

# --- ТОЧКА ВХОДА (Для Python 3.14) ---
async def start_app():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    bot = UltimateBot(config)
    await bot.run_bot()

if __name__ == "__main__":
    try:
        asyncio.run(start_app())
    except KeyboardInterrupt:
        pass
