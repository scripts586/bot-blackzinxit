import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- MANTÉM O BOT VIVO (RENDER/REPLIT) ---
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

# IDs CONFIGURADOS
ID_CANAL_COMPRAS = 1467715175372165232  # Seu ID atualizado
ID_CARGO_CLIENTE = 000000000000000000  # <--- COLOQUE O ID DO CARGO AQUI

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
        placeholder="[Xit👾]",
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
            return await interaction.response.send_message("Selecione o cliente primeiro!", ephemeral=True)
        if not self.produto:
            return await interaction.response.send_message("Selecione a opção xit primeiro!", ephemeral=True)

        msg_cargo = ""
        
        # Tenta dar o cargo
        if isinstance(self.cliente, discord.Member):
            role = interaction.guild.get_role(ID_CARGO_CLIENTE)
            if role:
                try:
                    if role not in self.cliente.roles:
                        await self.cliente.add_roles(role)
                        msg_cargo = "\nCargo cliente adicionado!"
                except:
                    msg_cargo = "\n(Erro: Sem permissão para dar cargo)"
            else:
                msg_cargo = "\n(Erro: ID do cargo não encontrado)"

        # Tenta enviar a mensagem no canal (Usando fetch para não falhar)
        try:
            canal = await bot.fetch_channel(ID_CANAL_COMPRAS)
            embed = discord.Embed(title="🛒 COMPRA EFETUADA!", color=0x00FF00)
            embed.description = (
                f"{self.cliente.mention} COMPRA EFETUADA!\n\n"
                f"{self.cliente.mention} Comprou o painel **{self.produto}**\n"
                f"Obrigado pela compra! {msg_cargo}"
            )
            await canal.send(content=self.cliente.mention, embed=embed)
            await interaction.response.send_message("✅ Registro enviado com sucesso!", ephemeral=True)
        except Exception as e:
            print(f"Erro ao achar canal: {e}")
            await interaction.response.send_message(f"Erro ao enviar no canal: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(interaction: discord.Interaction):
    await interaction.response.send_message(view=PainelVendas(), ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    bot.run(token)
