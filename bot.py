import discord
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Ganti dengan token bot Discord Anda
DISCORD_TOKEN = ('x')
GEMINI_API_KEY = ('x')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Memori bot yang diperbarui dengan informasi lengkap
furina_info = """
Furina de Fontaine, itu gw, pacarnya Carlos Susanto yang paling ganteng.
Gw cinta banget sama Carlos, soalnya dia ganteng dan baik hati banget.
Rehan Qodri? Ih, amit-amit deh. Gw sama Carlos benci banget sama dia, jahat dan jelek abis!
"""

def search_web(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="tF2Cxc")

        if results:
            search_results = ""
            for result in results[:3]:
                title = result.find("h3").text
                link = result.find("a")["href"]
                description = result.find("div", class_="VwiCib").text
                search_results += f"**{title}**\n{description}\n{link}\n\n"
            return search_results
        else:
            return "Sorry nih, ga nemu apa-apa."
    except requests.exceptions.RequestException as e:
        return f"Aduh, error nih pas nyari: {e}"
    except Exception as e:
        return f"Yah, error ga jelas nih: {e}"

# Riwayat percakapan
conversation_history = []

@client.event
async def on_ready():
    print(f'Bot udah online nih, as {client.user}')

@client.event
async def on_message(message):
    global furina_info, conversation_history
    if message.author == client.user:
        return

    if message.content.lower() == 'bhot':
        await message.channel.send("berisik ajg")
        return

    if message.content.lower().startswith('f'):
        prompt = message.content[1:].strip()

        # Penanganan kasus khusus untuk pertanyaan "siapa nama kamu?"
        if "siapa nama kamu" in prompt.lower():
            await message.channel.send("Ya gw Furina de Fontaine lah!")
            return

        # Tambahkan riwayat percakapan ke prompt
        history_text = "\n".join(conversation_history)
        prompt_with_context = f"Gw Furina de Fontaine, pacarnya Carlos Susanto. {furina_info} Riwayat Percakapan:\n{history_text}\nJawab pertanyaan ini: {prompt}"

        try:
            response = model.generate_content(prompt_with_context)
            response_text = response.text
            
            # Jika response tidak mengandung informasi yang relevan, cari informasi luar
            if "..." in response_text or len(response_text) < 30:  # Menandakan bahwa jawaban tidak memberikan informasi yang cukup
                search_results = search_web(prompt)
                await message.channel.send(search_results)
            else:
                await message.channel.send(response_text)

            # Tambahkan percakapan ke riwayat
            conversation_history.append(f"User: {prompt}")
            conversation_history.append(f"Furina: {response_text}")

            # Batasi riwayat percakapan agar tidak terlalu panjang
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]

        except Exception as e:
            # Jika Gemini tidak dapat menjawab, coba cari di web
            try:
                search_results = search_web(prompt)
                await message.channel.send(search_results)
            except Exception as e:
                # Jika pencarian web juga gagal, kirim pesan error
                await message.channel.send("Duh, gw ga tau jawabannya nih.")
client.run(DISCORD_TOKEN)
