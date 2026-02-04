import discord
from discord.ext import commands
from discord import app_commands # Adicionei a importação explícita
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

# --- CONFIGURAÇÕES DE IDs ---
ID_CARGO_CLIENTE = 123456789012345678  
ID_CANAL_ESTOQUE = 1467743387754168461
ID_CANAL_TICKET_POST = 1467746343664750673

# --- 1. CLASSE DO TICKET ---
class BotaoTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Compre aqui!", style=discord.ButtonStyle.blurple, custom_id="ticket_vendas", emoji="🛒")
    async def create_ticket(self, it: discord.Interaction, btn: discord.ui.Button):
        nome_canal = f"🛒-{it.user.name}"
        existente = discord.utils.get(it.guild.channels, name=nome_canal.lower())
        if existente:
            return await it.response.send_message(f"❌ Já tens um ticket em {existente.mention}", ephemeral=True)

        overwrites = {
            it.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            it.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            it.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_char = await it.guild.create_text_channel(nome_canal, overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 Atendimento Iniciado",
            description=f"Olá {it.user.mention}, bem-vindo ao teu ticket!\n\nUtiliza o comando `/compra` para registar o teu pedido aqui dentro.",
            color=0x5865F2
        )
        await ticket_char.send(embed=embed)
        await it.response.send_message(f"✅ Ticket criado em {ticket_char.mention}", ephemeral=True)

# --- 2. CLASSE DO MENU DE ESTOQUE ---
class MenuEstoque(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="📦 Qual estoque queres adicionar?", 
        options=[
            discord.SelectOption(label="Obb holograma + hs", value="Obb holograma + hs", emoji="⚡"),
            discord.SelectOption(label="SENSI PACK", value="SENSI PACK", emoji="🔥"), # ADICIONADO AQUI
        ]
    )
    async def select_callback(self, it: discord.Interaction, select: discord.ui.Select):
        nome_produto = select.values[0]
        canal = it.guild.get_channel(ID_CANAL_ESTOQUE)
        if not canal: return await it.response.send_message("Canal de estoque não encontrado!", ephemeral=True)

        embed = discord.Embed(
            title="NOVO ESTOQUE⚡!",
            description=f"Foi adicionado um novo estoque!\n\n**{nome_produto}**\n\nGaranta já o seu🤩",
            color=0xFFFF00 
        )
        await canal.send(content="@everyone", embed=embed)
        await it.response.send_message(f"✅ Estoque de `{nome_produto}` postado!", ephemeral=True)

# --- 3. CLASSE DO PAINEL DE VENDAS ---
class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None
        self.canal_log = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="👤 Selecione o Cliente")
    async def select_user(self, it: discord.Interaction, sel: discord.ui.UserSelect):
        self.cliente = sel.values[0]
        await it.response.send_message(f"✅ Cliente: {self.cliente.mention}", ephemeral=True)

    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="📺 Canal de Logs")
    async def select_channel(self, it: discord.Interaction, sel: discord.ui.ChannelSelect):
        self.canal_log = sel.values[0]
        await it.response.send_message(f"✅ Canal definido: {self.canal_log.mention}", ephemeral=True)

    @discord.ui.select(placeholder="👾 Selecione o Produto", options=[
        discord.SelectOption(label="Holograma", value="Holograma"),
        discord.SelectOption(label="Obb holograma + hs", value="Obb holograma + hs"),
        discord.SelectOption(label="SENSI PACK", value="SENSI PACK"), # ADICIONADO AQUI TAMBÉM
        discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max")
    ])
    async def select_product(self, it: discord.Interaction, sel: discord.ui.Select):
        self.produto = sel.values[0]
        await it.response.send_message(f"✅ Produto: {self.produto}", ephemeral=True)

    @discord.ui.button(label="CONFIRMAR VENDA", style=discord.ButtonStyle.green)
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        if not all([self.cliente, self.produto, self.canal_log]):
            return await it.response.send_message("❌ Erro: Falta selecionar dados!", ephemeral=True)

        await it.response.defer(ephemeral=True) 
        try:
            cargo = it.guild.get_role(ID_CARGO_CLIENTE)
            status_cargo = ""
            if cargo:
                await self.cliente.add_roles(cargo)
                status_cargo = "\n✅ Cargo entregue!"

            embed = discord.Embed(title="🛒 COMPRA REALIZADA", color=0x2ecc71)
            embed.set_thumbnail(url=self.cliente.display_avatar.url)
            embed.add_field(name="👤 Cliente", value=self.cliente.mention, inline=False)
            embed.add_field(name="📦 Produto", value=f"`{self.produto}`", inline=False)
            embed.set_footer(text=f"Registro Automático{status_cargo}")
            
            await self.canal_log.send(content=f"🔔 {self.cliente.mention} nova compra!", embed=embed)
            await it.followup.send(f"✅ Venda registrada com sucesso!", ephemeral=True)
        except Exception as e:
            await it.followup.send(f"❌ Erro: {e}", ephemeral=True)

# --- EVENTOS ---

@bot.event
async def on_ready():
    bot.add_view(BotaoTicket())
    # Sincroniza os comandos globalmente
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sincronizados {len(synced)} comandos slash.")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")
    print(f"✅ BOT ONLINE: {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(it: discord.Interaction):
    await it.response.send_message(view=PainelVendas(), ephemeral=True)

@bot.tree.command(name="estoque", description="Postar aviso de estoque")
async def estoque(it: discord.Interaction):
    if not it.user.guild_permissions.administrator:
        return await it.response.send_message("❌ Apenas Admins!", ephemeral=True)
    await it.response.send_message("Selecione o produto:", view=MenuEstoque(), ephemeral=True)

@bot.tree.command(name="set_ticket", description="Enviar a mensagem de ticket personalizada")
async def set_ticket(it: discord.Interaction):
    if not it.user.guild_permissions.administrator:
        return await it.response.send_message("❌ Apenas Admins!", ephemeral=True)

    canal = it.guild.get_channel(ID_CANAL_TICKET_POST)
    if not canal: return await it.response.send_message("Canal de postagem não encontrado!", ephemeral=True)

    embed = discord.Embed(title="Faça sua compra aqui!", color=0x5865F2)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1194067497519955988/1379104467915374642/banner_tickets.png")
    
    await canal.send(embed=embed, view=BotaoTicket())
    await it.response.send_message("✅ Painel de Ticket enviado!", ephemeral=True)

# Corrigido o espaço aqui
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ TOKEN não encontrado!")
