import os

# Força a instalação das bibliotecas caso elas sumam
try:
    import discord
    from flask import Flask
except ImportError:
    os.system("pip install discord.py flask")
    import discord
    from flask import Flask

from discord.ext import commands
from discord import app_commands
from threading import Thread

# --- MANTÉM O BOT VIVO ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURAÇÃO DO BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs IMPORTANTES (Substitua pelos números do seu Discord)
ID_CANAL_COMPRAS = 000000000000000000  
ID_CARGO_CLIENTE = 000000000000000000  

class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="[Cliente📌]")
    async def select_user(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        self.cliente = select.values[0]
        await interaction.response.send_message(f"Selecionado: {self.cliente.mention}", ephemeral=True)

    @discord.ui.select(
        placeholder="[Opções👾]",
        options=[
            discord.SelectOption(label="Holograma", value="Holograma"),
            discord.SelectOption(label="headtrick-fruit-ninja", value="headtrick-fruit-ninja"),
            discord.SelectOption(label="pack-de-sensi", value="pack-de-sensi"),
            discord.SelectOption(label="mod-menu-freefire-max", value="mod-menu-freefire-max"),
        ]
    )
    async def select_product(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.produto = select.values[0]
        await interaction.response.send_message(f"Produto: {self.produto}", ephemeral=True)

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cliente:
            return await interaction.response.send_message("selecione o cliente primeiro!", ephemeral=True)
        if not self.produto:
            return await interaction.response.send_message("selecione a opção primeiro!", ephemeral=True)

        canal = bot.get_channel(ID_CANAL_COMPRAS)
        msg_cargo = ""

        if isinstance(self.cliente, discord.Member):
            role = interaction.guild.get_role(ID_CARGO_CLIENTE)
            if role:
                if role not in self.cliente.roles:
                    await self.cliente.add_roles(role)
                    msg_cargo = "\nCargo cliente adicionado!"
            else:
                msg_cargo = "\n(Erro: ID do cargo de cliente não encontrado)"

        if canal:
            embed = discord.Embed(title="🛒 COMPRA EFETUADA!", color=0x00FF00)
            embed.description = (
                f"{self.cliente.mention} COMPRA EFETUADA!\n\n"
                f"{self.cliente.mention} Comprou o item: **{self.produto}**\n"
                f"Obrigado pela compra! {msg_cargo}"
            )
            await canal.send(content=self.cliente.mention, embed=embed)
            await interaction.response.send_message("✅ Feito!", ephemeral=True)
        else:
            await interaction.response.send_message("Erro: Canal de compras não configurado!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot ligado como {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(interaction: discord.Interaction):
    await interaction.response.send_message(view=PainelVendas(), ephemeral=True)

# Inicialização
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    if token:
        bot.run(token)
    else:
        print("ERRO: Você não configurou o TOKEN no Secrets (Cadeado)!")
