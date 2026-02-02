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

# --- CONFIGURAÇÕES GERAIS (IDs) ---
ID_CARGO_CLIENTE = 123456789012345678  # Substitua pelo ID do cargo que o cliente deve ganhar
ID_CANAL_ESTOQUE = 1467743387754168461 # Seu canal de estoque

# --- VIEW DO SISTEMA DE ESTOQUE ---
class MenuEstoque(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="📦 Qual estoque você quer adicionar?", 
        options=[
            discord.SelectOption(label="Obb holograma + hs", value="Obb holograma + hs", emoji="⚡"),
            # Adicione mais opções aqui se precisar
        ]
    )
    async def select_callback(self, it: discord.Interaction, select: discord.ui.Select):
        nome_produto = select.values[0]
        canal = it.guild.get_channel(ID_CANAL_ESTOQUE)

        if not canal:
            return await it.response.send_message("❌ Canal de estoque não encontrado!", ephemeral=True)

        embed = discord.Embed(
            title="NOVO ESTOQUE⚡!",
            description=f"Foi adicionado um novo estoque!\n\n**{nome_produto}**\n\nGaranta já o seu🤩",
            color=0xFFFF00 
        )
        
        await canal.send(content="@everyone", embed=embed)
        await it.response.send_message(f"✅ Estoque de `{nome_produto}` postado!", ephemeral=True)

# --- VIEW DO PAINEL DE VENDAS ---
class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None
        self.canal_destino = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="👤 Selecione o Cliente")
    async def select_user(self, it: discord.Interaction, sel: discord.ui.UserSelect):
        self.cliente = sel.values[0]
        await it.response.send_message(f"✅ Cliente selecionado: {self.cliente.mention}", ephemeral=True)

    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="📺 Canal de Logs/Compras")
    async def select_channel(self, it: discord.Interaction, sel: discord.ui.ChannelSelect):
        self.canal_destino = sel.values[0]
        await it.response.send_message(f"✅ Canal definido: {self.canal_destino.mention}", ephemeral=True)

    @discord.ui.select(placeholder="👾 Selecione o Produto", options=[
        discord.SelectOption(label="Holograma", value="Holograma"),
        discord.SelectOption(label="headtrick-fruit-ninja", value="headtrick-fruit-ninja"),
        discord.SelectOption(label="pack-de-sensi", value="pack-de-sensi"),
        discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max")
    ])
    async def select_product(self, it: discord.Interaction, sel: discord.ui.Select):
        self.produto = sel.values[0]
        await it.response.send_message(f"✅ Produto: {self.produto}", ephemeral=True)

    @discord.ui.button(label="CONFIRMAR VENDA", style=discord.ButtonStyle.green)
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        await it.response.defer(ephemeral=True) 

        if not all([self.cliente, self.produto, self.canal_destino]):
            return await it.followup.send("❌ Erro: Selecione todos os campos!", ephemeral=True)

        try:
            # 1. Tenta dar o cargo ao cliente
            cargo = it.guild.get_role(ID_CARGO_CLIENTE)
            status_cargo = ""
            if cargo:
                await self.cliente.add_roles(cargo)
                status_cargo = "\n✅ Cargo de Cliente entregue!"

            # 2. Envia a log da venda
            canal_real = it.guild.get_channel(self.canal_destino.id)
            embed = discord.Embed(title="🛒 COMPRA REALIZADA", color=0x2ecc71)
            embed.set_thumbnail(url=self.cliente.display_avatar.url)
            embed.add_field(name="👤 Cliente", value=self.cliente.mention, inline=False)
            embed.add_field(name="📦 Produto", value=f"`{self.produto}`", inline=False)
            embed.set_footer(text=f"Registro Automático{status_cargo}")
            
            await canal_real.send(content=f"🔔 {self.cliente.mention} nova compra!", embed=embed)
            await it.followup.send(f"✅ Sucesso! Venda registrada e cargo entregue.", ephemeral=True)

        except Exception as e:
            await it.followup.send(f"❌ Erro ao processar: {e}", ephemeral=True)

# --- COMANDOS SLASH ---

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ BOT ONLINE: {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(it: discord.Interaction):
    await it.response.send_message(view=PainelVendas(), ephemeral=True)

@bot.tree.command(name="estoque", description="Adicionar novo estoque ao canal")
async def estoque(it: discord.Interaction):
    if not it.user.guild_permissions.administrator:
        return await it.response.send_message("❌ Apenas administradores!", ephemeral=True)
    await it.response.send_message("Escolha o produto para anunciar o estoque:", view=MenuEstoque(), ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ TOKEN não encontrado!")
