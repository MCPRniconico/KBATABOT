import discord
from discord import app_commands
from discord.ext import commands
import json
import datetime
import os
from discord import app_commands, Interaction, Embed

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TOKEN = "TOKEN"
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


intents = discord.Intents.default()
intents.message_content = True


@client.event
async def on_ready():
    print('ログインしました')

    await client.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='BETA版です'))
    # スラッシュコマンドを同期
    await tree.sync()


@tree.command(name='info', description='BOTの情報を表示します')
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message('開発者<:DEV:1267440009452064829><@1002132268736856136> 開発協力者<:ACCDEV:1267440500625903618> <@1032649313165258772> バージョン<:BE:1267439343882993734><:TA:1267439331069657119>v1', ephemeral=True)

@tree.command(name='emoji', description='BOTに搭載されている絵文字をすべて表示します')
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message('搭載絵文字 <:partner:1267440895037542471> <:ACCDEV:1267440500625903618> <:DEV:1267440009452064829> <:BE:1267439343882993734> <:TA:1267439331069657119> <:B_:1267438603718627378> <:mukou:1267467191142322216>', ephemeral=True)

@tree.command(name='botid', description='BOTのIDなどの情報を表示します')
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message('<:mukou:1267467191142322216>このコマンドを実行する権限がありません ', ephemeral=True)

@tree.command(name="ticket", description="チケットを作成")
@discord.app_commands.default_permissions(
    administrator=True
)
async def create_ticket(interaction: discord.Interaction):
    channel = client.get_channel(interaction.channel_id)
    embed = discord.Embed(
                title="",
                color=0x178CE6,
                description="",                
        )
    embed.set_footer(text="Made by Spicy │2024/07/30")
    embed.add_field(name="チケット",value="お問い合わせはこちらからチケットを発行してください！")
    await channel.send(embed=embed)
    # チケット作成ボタンの表示
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.primary, label="チケットを作成", custom_id="create_ticket")
    view.add_item(button)
    await interaction.channel.send("", view=view)

ticket_owners = {}

@client.event
async def on_interaction(inter: discord.Interaction):
    try:
        custom_id = inter.data.get("custom_id")
        if custom_id == "create_ticket":
            # Handle ticket creation
            server = inter.guild

            # Check if the user already has a ticket
            if inter.user.id in ticket_owners.values():
                await inter.response.send_message("既にチケットが存在します。", ephemeral=True)
                return

            # Create a private channel
            overwrites = {
                server.default_role: discord.PermissionOverwrite(read_messages=False),
                server.me: discord.PermissionOverwrite(read_messages=True),
                inter.user: discord.PermissionOverwrite(read_messages=True)
            }
            channel_name = f"チケット-{inter.user.name}"
            channel = await server.create_text_channel(name=channel_name, overwrites=overwrites)

            ticket_owners[channel.id] = inter.user.id

            await channel.send(f"{inter.user.mention} チケットが作成されました!")

            ticket_message = f"チケットが作成されました！\n{channel.mention}"

            await inter.response.send_message(ticket_message, ephemeral=True)

            # Display delete button in the ticket channel
            view = discord.ui.View()
            button = discord.ui.Button(style=discord.ButtonStyle.danger, label="チケットを削除", custom_id="delete_ticket")
            view.add_item(button)
            await channel.send("", view=view)

        elif custom_id == "delete_ticket":
            # Handle ticket deletion
            channel = inter.channel

            # Delete the ticket channel
            await channel.delete()

            # Remove the ticket owner from the dictionary
            if channel.id in ticket_owners:
                del ticket_owners[channel.id]

    except Exception as e:
        print(f"An error occurred: {e}")


@bot.event
async def on_ready():
    print("Bot is ready")
    await tree.sync(guild=discord.Object(id=1260549847602302976))

# クールダウンの管理
if os.path.exists("lastcall.json"):
    with open("lastcall.json", "r") as f:
        lastcall = json.load(f)
else:
    lastcall = {"lastcall": 0}

@tree.command(name="call", description="募集します")
@app_commands.describe(内容="募集に表示するメッセージ")
async def call(interaction: discord.Interaction, 内容: str = None):
    await interaction.response.defer()
    current_time = datetime.datetime.now().timestamp()
    
    if lastcall["lastcall"] < current_time - 3600:
        embed = discord.Embed(title="募集", description="", color=discord.Color.green())
        if 内容 is not None:
            embed.description = 内容
        embed.set_author(name="募集者", icon_url=interaction.user.avatar.url)
        await interaction.followup.send(
            allowed_mentions=discord.AllowedMentions(roles=True),
            content=f"<@&1238062718825791590>",
            embed=embed
        )
        
        lastcall["lastcall"] = current_time
        with open("lastcall.json", "w") as f:
            json.dump(lastcall, f)
    else:
        remaining_time = 3600 - (current_time - lastcall["lastcall"])
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        await interaction.followup.send(
            f"1時間に1回しか募集できません。あと {minutes} 分 {seconds} 秒 待ってください。",
            ephemeral=True
        )




client.run("TOKEN")
