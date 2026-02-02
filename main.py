import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- SISTEMA PARA MANTER ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CONFIGURAÇÃO DOS INTENTS ---
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

    # 1. Selecionar o Cliente
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="👤 Selecione o Cliente")
    async def select_user(self, it: discord.Interaction, sel: discord.ui.UserSelect):
        self.cliente = sel.values[0]
        await it.response.send_message(f"✅ Cliente selecionado: {self.cliente.mention}", ephemeral=True)

    # 2. Selecionar o Canal (Onde vai cair a log)
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="📺 Selecione o Canal de Compras")
    async def select_channel(self, it: discord.Interaction, sel: discord.ui.ChannelSelect):
        self.canal_destino = sel.values[0]
        await it.response.send_message(f"✅ Canal definido: {self.canal_destino.mention}", ephemeral=True)

    # 3. Selecionar o Produto/Xit
    @discord.ui.select(placeholder="👾 Selecione o Xit", options=[
        discord.SelectOption(label="Holograma", value="Holograma"),
        discord.SelectOption(label="headtrick-fruit-ninja", value="headtrick-fruit-ninja"),
        discord.SelectOption(label="pack-de-sensi", value="pack-de-sensi"),
        discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max")
    ])
    async def select_product(self, it: discord.Interaction, sel: discord.ui.Select):
        self.produto = sel.values[0]
        await it.response.send_message(f"✅ Produto: {self.produto}", ephemeral=True)

    # 4. Botão de Confirmar (Onde o erro morre)
    @discord.ui.button(label="CONFIRMAR VENDA", style=discord.ButtonStyle.green)
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        # Ganha 15 minutos de tempo para o bot processar tudo
        await it.response.defer(ephemeral=True) 

        if not all([self.cliente, self.produto, self.canal_destino]):
            return await it.followup.send("❌ Erro: Você esqueceu de selecionar algo!", ephemeral=True)

        try:
            # CONVERSÃO: Transforma a referência do canal em um canal de texto real
            canal_real = it.guild.get_channel(self.canal_destino.id)
            if not canal_real:
                canal_real = await it.guild.fetch_channel(self.canal_destino.id)

            # Cria a Embed Bonitona
            embed = discord.Embed(title="🛒 COMPRA REALIZADA", color=0x2ecc71)
            embed.set_thumbnail(url=self.cliente.display_avatar.url)
            embed.add_field(name="👤 Cliente", value=self.cliente.mention, inline=False)
            embed.add_field(name="📦 Produto", value=f"`{self.produto}`", inline=False)
            embed.set_footer(text="Registro de Vendas Automático")
            
            # Envia para o canal selecionado
            await canal_real.send(content=f"🔔 {self.cliente.mention} nova compra!", embed=embed)
            
            # Avisa quem usou o comando que deu certo
            await it.followup.send(f"✅ Sucesso! Venda enviada para {canal_real.mention}", ephemeral=True)

        except Exception as e:
            # Se der erro de permissão, ele avisa aqui
            print(f"Erro detalhado: {e}")
            await it.followup.send(f"❌ Erro ao enviar: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ BOT ONLINE: {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(it: discord.Interaction):
    # Envia o painel
    await it.response.send_message(view=PainelVendas(), ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ TOKEN não encontrado nos Secrets!")
