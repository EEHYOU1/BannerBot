import discord
from discord import app_commands
import aiohttp
import os
from dotenv import load_dotenv
import urllib.parse
import random
import io

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN manquant !")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ─────────────────────────────────────────
# PROMPT BUILDER — cœur du bot
# ─────────────────────────────────────────

STYLES = {
    "gaming": {
        "label": "🎮 Gaming",
        "base": "epic gaming banner, ultra detailed, cinematic lighting, dark moody atmosphere",
        "fx": "neon grid floor, lens flare, particle effects, depth of field, volumetric fog",
        "colors": "deep black background, electric blue and purple neon accents",
        "quality": "8k render, hyper realistic, professional game art, trending on artstation",
    },
    "cyberpunk": {
        "label": "🌆 Cyberpunk",
        "base": "cyberpunk city banner, dystopian mega city, rain reflections on wet streets",
        "fx": "holographic ads, neon signs, flying cars, rain drops, glitch effects",
        "colors": "purple magenta and cyan palette, high contrast, neon on black",
        "quality": "cinematic, blade runner aesthetic, 8k, ultra detailed, photorealistic",
    },
    "fire": {
        "label": "🔥 Fire",
        "base": "intense fire banner, dramatic flames, ember particles floating",
        "fx": "explosive fire burst, heat distortion, glowing embers, smoke wisps",
        "colors": "deep red orange yellow gradient, black background, glowing highlights",
        "quality": "ultra detailed fire simulation, 8k, cinematic, professional vfx",
    },
    "anime": {
        "label": "⛩️ Anime",
        "base": "anime banner, japanese animation style, beautiful detailed illustration",
        "fx": "sakura petals, energy aura, speed lines, dramatic sky",
        "colors": "vibrant saturated colors, soft gradients, anime color palette",
        "quality": "studio ghibli quality, sharp lineart, professional anime key visual, trending on pixiv",
    },
    "neon": {
        "label": "💜 Neon",
        "base": "neon synthwave banner, retro futuristic aesthetic, 80s vibes",
        "fx": "grid lines, retrowave sun, neon outlines, scanlines, CRT glow",
        "colors": "hot pink magenta and cyan on dark purple background, neon glow",
        "quality": "synthwave art, outrun aesthetic, ultra detailed, high contrast",
    },
    "nature": {
        "label": "🌿 Nature",
        "base": "epic nature landscape banner, dramatic scenery, majestic environment",
        "fx": "god rays through trees, mist, flowing water, dynamic clouds, birds",
        "colors": "lush greens, golden hour light, deep blues, natural palette",
        "quality": "national geographic quality, photorealistic, 8k landscape photography",
    },
    "space": {
        "label": "🚀 Space",
        "base": "epic space banner, galaxy nebula, cosmic scenery, deep space",
        "fx": "stars, nebula clouds, planet surface, aurora, light years of depth",
        "colors": "deep navy black, purple pink nebula, golden stars, cosmic blue",
        "quality": "nasa quality, hubble telescope aesthetic, ultra detailed, photorealistic cosmos",
    },
    "minimal": {
        "label": "⬜ Minimal",
        "base": "minimalist clean banner, geometric shapes, professional design",
        "fx": "subtle shadow, thin lines, geometric pattern, clean negative space",
        "colors": "white or dark background, single accent color, monochrome palette",
        "quality": "swiss design, professional branding, high end minimal aesthetic",
    },
    "medieval": {
        "label": "⚔️ Medieval",
        "base": "epic medieval fantasy banner, dark fantasy world, heroic atmosphere",
        "fx": "castle silhouette, magical runes, sword and shield, dramatic storm sky",
        "colors": "dark stone grey, gold accents, blood red, mystical purple glow",
        "quality": "fantasy concept art, detailed illustration, game of thrones aesthetic, artstation",
    },
    "crypto": {
        "label": "💎 Crypto",
        "base": "futuristic crypto blockchain banner, digital finance, tech aesthetic",
        "fx": "blockchain nodes, crypto coins, matrix data flow, holographic charts",
        "colors": "dark background, gold bitcoin orange, electric blue, green matrix",
        "quality": "professional fintech design, ultra modern, 3d render, high tech",
    },
}

def build_prompt(texte: str, style: str, slogan: str = "", couleur: str = "") -> str:
    s = STYLES.get(style, STYLES["gaming"])
    color_override = f", dominant color {couleur}" if couleur else ""
    slogan_part = f", subtitle text '{slogan}'" if slogan else ""
    prompt = (
        f"{s['base']}, "
        f"bold text '{texte}'{slogan_part}, "
        f"{s['fx']}, "
        f"{s['colors']}{color_override}, "
        f"{s['quality']}, "
        f"no watermark, no signature, banner format"
    )
    return prompt

async def generate_image(prompt: str, width: int, height: int) -> bytes:
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 99999)
  url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={seed}&enhance=true&model=flux"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

# ─────────────────────────────────────────
# COMMANDES
# ─────────────────────────────────────────

style_choices = [app_commands.Choice(name=v["label"], value=k) for k, v in STYLES.items()]

@tree.command(name="banner", description="Génère une bannière ultra qualité pour ton serveur")
@app_commands.describe(
    texte="Texte principal (ex: ARKADIA)",
    style="Style visuel",
    slogan="Slogan sous le titre (optionnel)",
    couleur="Couleur dominante en anglais (ex: red, blue, gold) — optionnel"
)
@app_commands.choices(style=style_choices)
async def banner(interaction: discord.Interaction, texte: str, style: str, slogan: str = "", couleur: str = ""):
    await interaction.response.defer(thinking=True)
    prompt = build_prompt(texte, style, slogan, couleur)
    data = await generate_image(prompt, 1200, 400)
    if data:
        file = discord.File(fp=io.BytesIO(data), filename="banner.png")
        embed = discord.Embed(title=f"🎨 Bannière — {texte}", color=0x5865F2)
        embed.set_image(url="attachment://banner.png")
        embed.set_footer(text=f"Style: {STYLES[style]['label']} • BannerBot")
        await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send("❌ Erreur de génération, réessaie !")

@tree.command(name="emote", description="Génère une emote custom Discord")
@app_commands.describe(
    description="Décris l'emote (ex: chat qui rigole, crâne gaming, feu)",
    style="Style visuel"
)
@app_commands.choices(style=style_choices)
async def emote(interaction: discord.Interaction, description: str, style: str = "gaming"):
    await interaction.response.defer(thinking=True)
    s = STYLES.get(style, STYLES["gaming"])
    prompt = f"discord emote icon, {description}, {s['colors']}, {s['quality']}, simple centered icon, white background, no text, 1:1 ratio"
    data = await generate_image(prompt, 256, 256)
    if data:
        file = discord.File(fp=io.BytesIO(data), filename="emote.png")
        embed = discord.Embed(title=f"😎 Emote — {description}", color=0x5865F2)
        embed.set_image(url="attachment://emote.png")
        embed.set_footer(text=f"Style: {STYLES[style]['label']} • BannerBot")
        await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send("❌ Erreur de génération, réessaie !")

@tree.command(name="avatar", description="Génère un avatar pour ton serveur")
@app_commands.describe(
    nom="Thème ou nom (ex: dragon, loup, ARKADIA)",
    style="Style visuel"
)
@app_commands.choices(style=style_choices)
async def avatar(interaction: discord.Interaction, nom: str, style: str = "gaming"):
    await interaction.response.defer(thinking=True)
    s = STYLES.get(style, STYLES["gaming"])
    prompt = f"discord server avatar, {nom}, {s['base']}, {s['colors']}, {s['quality']}, centered square icon, no text"
    data = await generate_image(prompt, 512, 512)
    if data:
        file = discord.File(fp=io.BytesIO(data), filename="avatar.png")
        embed = discord.Embed(title=f"🖼️ Avatar — {nom}", color=0x5865F2)
        embed.set_image(url="attachment://avatar.png")
        embed.set_footer(text=f"Style: {STYLES[style]['label']} • BannerBot")
        await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send("❌ Erreur de génération, réessaie !")

@tree.command(name="wallpaper", description="Génère un fond d'écran gaming 1920x1080")
@app_commands.describe(
    theme="Thème du wallpaper (ex: dragon, espace, forêt magique)",
    style="Style visuel"
)
@app_commands.choices(style=style_choices)
async def wallpaper(interaction: discord.Interaction, theme: str, style: str = "gaming"):
    await interaction.response.defer(thinking=True)
    s = STYLES.get(style, STYLES["gaming"])
    prompt = f"desktop wallpaper, {theme}, {s['base']}, {s['fx']}, {s['colors']}, {s['quality']}, 16:9 ratio, no text, no watermark"
    data = await generate_image(prompt, 1920, 1080)
    if data:
        file = discord.File(fp=io.BytesIO(data), filename="wallpaper.png")
        embed = discord.Embed(title=f"🖥️ Wallpaper — {theme}", color=0x5865F2)
        embed.set_image(url="attachment://wallpaper.png")
        embed.set_footer(text=f"Style: {STYLES[style]['label']} • BannerBot")
        await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send("❌ Erreur de génération, réessaie !")

@tree.command(name="styles", description="Affiche tous les styles disponibles")
async def styles(interaction: discord.Interaction):
    embed = discord.Embed(title="🎨 Styles disponibles", color=0x5865F2)
    for key, val in STYLES.items():
        embed.add_field(name=val["label"], value=f"`{key}`", inline=True)
    embed.set_footer(text="Utilise ces styles sur /banner, /emote, /avatar, /wallpaper")
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot connecté : {client.user}")
    print(f"✅ Commandes synchronisées !")
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="vos /banner 🎨"
    ))

client.run(TOKEN)
