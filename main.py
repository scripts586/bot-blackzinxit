import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Online"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT CONFIG ---
intents = discord.Intents.default()
intents.members = True  # ESSENCIAL ESTAR LIGADO NO SITE
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# COLOQUE O NOME EXATO DO CANAL AQUI
CANAL_NOME = "compras🛒" 

class Painel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.user = None
        self.item = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Selecione o Cliente")
    async def s1(self, it: discord.Interaction, sel: discord.ui.UserSelect):
        self.user = sel.values[0]
        await it.response.send_message(f"Selecionado: {self.user.name}", ephemeral=True)

    @discord.ui.select(placeholder="Selecione o Produto", options=[
        discord.SelectOption(label="Holograma", value="Holograma"),
        discord.SelectOption(label="headtrick-fruit-ninja", value="headtrick-fruit-ninja"),
        discord.SelectOption(label="pack-de-sensi", value="pack-de-sensi"),
        discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max")
    ])
    async def s2(self, it: discord.Interaction, sel: discord.ui.Select):
        self.item = sel.values[0]
        await it.response.send_message(f"Produto: {self.item}", ephemeral=True)

    @discord.ui.button(label="CONFIRMAR", style=discord.ButtonStyle.green)
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        # RESPOSTA INSTANTÂNEA PARA NÃO DAR "INTERAÇÃO FALHOU"
        await it.response.send_message("Processando...", ephemeral=True)

        if not self.user or not self.item:
            return await it.edit_original_response(content="Erro: Selecione tudo!")

        # Procura o canal
        canal = discord.utils.get(it.guild.channels, name=CANAL_NOME)
        
        if canal:
            embed = discord.Embed(title="🛒 VENDA", description=f"Cliente: {self.user.mention}\nProduto: {self.item}", color=0x00FF00)
            await canal.send(embed=embed)
            await it.edit_original_response(content="✅ Enviado com sucesso!")
        else:
            await it.edit_original_response(content=f"❌ Canal '{CANAL_NOME}' não encontrado!")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT ONLINE: {bot.user}")

@bot.tree.command(name="compra", description="Painel")
async def compra(it: discord.Interaction):
    await it.response.send_message(view=Painel(), ephemeral=True)

keep_alive()
bot.run(os.environ.get('TOKEN'))
