import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- VIVO ---
app = Flask('')
@app.route('/')
def home(): return "Online"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CONFIGURAÇÃO FÁCIL
NOME_DO_CANAL = "compras🛒"  # <-- ESCREVA O NOME EXATO DO CANAL AQUI
ID_CARGO_CLIENTE = 000000000000000000  # Troque pelo ID do cargo

class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="[Selecionar Cliente]")
    async def select_user(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        self.cliente = select.values[0]
        await interaction.response.send_message(f"Selecionado: {self.cliente.mention}", ephemeral=True)

    @discord.ui.select(
        placeholder="[Selecionar Xit]",
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

    @discord.ui.button(label="Confirmar Compra", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Resposta imediata para o Discord não dar erro de "Interação Falhou"
        await interaction.response.defer(ephemeral=True)

        if not self.cliente or not self.produto:
            return await interaction.followup.send("Selecione o cliente e o produto!", ephemeral=True)

        # BUSCA O CANAL PELO NOME
        canal = discord.utils.get(interaction.guild.channels, name=NOME_DO_CANAL)
        
        if canal is None:
            return await interaction.followup.send(f"❌ Erro: Não achei um canal chamado `{NOME_DO_CANAL}`", ephemeral=True)

        # TENTA DAR O CARGO
        msg_cargo = ""
        role = interaction.guild.get_role(ID_CARGO_CLIENTE)
        if role:
            try:
                await self.cliente.add_roles(role)
                msg_cargo = "\n✅ Cargo de cliente entregue!"
            except:
                msg_cargo = "\n⚠️ Sem permissão para dar cargo (arraste o cargo do bot para o topo)."

        # ENVIA A MENSAGEM
        embed = discord.Embed(title="🛒 NOVA VENDA", color=0x2ecc71)
        embed.add_field(name="👤 Cliente", value=self.cliente.mention)
        embed.add_field(name="📦 Produto", value=f"`{self.produto}`")
        embed.description = msg_cargo
        
        try:
            await canal.send(embed=embed)
            await interaction.followup.send("✅ Compra registrada!", ephemeral=True)
        except:
            await interaction.followup.send("❌ O bot não tem permissão para escrever nesse canal!", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot Online como {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel")
async def compra(interaction: discord.Interaction):
    await interaction.response.send_message(view=PainelVendas(), ephemeral=True)

keep_alive()
bot.run(os.environ.get('TOKEN'))
