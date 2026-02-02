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

# IDs CONFIGURADOS (Mude apenas o ID_CARGO_CLIENTE agora)
ID_CANAL_COMPRAS = 1467715175372165232 
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
        # Evita o erro de "Interação falhou" dando 15min de tempo pro bot agir
        await interaction.response.defer(ephemeral=True)

        if not self.cliente or not self.produto:
            return await interaction.followup.send("❌ Selecione o cliente e o xit antes!", ephemeral=True)

        msg_cargo = ""
        
        # 1. Lógica do Cargo
        if isinstance(self.cliente, discord.Member):
            role = interaction.guild.get_role(ID_CARGO_CLIENTE)
            if role:
                try:
                    await self.cliente.add_roles(role)
                    msg_cargo = "\n✅ Cargo cliente adicionado!"
                except Exception as e:
                    msg_cargo = f"\n⚠️ Erro de permissão no cargo: {e}"
            else:
                msg_cargo = "\n⚠️ ID do cargo de cliente não configurado."

        # 2. Envio para o Canal de Compras
        try:
            # Força o bot a buscar o canal pelo ID que você passou
            canal = await bot.fetch_channel(ID_CANAL_COMPRAS)
            
            embed = discord.Embed(title="🛒 COMPRA REALIZADA!", color=0x2ecc71)
            embed.set_thumbnail(url=self.cliente.display_avatar.url)
            embed.add_field(name="👤 Cliente:", value=self.cliente.mention, inline=False)
            embed.add_field(name="📦 Produto/Xit:", value=f"`{self.produto}`", inline=False)
            embed.add_field(name="ℹ️ Status:", value=f"Finalizado com sucesso {msg_cargo}", inline=False)
            embed.set_footer(text="Sistema de Vendas Automatizado")

            await canal.send(content=self.cliente.mention, embed=embed)
            await interaction.followup.send("✅ Compra registrada e enviada para o canal!", ephemeral=True)
            
        except Exception as e:
            print(f"Erro no canal: {e}")
            await interaction.followup.send(f"❌ Erro ao enviar no canal: O ID é inválido ou o bot não tem permissão para ver o canal.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"--- BOT ONLINE ---")
    print(f"Logado como: {bot.user}")
    print(f"ID do Canal: {ID_CANAL_COMPRAS}")

@bot.tree.command(name="compra", description="Abrir painel de vendas")
async def compra(interaction: discord.Interaction):
    await interaction.response.send_message(view=PainelVendas(), ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('TOKEN')
    if token:
        bot.run(token)
    else:
        print("ERRO: Configure o TOKEN no Secrets (Cadeado).")
