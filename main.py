import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- MANTÉM ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CONFIG BOT ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None
        self.canal_destino = None

    # Selecionar o Cliente
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="👤 Selecione o Cliente")
    async def select_user(self, it: discord.Interaction, sel: discord.ui.UserSelect):
        self.cliente = sel.values[0]
        await it.response.send_message(f"✅ Cliente: {self.cliente.mention}", ephemeral=True)

    # Selecionar o Canal (MUITO MAIS FÁCIL)
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="📺 Selecione o Canal de Compras")
    async def select_channel(self, it: discord.Interaction, sel: discord.ui.ChannelSelect):
        self.canal_destino = sel.values[0]
        await it.response.send_message(f"✅ Canal definido: {self.canal_destino.mention}", ephemeral=True)

    # Selecionar o Produto
    @discord.ui.select(placeholder="👾 Selecione o Xit", options=[
        discord.SelectOption(label="Holograma", value="Holograma"),
        discord.SelectOption(label="headtrick-fruit-ninja", value="headtrick-fruit-ninja"),
        discord.SelectOption(label="pack-de-sensi", value="pack-de-sensi"),
        discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max")
    ])
    async def select_product(self, it: discord.Interaction, sel: discord.ui.Select):
        self.produto = sel.values[0]
        await it.response.send_message(f"✅ Produto: {self.produto}", ephemeral=True)

    # Botão de Confirmar
    @discord.ui.button(label="CONFIRMAR VENDA", style=discord.ButtonStyle.green)
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        await it.response.defer(ephemeral=True) # Ganha tempo

        if not all([self.cliente, self.produto, self.canal_destino]):
            return await it.followup.send("❌ Erro: Selecione Cliente, Canal e Produto!", ephemeral=True)

        try:
            embed = discord.Embed(title="🛒 COMPRA REALIZADA", color=0x2ecc71)
            embed.add_field(name="Cliente", value=self.cliente.mention, inline=False)
            embed.add_field(name="Produto", value=f"`{self.produto}`", inline=False)
            
            await self.canal_destino.send(content=self.cliente.mention, embed=embed)
            await it.followup.send(f"✅ Venda enviada para {self.canal_destino.mention}!", ephemeral=True)
        except Exception as e:
            await it.followup.send(f"❌ Erro ao enviar: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot Online: {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel")
async def compra(it: discord.Interaction):
    await it.response.send_message(view=PainelVendas(), ephemeral=True)

keep_alive()
bot.run(os.environ.get('TOKEN'))
