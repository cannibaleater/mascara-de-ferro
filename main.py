import discord
from discord.ext import commands
from discord import ButtonStyle, TextStyle, Interaction

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Necessário para gerenciar membros

bot = commands.Bot(command_prefix="!", intents=intents)

class FormModal(discord.ui.Modal, title="Formulário de Verificação"):
    nome = discord.ui.TextInput(label="Quem você conhece?", style=TextStyle.short)
    pergunta = discord.ui.TextInput(label="Quanto é (2x2)^3 + 23x4 ?", style=TextStyle.short)

    def __init__(self, user, canal_formulario_id, cargo_id):
        super().__init__()
        self.user = user
        self.canal_formulario_id = canal_formulario_id
        self.cargo_id = cargo_id

    async def on_submit(self, interaction: Interaction):
        canal = interaction.client.get_channel(self.canal_formulario_id)
        if not canal:
            await interaction.response.send_message("Erro: canal de formulário não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(title="Novo Formulário de Verificação",
                              description=f"**Usuário:** {self.user.mention}",
                              color=0x2f3136)
        embed.add_field(name="Quem você conhece?", value=self.nome.value, inline=False)
        embed.add_field(name="Resultado?", value=self.pergunta.value, inline=False)

        view = ActionView(self.user, self.cargo_id)
        await canal.send(content=self.user.mention, embed=embed, view=view)
        await interaction.response.send_message("Formulário enviado com sucesso!", ephemeral=True)

class ActionView(discord.ui.View):
    def __init__(self, user, cargo_id):
        super().__init__(timeout=None)
        self.user = user
        self.cargo_id = cargo_id

    @discord.ui.button(label="Aprovar", style=ButtonStyle.success)
    async def approve(self, interaction: Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user.id)
        cargo = guild.get_role(self.cargo_id)

        if member and cargo:
            try:
                await member.add_roles(cargo, reason="Aprovado na verificação")
                await interaction.response.send_message(f"{self.user.mention} foi aprovado ✅ e recebeu o cargo {cargo.mention}.")
            except discord.Forbidden:
                await interaction.response.send_message("Não tenho permissão para atribuir este cargo.", ephemeral=True)
        else:
            await interaction.response.send_message("Erro ao localizar usuário ou cargo.", ephemeral=True)

    @discord.ui.button(label="Recusar", style=ButtonStyle.danger)
    async def reject(self, interaction: Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user.id)

        if member:
            try:
                await member.kick(reason="Recusado no formulário de verificação")
                await interaction.response.send_message(f"{self.user.mention} foi recusado ❌ e removido do servidor.")
            except discord.Forbidden:
                await interaction.response.send_message("Não tenho permissão para expulsar este membro.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Erro ao expulsar: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado no servidor.", ephemeral=True)

class OpenFormView(discord.ui.View):
    def __init__(self, user, canal_formulario_id, cargo_id):
        super().__init__(timeout=None)
        self.user = user
        self.canal_formulario_id = canal_formulario_id
        self.cargo_id = cargo_id

    @discord.ui.button(label="Abrir", style=discord.ButtonStyle.primary)
    async def open_button(self, interaction: Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Você não pode abrir o formulário de outra pessoa.", ephemeral=True)
            return
        await interaction.response.send_modal(FormModal(self.user, self.canal_formulario_id, self.cargo_id))

@bot.command(name="vf")
async def vf(ctx, id_canal_embed: int, id_cargo: int, id_canal_formulario: int):
    canal = bot.get_channel(id_canal_embed)
    if not canal:
        await ctx.send("Canal de embed não encontrado.")
        return

    embed = discord.Embed(
        title="Verificação",
        description="Clique no botão abaixo para abrir o formulário de verificação.",
        color=0x5865f2
    )
    view = OpenFormView(ctx.author, id_canal_formulario, id_cargo)
    await canal.send(embed=embed, view=view)
    await ctx.send("Painel enviado com sucesso!", delete_after=5)

bot.run("MTM5MDA2NDExNDg3MjYxNTAwMg.GpuevA.tt_cwaTf6qF1VI8qep0rXlJP-UIQntJV50H-B")
