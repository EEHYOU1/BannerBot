import discord
from discord import app_commands
import aiohttp
import os
from dotenv import load_dotenv
import urllib.parse
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

STYLES = {
    "gaming": "epic gaming banner, neon lights, dark background, futuristic",
    "anime": "anime style banner, colorful, vibrant, japanese art",
    "minimal": "minimalist banner, clean design, modern, professional",
    "fire": "fire flames banner, intense, dramatic, red and orange",
    "cyberpunk": "cyberpunk banner, neon, dystopian city, purple and blue",
}

async def generate_image(prompt: str, width: int, height: int) -> str:
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 9999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={seed}"
    return url

@tree.command(name="banner", description="Génère une bannière pour ton serveur")
@app_commands.describe(
    texte="Texte principal de la bannière (ex: ARKADIA)",
    style="Style visuel de la bannière",
    slogan="Slogan sous le titre (optionnel)"
)
@app_commands.choices(style=[
    app_commands.Choice(name="Gaming", value="gaming"),
    app_commands.Choice(name="Anime", value="anime"),
    app_commands.Choice(name="Minimal", value="minimal"),
    app_commands.Choice(name="Feu / Intense", value="fire"),
    app_commands.Choice(name="Cyberpunk", value="cyberpunk"),
])
async def banner(interaction: discord.Interaction, texte: str, style: str, slogan: str = ""):
    await interaction.response.defer(thinking=True)
    style_desc = STYLES.get(style, STYLES["gaming"])
    prompt = f"{style_desc}, text '{texte}', {slogan}, banner 1200x400, high quality, no watermark"
    url = await generate_image(prompt, 1200, 400)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                file = discord.File(fp=__import__('io').BytesIO(data), filename="banner.png")
                embed = discord.Embed(title=f"Bannière — {texte}", color=0x5865F2)
                embed.set_image(url="attachment://banner.png")
                embed.set_footer(text=f"Style: {style} • Généré par BannerBot")
                await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send("Erreur lors de la génération. Réessaie !")

@tree.command(name="emote", description="Génère une emote custom pour Discord")
@app_commands.describe(
    description="Décris l'emote que tu veux (ex: chat qui rigole, feu, coeur gaming)"
)
async def emote(interaction: discord.Interaction, description: str):
    await interaction.response.defer(thinking=True)
    prompt = f"discord emote, {description}, simple, flat icon, white background, 128x128, cute, no text"
    url = await generate_image(prompt, 128, 128)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                file = discord.File(fp=__import__('io').BytesIO(data), filename="emote.png")
                embed = discord.Embed(title=f"Emote — {description}", color=0x5865F2)
                embed.set_image(url="attachment://emote.png")
                embed.set_footer(text="Généré par BannerBot")
                await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send("Erreur lors de la génération. Réessaie !")

@tree.command(name="avatar", description="Génère un avatar pour ton serveur Discord")
@app_commands.describe(
    nom="Nom ou thème de l'avatar (ex: dragon, logo ARKADIA, loup)",
    style="Style visuel"
)
@app_commands.choices(style=[
    app_commands.Choice(name="Gaming", value="gaming"),
    app_commands.Choice(name="Anime", value="anime"),
    app_commands.Choice(name="Logo 3D", value="3d logo, render, glossy"),
    app_commands.Choice(name="Pixel Art", value="pixel art, 8bit"),
])
async def avatar(interaction: discord.Interaction, nom: str, style: str):
    await interaction.response.defer(thinking=True)
    prompt = f"{style}, {nom}, discord server icon, square, centered, high quality, no background text"
    url = await generate_image(prompt, 512, 512)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                file = discord.File(fp=__import__('io').BytesIO(data), filename="avatar.png")
                embed = discord.Embed(title=f"Avatar — {nom}", color=0x5865F2)
                embed.set_image(url="attachment://avatar.png")
                embed.set_footer(text="Généré par BannerBot")
                await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send("Erreur lors de la génération. Réessaie !")

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot connecté : {client.user}")
    print("Commandes synchronisées !")

client.run(TOKEN)
