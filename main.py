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

# IDs (Colocados como texto para evitar erro de processamento de números grandes)
ID_CANAL = "1467715175372165232" 
ID_CARGO = "0000000000000000000" # TROQUE PELO ID DO CARGO

class PainelVendas(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cliente = None
        self.produto = None

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Selecionar Cliente")
    async def select_user(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        self.cliente = select.values[0]
        await interaction.response.send_message(f"Selecionado: {self.cliente.mention}", ephemeral=True)

    @discord.ui.select(
        placeholder="Selecionar Produto",
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
        # RESPOSTA IMEDIATA PARA EVITAR "INTERAÇÃO FALHOU"
        await interaction.response.defer(ephemeral=True)

        if not self.cliente or not self.produto:
            return await interaction.followup.send("Selecione o cliente e o produto!", ephemeral=True)

        try:
            # Busca o canal de forma forçada usando o ID que você mandou
            canal = await bot.fetch_channel(int(ID_CANAL))
            
            # Tenta dar o cargo
            msg_cargo = ""
            try:
                cargo_obj = interaction.guild.get_role(int(ID_CARGO))
                if cargo_obj:
                    await self.cliente.add_roles(cargo_obj)
                    msg_cargo = "\n✅ Cargo entregue!"
            except:
                msg_cargo = "\n❌ Erro ao dar cargo (verifique a hierarquia)."

            embed = discord.Embed(title="🛒 NOVA VENDA", color=0x00FF00)
            embed.add_field(name="Comprador", value=self.cliente.mention)
            embed.add_field(name="Produto", value=self.produto)
            embed.description = msg_cargo

            await canal.send(embed=embed)
            await interaction.followup.send("✅ Finalizado com sucesso!", ephemeral=True)

        except Exception as e:
            print(f"ERRO NO CONSOLE: {e}")
            await interaction.followup.send(f"Erro técnico: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot logado como {bot.user}")

@bot.tree.command(name="compra", description="Abrir painel")
async def compra(interaction: discord.Interaction):
    await interaction.response.send_message(view=PainelVendas(), ephemeral=True)

keep_alive()
bot.run(os.environ.get('TOKEN'))
