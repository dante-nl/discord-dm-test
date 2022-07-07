# Gradient from #40c9ff to #e81cff rotated 150 degrees
import asyncio
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_components import wait_for_component
from discord_slash import ComponentContext
from datetime import datetime
import os
import re
import sys
import json
import time
import random

intents = discord.Intents(messages=True, guilds=True)
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True)
guild_ids = [803639880391065623, 869959165139910736]
# 803639880391065623 (1): Bot Runtime Environment
# 869959165139910736 (2): Ask! Discord
bad_words = ["balls", "arsehole", "asshole",
			 "bullshit", "bitch", "son of a bitch", "bollocks", 
			 "tit", "butt", "twat", "pussy", "cock", "dickhead", "dick", 
			 "bastard", "fuck", "motherfucker", "wanker", "cunt", "sex", "penis", "boob"]

ask_blue = 0x70D7FF
ask_magenta = 0xED47FF
green = 0x17B890
red = 0xF02D3A
orange = 0xF06543


class bcolors:
	LOG = '\033[95m'
	INFO = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

askquestion = [
	create_button(
		style=ButtonStyle.green,
		label="Ask my question!"
	)
]
action_row1 = create_actionrow(*askquestion)

question_options = [
	create_button(
		style=ButtonStyle.red,
		label="Report question",
		custom_id="report",
	),
	create_button(
		style=ButtonStyle.gray,
		label="Send a message with raw ID",
		custom_id="new_raw",
	),
	create_button(
		style=ButtonStyle.gray,
		label="Remove question",
		custom_id="remove",
	)
]
action_row2 = create_actionrow(*question_options)

sendanswer = [
	create_button(
		style=ButtonStyle.green,
		label="Send my answer!"
	)
]
action_row3 = create_actionrow(*sendanswer)

report_in_dm = [
	create_button(
		style=ButtonStyle.green,
		label="Mark best answer",
		custom_id="mark_best"
	),
	create_button(
		style=ButtonStyle.red,
		label="Report question",
		custom_id="report_in_dm"
	)
]
action_row4 = create_actionrow(*report_in_dm)

remove_and_report_answer = [
	create_button(
		style=ButtonStyle.red,
		label="Report answer",
		custom_id="report_answer",
	),
	create_button(
		style=ButtonStyle.gray,
		label="Remove answer",
		custom_id="remove_answer",
	)
]

action_row5 = create_actionrow(*remove_and_report_answer)

untrust_person = [
	create_button(
		style=ButtonStyle.red,
		label="Revoke status as trusted person",
		custom_id="untrust_user"
	)
]
action_row6 = create_actionrow(*untrust_person)

# Random new ID
def get_string():
	"""Returns a random string of 5 characters, containing two numbers and three letters."""
	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
			'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

	letter_id = None
	id_list = []

	for letter in range(1, 3 + 1):
			random_letter = random.choice(letters)
			if letter_id != None:
				letter_id = random_letter + letter_id
			else:
				letter_id = random_letter

	for letter in letter_id:
		id_list.append(letter)

	number_id = None
	for number in range(1, 2 + 1):
		random_number = str(random.choice(numbers))
		if number_id != None:
			number_id = random_number + number_id
		else:
			number_id = random_number

	for number in number_id:
		id_list.append(number)

	random.shuffle(id_list)

	return "".join(id_list)

# Check if user is banned from using Ask!
def is_banned(user_id, data_string):
	"""Takes the user's ID and the data.json and checks if the user is banned from using Ask!. Returns `False` if not banned, and `True` if the user is banned"""
	user_data = data_string["user_data"]
	try:
		if user_data[str(user_id)]["banned"] == "true":
			return True
		else:
			return False
	except KeyError:
		return False

# Check if string contains URL
def has_url(string):
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	url = re.findall(regex, string)
	if url:
		return True
	else:
		return False

# Check if string contains bad words
def check_bad_words(string):
	for word in string.casefold().split():
		if word in bad_words:
			return True
		else:
			return False

# Get current time
def current_time():
	"""Returns the current time in hour:minute:seconds (24 hour time)"""
	return datetime.now().strftime("%H:%M:%S")


def restart_bot():
	"""Restarts the bot"""
	os.execv(sys.executable, ['python'] + sys.argv)

@client.event
async def on_connect():
	print(f"{bcolors.OKCYAN}[{current_time()}] Ask! is now connected to Discord.{bcolors.END}")

@client.event
async def on_ready():
	print(f"{bcolors.OKGREEN}[{current_time()}] Ask! is ready to use! :D{bcolors.END}")
	if os.path.exists("ASK_SEND_STATUS_MESSAGE.txt") == True:
		channel = client.get_channel(870225556782870569)
		embed = discord.Embed(color=green, title="An intended restart was completed", description="Ask! is back online! Any changes made to slash commands (e.g. a new one) will roll out to every server within the next hour or so.")
		await channel.send(embed=embed, content=None)
		os.remove("ASK_SEND_STATUS_MESSAGE.txt")

@client.event
async def on_disconnect():
	print(f"{bcolors.FAIL}[{current_time()}] Connection to Discord lost.{bcolors.END}")

@client.event
async def on_resume():
	print(f"{bcolors.OKCYAN}[{current_time()}] Session resumed.{bcolors.END}")

@client.event
async def on_guild_join(guild):
	print(f"{bcolors.INFO}[{current_time()}] Joined {guild.name}{bcolors.END}")
	channel = client.get_channel(971041984003321917)
	embed = discord.Embed(color=green, title="Ask! joined a new guild!", description=f"Ask! joined {guild.name}!")
	await channel.send(embed=embed, content=None)

@client.event
async def on_guild_remove(guild):
	print(f"{bcolors.INFO}[{current_time()}] Left {guild.name}{bcolors.END}")
	channel = client.get_channel(971041984003321917)
	embed = discord.Embed(color=red, title="Ask! left a guild!", description=f"Ask! left {guild.name}!")
	await channel.send(embed=embed, content=None)

@slash.slash(name="ping", description="Gives you the current ping")
async def _ping(ctx):
	if round(client.latency*1000) <= 150:
		clr = green
	elif round(client.latency*1000) <= 200:
		clr = orange
	else:
		clr = red
	embed = discord.Embed(title=f"{round(client.latency*1000)}ms", description=f"The current ping of Ask! is {round(client.latency*1000)}ms", color=clr)
	await ctx.send(embed=embed, content=None, hidden=True)


@slash.slash(name="my-supercharges", description="View how many Supercharges you have!")
async def _my_supercharges(ctx):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	
	
	try:
		data["user_data"][str(ctx.author.id)]
	except KeyError:
		data["user_data"][str(ctx.author.id)] = {}

	try:
		data["user_data"][str(ctx.author.id)]["supercharges"]
	except KeyError:
		data["user_data"][str(ctx.author.id)]["supercharges"] = 0

	supercharges = data["user_data"][str(ctx.author.id)]["supercharges"]
	if supercharges == 0:
		embed = discord.Embed(color=red, title="You don't have any Supercharges!", description="Unfortunately, you do not have any Supercharges at the moment! However, you can get them [here](https://ask-bot.gq/supercharges/)!")
		await ctx.send(embed=embed, content=None, hidden=True)
	elif supercharges == 1:
		embed = discord.Embed(color=ask_blue, title=f"You have {supercharges} Supercharge!", description="If you would like to purchase more, you can click [here](https://ask-bot.gq/supercharges/)! To Supercharge a question, just do `/supercharge id:`!")
		await ctx.send(embed=embed, content=None, hidden=True)
	else:
		embed = discord.Embed(color=ask_blue, title=f"You have {supercharges} Supercharges!", description="If you would like to purchase more, you can click [here](https://ask-bot.gq/supercharges/)! To Supercharge a question, just do `/supercharge id:`!")
		await ctx.send(embed=embed, content=None, hidden=True)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))


@slash.slash(name="supercharge",
             description="Supercharge a question!",
             options=[
                 create_option(
                     name="id",
                     description="The ID of the question you want to Supercharge! Is above question.",
                     option_type=3,
                     required=True
                 )
             ])
async def _supercharge(ctx, id: str):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	
	try:
		if data["data"][id]["deleted"] == "true":		
			embed = discord.Embed(color=red, title="Error", description="This question has been deleted by the author or a moderator. This means this question can not be Supercharged.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return
	except:
		pass

	try:
		data["user_data"][str(ctx.author.id)]
	except KeyError:
		data["user_data"][str(ctx.author.id)] = {}

	try:
		data["user_data"][str(ctx.author.id)]["supercharges"]
	except KeyError:
		data["user_data"][str(ctx.author.id)]["supercharges"] = 0

	supercharges = data["user_data"][str(ctx.author.id)]["supercharges"]
	if supercharges == 0:
		embed = discord.Embed(color=red, title="You don't have any Supercharges!", description="Unfortunately, you do not have any Supercharges at the moment! However, you can get them [here](https://ask-bot.gq/supercharges/)!")
		await ctx.send(embed=embed, content=None, hidden=True)
	else:
		try:
			data["data"][id]
		except KeyError:
			embed = discord.Embed(color=red, title="Error",
							description="That is not a valid ID. Please make sure that the ID you filled in has the correct casing, aBc instead of for example ABC and make sure the question you are trying to edit exists.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		if data["data"][id]["author_id"] != str(ctx.author.id):
			embed = discord.Embed(color=orange, title="That's not your question!", description=f"Are you sure you want to Supercharge a question by {data['data'][id]['author']}?")
			confirm_charge_exotic_author = [
				create_button(
					style=ButtonStyle.gray,
					label="Yes, continue"
				)
			]
			confirm_charge_exotic_author_btn = create_actionrow(*confirm_charge_exotic_author)

			await ctx.send(embed=embed, content=None, hidden=True, components=[confirm_charge_exotic_author_btn])
			button_ctx: ComponentContext = await wait_for_component(client, components=confirm_charge_exotic_author_btn)
			embed = discord.Embed(color=green, title="Continuing Supercharge process!", description=f"You confirmed that you wanted to Supercharge a question by {data['data'][id]['author']}")
			await button_ctx.edit_origin(embed=embed, content=None, components=None)
		
		embed = discord.Embed(title="Supercharge question?", description=f"Are you that you want to Supercharge that question? You will have {supercharges-1} Supercharge(s) after that!", color=ask_blue)
		confirm_charge = [
				create_button(
					style=ButtonStyle.green,
					label="Supercharge this question!"
				)
			]
		confirm_charge_btn = create_actionrow(*confirm_charge)
		await ctx.send(embed=embed, content=None, hidden=True, components=[confirm_charge_btn])
		button_ctx: ComponentContext = await wait_for_component(client, components=confirm_charge_btn)
		data["data"][id]["supercharged"] = "true"
		data["user_data"][str(ctx.author.id)]["supercharges"] -= 1
		embed = discord.Embed(color=green, title="Question Supercharged!", description=f"You Supercharged a question with ID {id}! The question is Supercharged to the top of the Question Browser!")
		send_charge_receipt= [
				create_button(
					style=ButtonStyle.gray,
					label="DM me a receipt"
				)
			]
		send_charge_receipt_btn = create_actionrow(*send_charge_receipt)
		await button_ctx.edit_origin(embed=embed, content=None, hidden=True, components=[send_charge_receipt_btn])
		button_ctx: ComponentContext = await wait_for_component(client, components=send_charge_receipt_btn)

		try:
			embed = discord.Embed(color=green, title="Question Supercharged!", description=f"""
A question with ID {id} was Supercharged on <t:{int(time.time())}:F>. Full receipt:
```AskReceipt
——————————————————————————————
1x Ask! Supercharge

Time:      {datetime.utcnow()} UTC
Purchaser: {ctx.author.id} ({ctx.author.name}#{ctx.author.discriminator})
——————————————————————————————
```
""")
			user = await client.fetch_user(ctx.author.id)
			await user.send(embed=embed, content=None)
			await button_ctx.edit_origin(content="Your receipt was send!", components=None)
		except:
			embed =  discord.Embed(color=red, title="Your DMs are closed!", description="A direct message could not be send to you because your DMs are closed.")
			await button_ctx.send(embed=embed, content=None, hidden=True)


	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))

		

@slash.slash(name="toggle-dms", description="Enable or disable if Ask! should DM you.")
async def _toggle_dms(ctx):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		data["user_data"]
	except KeyError:
		data["user_data"] = {}

	try:
		data["user_data"][str(ctx.author.id)]
	except KeyError:
		data["user_data"][str(ctx.author.id)] = {}

	try:
		data["user_data"][str(ctx.author.id)]["dms_enabled"]
	except KeyError:
		data["user_data"][str(ctx.author.id)]["dms_enabled"] = "true"

	if data["user_data"][str(ctx.author.id)]["dms_enabled"] == "true":
		data["user_data"][str(ctx.author.id)]["dms_enabled"] = "false"
		embed = discord.Embed(title="DMs disabled",
		                      description=f"Ask! will no longer attempt to send direct messages to you.", color=green)
		await ctx.send(embed=embed, content=None, hidden=True)
	elif data["user_data"][str(ctx.author.id)]["dms_enabled"] == "false":
		data["user_data"][str(ctx.author.id)]["dms_enabled"] = "true"
		embed = discord.Embed(title="DMs enabled",
		                      description=f"Ask! will attempt to send direct messages to you.", color=green)
		await ctx.send(embed=embed, content=None, hidden=True)
	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))


@slash.slash(name="help", description="Need a little help?")
async def _help(ctx):
	select = create_select(
		custom_id="help_menu",
		options=[  # the options in your dropdown
			create_select_option("Supercharges", value="supercharges"),
			create_select_option("/answer", value="answer"),
			create_select_option("/ask", value="ask"),
			create_select_option("/create-question", value="create-question"),
			create_select_option("/edit", value="edit"),
			create_select_option("/help", value="help"),
			create_select_option("/mydata", value="mydata"),
			create_select_option("/ping", value="ping"),
			create_select_option("/toggle-dms", value="toggle-dms"),
		],
		# the placeholder text to show when no options have been chosen
		placeholder="Select a command",
		min_values=1,  # the minimum number of options a user must select
		max_values=1,  # the maximum number of options a user can select
	)

	# like action row with buttons but without * in front of the variable
	embed = discord.Embed(title="Help menu", description="""Ask! has various features, but they are mainly for asking and responding questions. 
You can select a command from the dropdown menu below to learn more about them. (**Note:** You can scroll down)

**Links**
:heavy_plus_sign:: **[Invite Ask!](https://ask-bot.gq/invite)**
<:Ask:877256054638018570>: [Ask! Website](https://ask-bot.gq)
:link:: [Ask! Discord server](https://discord.gg/YNPcH27Wfj)
""", color=ask_blue)
	await ctx.send(content=None, components=[create_actionrow(select)], hidden=True, embed=embed)


@slash.slash(name="ask",
			 description="Ask a question. Can be answered in the official server.",
			 options=[
				 create_option(
					 name = "question",
					 description = "The question you want to ask",
					 option_type = 3,
					 required = True
				 )
			 ])

async def _ask(ctx, question: str):
	# Check for URL
	if has_url(question):
		embed = discord.Embed(color=red, title="You can not send URLs", description="URLs are blocked so things like IP grabbers can't be send, but also to prevent self promotion. Bypassing this filter will result in a ban")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report", description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{question}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return
	# Check for bad words
	if check_bad_words(question):
		embed = discord.Embed(color=red, title="You can not send bad words",
							  description="Your message contained bad words, due to obvious reasons, they are blocked")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report",
							  description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{question}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	if len(question) > 256:
		embed = discord.Embed(color=red, title="Error",
						description=f"The maximum lenght for questions is 256 characters. Your question has {len(question)} characters.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	id = get_string()

	embed = discord.Embed(title=f"{question}", color=ask_blue, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
	
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	embed.set_author(name=id)
	components = [
			create_button(
				style=ButtonStyle.green,
				label="Ask my question!",
				custom_id=f"ask_question_{ctx.author.id}"
			),
			create_button(
				style=ButtonStyle.blurple,
				label="Ask my question SUPERCHARGED!",
				custom_id=f"ask_question_sc_{ctx.author.id}"
			)
	]
	action_row = create_actionrow(*components)
	msg = await ctx.send(content="**Preview**", embed=embed, hidden=True, components=[action_row])

	button_ctx: ComponentContext = await wait_for_component(client, components=action_row)

	if button_ctx.custom_id == f"ask_question_sc_{ctx.author.id}":
		try:
			data["user_data"][str(ctx.author.id)]
		except KeyError:
			data["user_data"][str(ctx.author.id)] = {}

		try:
			data["user_data"][str(ctx.author.id)]["supercharges"]
		except KeyError:
			data["user_data"][str(ctx.author.id)]["supercharges"] = 0

		supercharges = data["user_data"][str(ctx.author.id)]["supercharges"]
		if supercharges == 0:
			embed = discord.Embed(color=red, title="You don't have any Supercharges!",
								description="Unfortunately, you do not have any Supercharges at the moment! However, you can get them [here](https://ask-bot.gq/supercharges/)!")
			await button_ctx.edit_origin(embed=embed, content=None, hidden=True, components=None)
			return

	embed = discord.Embed(title=f"{question}", color=green, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	embed.set_author(name=id)
	author = ctx.author

	try:
		if data["user_data"][str(ctx.author.id)]["dms_enabled"] == "false":
			extra_note = "You have DMs disabled, you will not get pinged in the Ask! Discord server or a get direct message."
		else:
			extra_note = "Your DMs are enabled, so you Ask! will try to DM you when the question gets an answer. If this fails, you will be pinged in the Discord server."
	except KeyError:
		extra_note = "Your DMs are enabled, so you Ask! will try to DM you when the question gets an answer. If this fails, you will be pinged in the Discord server."
	await button_ctx.edit_origin(content=f"**Question asked! You can check it out at https://discord.gg/m25Zd4ZA6s ** \n\nYou can check it out on [the website](https://ask-bot.gq/question?id={id}). \n{extra_note}", components=None, embed=embed, hidden=True)

	channel = client.get_channel(869988765307908096)

	embed = discord.Embed(title=f"{question}", color=ask_blue, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	embed.set_author(name=f"{id}")
	msg = await channel.send(content="<a:Discord_Loading:875322034337493033> Loading question, this shouldn't take longer than a few milliseconds.")

	question_options = [
        create_button(
			style=ButtonStyle.red,
			label="Report question",
			custom_id="report",
        ),
        create_button(
			style=ButtonStyle.gray,
			label="Send a message with raw ID",
			custom_id="new_raw",
        ),
		create_button(
			style=ButtonStyle.URL,
			label="Open on Ask! website",
			url=f"https://ask-bot.gq/question?id={id}"
		),
        create_button(
			style=ButtonStyle.gray,
			label="Remove question",
			custom_id="remove",
        )
    ]

	question_action = create_actionrow(*question_options)
	await msg.edit(content=None, embed=embed, components=[question_action])
	if button_ctx.custom_id == f"ask_question_sc_{ctx.author.id}":
		data["data"].update({
				f"{id}": {
					"supercharged": "true",
					"question": f"{question}",
					"author_id": f"{author.id}",
					"message_id": f"{msg.id}",
					"author": f"{author}"
				}
			}
		)

		data["user_data"][str(ctx.author.id)]["supercharges"] -= 1
		try:
			embed = discord.Embed(color=green, title="Question Supercharged!", description=f"""
A question with ID {id} was Supercharged on <t:{int(time.time())}:F>. Full receipt:
```AskReceipt
——————————————————————————————
1x Ask! Supercharge

Time:      {datetime.utcnow()} UTC
Purchaser: {ctx.author.id} ({ctx.author.name}#{ctx.author.discriminator})
——————————————————————————————
```
""")
			user = await client.fetch_user(ctx.author.id)
			await user.send(embed=embed, content=None)
			embed = discord.Embed(color=green, title="Receipt send!", description="A receipt was send to your DMs.")
			await button_ctx.send(content="Your receipt was send!", hidden=True)
		except:
			embed =  discord.Embed(color=red, title="Your DMs are closed!", description="A direct message could not be send to you because your DMs are closed.")
			await button_ctx.send(embed=embed, content=None, hidden=True)

	else:
		data["data"].update({
				f"{id}": {
					"question": f"{question}",
					"author_id": f"{author.id}",
					"message_id": f"{msg.id}",
					"author": f"{author}"
				}
			}
		)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))

	button_ctx: ComponentContext = await wait_for_component(client, components=question_action)


@slash.slash(name="answer",
			 description="Answer a question with a Question ID (text above question)",
			 options=[
				 create_option(
					 name="id",
					 description="The Ask! ID. Is above question",
					 option_type=3,
					 required=True
				 ),

				 create_option(
					 name="answer",
					 description="The answer you want to send",
					 option_type=3,
					 required=True
				 )
			 ])
async def _answer(ctx, id: str, answer: str):
	# Check for URLs
	if has_url(answer):
		embed = discord.Embed(color=red, title="You can not send URLs",
							  description="URLs are blocked so things like IP grabbers can't be send, but also to prevent self promotion. Bypassing this filter will result in a ban")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report",
							  description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{answer}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return
	# Check for bad words
	if check_bad_words(answer):
		embed = discord.Embed(color=red, title="You can not send bad words",
							  description="Your message contained bad words, due to obvious reasons, they are blocked")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report",
							  description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{answer}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return

	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	if len(answer) > 256:
		embed = discord.Embed(color=red, title="Error",
						description=f"The maximum lenght for questions is 256 characters. Your question has {len(answer)} characters.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		data["data"][id]
	except KeyError:
		embed = discord.Embed(color=red, title="Error",
						description="That is not a valid ID. Please make sure that the ID you filled in has the correct casing, aBc instead of for example ABC and make sure the question you are trying to edit exists.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	author_id = data["data"][id]["author_id"]
	try:
		if data["user_data"][author_id]["dms_enabled"] == "false":
			dms = False
		else:
			dms = True
	except KeyError:
		dms = True

	channel = client.get_channel(869988765307908096)
	msg = await channel.fetch_message(data["data"][id]["message_id"])
	id2 = data["data"][id]["author_id"]

	user = await client.fetch_user(id2)

	if str(ctx.author.id) == str(id2):
		embed = discord.Embed(color=red, title="Error",
							  description="You can't answer your own questiions, if you want to delete your question, press the \"Remove question\" button")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	new_id = get_string()
	embed = discord.Embed(title=f"{answer}", description=f"> {msg.embeds[0].title}\n\nAnswer was submitted by {ctx.author}. If you think this answer breaks any rules, please press the report button below. Submittting a fake report may result in a punishment.", 
                       color=ask_magenta)
	embed.set_author(name=new_id)
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")

	send_answer_components = [
            create_button(
                style=ButtonStyle.green,
                label="Send my answer!",
                custom_id=f"send_answer_{time.time()}"
            )
	]
	send_answer_action_row = create_actionrow(*send_answer_components)
	
	await ctx.send(embed=embed, content="**Preview**", hidden=True, components=[send_answer_action_row])
	button_ctx: ComponentContext = await wait_for_component(client, components=send_answer_action_row)

	embed = discord.Embed(title=f"{answer}", description=f"> {msg.embeds[0].title}\n\nAnswer was submitted by {ctx.author}. If you think this answer breaks any rules, please press the report button below. Submittting a fake report may result in a punishment.",
						  color=green)
	embed.set_author(name=new_id)
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	await button_ctx.edit_origin(embed=embed, content="**Answer send!**", hidden=True, components=None)
	
	if dms == True:
		try:
			ping = None
			embed = discord.Embed(title=f"{answer}", description=f"> {msg.embeds[0].title}\n\nAnswer was submitted by {ctx.author}. If you think this answer breaks any rules, please press the report button below. Submittting a fake report may result in a punishment.",
                         color=ask_magenta)
			if ctx.author.id in data["trusted_people"]:
				embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
			else:
				embed.set_footer(text=f"{ctx.author}")
			embed.set_author(name=new_id)
			sent_message = await user.send(embed=embed, content=None, components=[action_row4])
		except:
			ping = f"<@{id2}>"
			sent_message = None
	else:
		ping = None
		sent_message = None
	channel = await client.fetch_channel(869988765307908096)
	embed = discord.Embed(title=f"{answer}", description=f"> {msg.embeds[0].title}\n\nAnswer was submitted by {ctx.author}. If you think this answer breaks any rules, please press the report button below. Submittting a fake report may result in a punishment.",
						  color=ask_magenta)
	embed.set_author(name=new_id)
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	await channel.send(embed=embed, content=ping, components=[action_row5])

	if sent_message != None:
		sent_message_id = sent_message.id
	else:
		sent_message_id = "none"

	try:
		data["data"][id]["answers"]
	except KeyError:
		data["data"][id]["answers"] = {}

	data["data"][id]["answers"][new_id] = {
		"answer": answer,
		"author_id": ctx.author.id,
		"author": f"{ctx.author.name}#{ctx.author.discriminator}",
		"message_id": sent_message_id
	}
	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))


@slash.slash(name="edit",
			 description="Edit a question via the Ask! ID (above the question)",
			 options=[
				 create_option(
					 name="id",
					 description="The Ask! ID. Is above question",
					 option_type=3,
					 required=True
				 ),

				 create_option(
					 name="new_question",
					 description="The updated question",
					 option_type=3,
					 required=True
				 )
			 ])
async def _edit(ctx, id: int, new_question: str):
	# Check for URLs
	if has_url(new_question):
		embed = discord.Embed(color=red, title="You can not send URLs",
							  description="URLs are blocked so things like IP grabbers can't be send, but also to prevent self promotion. Bypassing this filter will result in a ban")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report",
							  description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{new_question}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return
	# Check for bad words
	if check_bad_words(new_question):
		embed = discord.Embed(color=red, title="You can not send bad words",
							  description="Your message contained bad words, due to obvious reasons, they are blocked")
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(color=red, title="Automatic Report",
							  description=f"Automatic report, {ctx.author} ({ctx.author.id}) tried sending the following: \n\n{new_question}")
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)
		return

	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		if data["data"][id]["deleted"] == "true":
			embed = discord.Embed(color=red, title="Error",
							description="This question has been deleted by the author or a moderator. This means its history can not be viewed.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return
	except KeyError:
		pass			

	try:
		data["data"][id]
	except KeyError:
		embed = discord.Embed(color=red, title="Error",
						description="That is not a valid ID. Please make sure that the ID you filled in has the correct casing, aBc instead of for example ABC and make sure the question you are trying to edit exists.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	channel = client.get_channel(869988765307908096)
	msg = await channel.fetch_message(data["data"][id]["message_id"])
	id2 = data["data"][id]["author_id"]

	if str(ctx.author.id) != str(id2):
		embed = discord.Embed(color=red, title="Error",
							  description="You can only edit questions send by you, for obvious reasons")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	embed = discord.Embed(color=red, title="Automatic Report",
						  description=f"Automatic report, {ctx.author} ({ctx.author.id}) edited a message. \n\n**Original:** {msg.embeds[0].title} \n**New:** {new_question} \n\n**[Jump to question](https://discord.com/channels/869959165139910736/869988765307908096/{id})**")
	report_channel = client.get_channel(870066564714627073)
	await report_channel.send(content=None, embed=embed)

	try:
		data["data"][id]["question_history"].append(data["data"][id]["question"])
	except KeyError:
		data["data"][id]["question_history"] = [data["data"][id]["question"]]

	data["data"][id]["question"] = new_question

	if len(data["data"][id]["question_history"]) > 1:
		history_text = f'{data["data"][id]["question_history"][0]} (type `/history` to view entire history)'
	else:
		history_text = f'{data["data"][id]["question_history"][0]}'
	
	embed = discord.Embed(color=ask_blue,
		title=new_question, description=f"Original question: \n> {history_text} \n\nAsked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer`. You can also edit this question (if you are the author) by using `/edit`. This also requires the ID\n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
	if ctx.author.id in data["trusted_people"]:
		embed.set_footer(text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
	else:
		embed.set_footer(text=f"{ctx.author}")
	embed.set_author(name=id)
	await msg.edit(content=None, embed=embed)
	embed = discord.Embed(color=green, title="Question edited!", description="Your question has been edited!")
	await ctx.send(embed=embed, content=None, hidden=True)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))


@slash.slash(name="history",
             description="View the history of a question",
             options=[
                 create_option(
                     name="id",
                     description="The Ask! ID. Is above question, case sensitive",
                     option_type=3,
                     required=True
                 )
             ])

async def _history(ctx, id: int):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		data["data"][id]
	except KeyError:
		embed = discord.Embed(color=red, title="Error",
						description="That is not a valid ID. Please make sure that the ID you filled in has the correct casing, aBc instead of for example ABC and make sure the question you are trying view the history of exists.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		if data["data"][id]["deleted"] == "true":
			# // await ctx.send(content=ctx.author.roles)]
			correct_roles_found = 0
			for role in ctx.author.roles:
				if str(role.id) == "869962152428056608":
					correct_roles_found += 1
				elif str(role.id) == "869962766507724852":
					correct_roles_found += 1
				elif str(role.id) == "869962940734926858":
					correct_roles_found += 1
				# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
				# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
				# NOTE: 869962940734926858 is for the mod role in the Ask! Discord server
			if correct_roles_found == 0:
				embed = discord.Embed(color=red, title="Error",
							description="This question has been deleted by the author or a moderator. This means its history can not be viewed.")
				await ctx.send(embed=embed, content=None, hidden=True)
				return
	except:
		pass

	try:
		data["data"][id]["question_history"]
	except KeyError:
		embed = discord.Embed(color=red, title="Error",
						description="This question has not been edited yet, and so it can't have a history")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	question_number = 0
	question_list = []
	for question in data["data"][id]["question_history"]:
		question_number += 1
		question_list.append(f"[{question_number}] {question}")

	question_number += 1
	question_list.append(f"[{question_number}] {data['data'][id]['question']}")
	question_list = "\n".join(question_list)


	embed = discord.Embed(title="Question history", description=f"""Below is the question history. Number one is the oldest, number two came after that, etc.
```ask_list
{question_list}
```""", color=green)
	await ctx.send(embed=embed, content=None, hidden=True)
	

@slash.slash(name="mydata",
             description="Manage your data",
             options=[
                 create_option(
                    name="action",
                    description="What would you like to do with your data?",
                    option_type=3,
                    required=True,
                    choices=[
                        create_choice(
                            name="View",
                            value="view"
                        ),
                        create_choice(
                            name="Remove",
                            value="delete"
                        )
                    ]
                )
            ])
async def _mydata(ctx, action : str):
	with open("Python/data.json") as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error",
						description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	# Viewing a question
	if action == "view":
		embed = discord.Embed(color=ask_blue, title="Retrieving your data...", description=f"We're getting each bit of info we store about you, and things you have done. This includes things such as questions you asked, but also if you have direct messages enabled. The data will be send as a different **hidden** message in **this channel** with a file attached to it, named `{ctx.author.id}.json`. This is data will quickly be created, send and then deleted. We do not keep your data as a unique file, every bit of data is combined. \n\nIf you're interested, you can also view [Ask!'s privacy policy](https://ask-bot.gq/privacy).")
		await ctx.send(content=None, hidden=True, embed=embed)

		verified = False
		for id in data["trusted_people"]:
			if id == ctx.author.id:
				verified = True
			else:
				pass
		if verified != True:
			verified = False

		user_data = {
			"_COMMENT": "Welcome to your Ask! data!",
			"_COMMENT2": "This has every piece of data we have of you, nicely organised, and as easy to read as possible.",
			"_IMPORTANT": "This contains no data that would be considered private by most people, but IT IS NOT RECOMMENDED TO SHARE THIS!",
			"questions_asked_by_you": {},
			"answers_send_by_you": {},
			"user_data": {
				"_USER_DATA_NOTE": "This is not personal, this is mainly if you're banned and some settings."
			},
			"verified": verified,
		}

		questions_by_person = []
		answers_by_person = []
		for question in data["data"]:
			if data["data"][question]["author_id"] == str(ctx.author.id):
				questions_by_person += [question]
				user_data["questions_asked_by_you"][question] = {
					"question": data["data"][question]["question"],
					"author": data["data"][question]["author"],
					"author_id": data["data"][question]["author_id"],
					"message_id": data["data"][question]["message_id"],
					"answers": {}
				}
				try:
					user_data["questions_asked_by_you"][question].update({
						"deleted": data["data"][question]["deleted"],
						"reason_for_deletion": data["data"][question]["deleted_reason"]
					})
				except KeyError:
					pass
				try:
					for answer in data["data"][question]["answers"]:
						user_data["questions_asked_by_you"]["answers"][answer] = {
							"answer": data["data"][question]["answers"][answer]["answer"],
							"author": data["data"][question]["answers"][answer]["author"],
							"author_id": data["data"][question]["answers"][answer]["author_id"],
							"message_id": data["data"][question]["answers"][answer]["message_id"]
						}
				except KeyError:
					pass
			try:
				for answer in data["data"][question]["answers"]:
					if data["data"][question]["answers"][answer]["author_id"] == ctx.author.id:
						user_data["answers_send_by_you"][answer] = {
							"answer": data["data"][question]["answers"][answer]["answer"],
							"author": data["data"][question]["answers"][answer]["author"],
							"author_id": data["data"][question]["answers"][answer]["author_id"]
						}
						try:
							user_data["answers_send_by_you"][answer].update({
								"message_id": data["data"][question]["answers"][answer]["message_id"]
							})
						except KeyError:
							pass
			except KeyError:
				pass

		for id in data["user_data"]:
			if id == str(ctx.author.id):
				try:
					if data["user_data"][id]["dms_enabled"] == "true":
						dms = True
					else:
						dms = False
				except KeyError:
					dms = False
				try:
					if data["user_data"][id]["banned"] == "true":
						banned = True
					else:
						banned = False
				except KeyError:
					banned = False
				user_data["user_data"].update({
					"dms_enabled": dms,
					"banned": banned
				})
		with open(f"{ctx.author.id}.json", 'w') as json_file:
			json.dump(user_data, json_file,
						indent=4,
						separators=(',', ': '))
		embed = discord.Embed(color=green, title="File created", description="The file with you data has been created and is attached to this message. This file will be deleted again from our storage directly after this message has been send.")
		await ctx.send(content=None, embed=embed, file=discord.File(f"{ctx.author.id}.json"), hidden=True)
		os.remove(f"{ctx.author.id}.json")

	if action == "delete":
		delete_data_button = [
			create_button(
				style=ButtonStyle.red,
				label="Remove my data"
			)
		]
		delete_data = create_actionrow(*delete_data_button)
		embed = discord.Embed(color=orange, title="Important warning", description=f"""**If you delete your data, your account will be permanently banned!**

Because Ask! stores a lot of data for moderation purposes, deleting your data, hugely interferes with our moderation abilities.
When you delete you data, the following will be completely deleted:
```AskList
— All your questions and its answers
— All your answers; as much as we can (we are not able to delete messages)
— Personal settings, e.g. if your DMs are enabled
— Your verified status
``` The only thing that we will store is just enough data to save that you are banned, so that will be your ID; your entry in [our file](https://ask.luckunstoppable.com/data.json) will look like this:
```json
"{ctx.author.id}" {{
	"banned": "true"
}}
```
""")
		await ctx.send(embed=embed, content=None, hidden=True, components=[delete_data])

		delete_data_button2 = [
			create_button(
				style=ButtonStyle.red,
				label="I know for sure I want to delete my data"
			)
		]
		delete_data2_electric_boogaloo = create_actionrow(*delete_data_button2)

		button_ctx: ComponentContext = await wait_for_component(client, components=delete_data)
		await button_ctx.edit_origin(components=[delete_data2_electric_boogaloo], content="**NO PROMPTS AFTER THIS!**")
		await wait_for_component(client, components=delete_data2_electric_boogaloo)

		questions_deleted = 0
		delete_questions = []
		delete_answers = []
		for question in data["data"]:
			if data["data"][question]["author_id"] == str(ctx.author.id):
				questions_deleted += 1
				# data["data"].pop(question)
				delete_questions.append(question)

			try:
				for answer in data["data"][question]["answers"]:
					if data["data"][question]["answers"][answer]["author_id"] == ctx.author.id:
						delete_answers.append({
							"q_id": question,
							"a_id": answer
						})
			except KeyError:
				pass

		channel = client.get_channel(869988765307908096)
		embed_answer = discord.Embed(color=red, title="Question deleted",
		                      description="This question has been deleted because the author chose to wipe their data.")
		for id_ in delete_questions:
			data["data"].pop(id_)
			try:
				question = await channel.fetch_message(int(data["data"][id_]["message_id"]))
				question.edit(embed=embed_answer, content=None, components=[])
			except KeyError:
				pass

		for answer in delete_answers:
			question_id = answer["q_id"]
			answer_id = answer["a_id"]
			data["data"][question_id]["answers"].pop(answer_id)

		for id_ in data["trusted_people"]:
			if id_ == ctx.author.id:
				data["trusted_people"].remove(ctx.author.id)
				break
		
		for person in data["user_data"]:
			if person == str(ctx.author.id):
				data["user_data"].pop(str(ctx.author.id))
				break

		embed = discord.Embed(color=ask_blue, title="Your data is removed.", description="""
Your data has been removed from the database, with the exception of your ID and your banned status set to true.
This ban is permanent and will in almost all cases not be undone. This ban means that you can not use Ask! anymore,
with the exception of some commands such as `/ping` and the help command.

**Thank you for your time with Ask!**
""")

		data["user_data"][ctx.author.id] = {"banned": "true"}

		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))

		embed = discord.Embed(color=red, title="Data deleted", description="Your data has been deleted, and you have been banned.")
		await ctx.send(embed=embed, hidden=True)
		
			
@client.event
async def on_component(ctx: ComponentContext):
	# Send a new message with just the ID
	if ctx.custom_id == "new_raw":
		await ctx.send(content=ctx.origin_message.embeds[0].author.name, hidden=True)

	# Report question
	if ctx.custom_id == "report":
		with open("Python/data.json") as data_file:
			data = json.load(data_file)

		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
							description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		id = ctx.origin_message.embeds[0].author.name

		embed = discord.Embed(
			title="Report sent!", description="The report has been sent to our moderators! Fake reports can get you punished.", color=green)
		await ctx.send(content=None, embed=embed, hidden=True)
		embed = discord.Embed(title=f"Report submitted by {ctx.author} ({ctx.author.id})",
							  description=f"**Question:** {ctx.origin_message.embeds[0].title} \n**Question by user with ID:** {data['data'][id]['author_id']} \n\n**[Jump to question](https://discord.com/channels/869959165139910736/869988765307908096/{ctx.origin_message_id})**",
							  color=red)
		channel = client.get_channel(870066564714627073)
		await channel.send(embed=embed, content=None)

	# Remove question
	elif ctx.custom_id == "remove":
		with open("Python/data.json") as data_file:
			data = json.load(data_file)
		
		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
							description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		id = ctx.origin_message.embeds[0].author.name
		if ctx.author.id == int(data["data"][id]["author_id"]):
			embed = discord.Embed(color=red, title="Question deleted",
								  description="This question has been deleted by the author of this question.")
			await ctx.edit_origin(embed=embed, content=None, components=None)
			with open('Python/data.json') as data_file:
				data = json.load(data_file)
				data["data"][id].update({
					"question": f"{data['data'][id]['question']}",
					"author_id": f"{data['data'][id]['author_id']}",
					"message_id": f"none",
					"deleted": "true",
					"deleted_reason": "author"
					}
				)

			with open("Python/data.json", 'w') as json_file:
				json.dump(data, json_file, indent=4, separators=(',', ': '))
		elif ctx.author.guild_permissions.manage_messages == True:
			question = ctx.origin_message.embeds[0].title
			embed = discord.Embed(color=red, title="Question deleted",
								  description="This question has been deleted by a moderator.")
			await ctx.edit_origin(embed=embed, content=None, components=None)
			try:
				user = await client.fetch_user(data["data"][id]["author_id"])
				embed = discord.Embed(color=red, title="One of your questions has been removed by a moderator", description=f"\"{question}\" has been removed by a moderator due to violation of our rules.")
				await user.send(content=None, embed=embed)

			except:
				user = await client.fetch_user(data["data"][id]["author_id"])
				embed = discord.Embed(
					title="Notice", description=f"Could not send a DM to to {user.name} because the user has DMs disabled", color=orange)
				await ctx.send(embed=embed, content=None, hidden=True)
			with open('Python/data.json') as data_file:
				data = json.load(data_file)
				data["data"][id].update({
                    "question": f"{data['data'][id]['question']}",
					"author_id": f"{data['data'][id]['author_id']}",
					"message_id": f"none",
					"deleted": "true",
					"deleted_reason": "moderator"
                }
            )

			with open("Python/data.json", 'w') as json_file:
				json.dump(data, json_file, indent=4, separators=(',', ': '))
		else:
			embed = discord.Embed(color=red, title="Permission error", description="You are not allowed to delete this question; you can only delete your own questions!")
			await ctx.send(content=None, embed=embed, hidden=True)

	# Reporting in DM
	elif ctx.custom_id == "report_in_dm":

		id = str(ctx.origin_message.embeds[0].author.name)
		with open('Python/data.json') as data_file:
			data = json.load(data_file)

		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
							description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		question_id = None
		for question in data["data"]:
			try: 
				if data["data"][question]["answers"][id]:
					question_id = question
			except KeyError:
				pass
		if question_id == None:
			embed = discord.Embed(color=red, title="Error",
							description=f"No answer with this ID ({id}) could be found!")
			await ctx.send(content=None, embed=embed, hidden=True)
			return

		embed = discord.Embed(
			title="Report sent!", description="The report has been send to our moderators! Fake reports can get you punished.", color=green)
		await ctx.send(content=None, embed=embed, hidden=False)

		embed = discord.Embed(title=f"Report submitted by {ctx.author} ({ctx.author.id}) via DMs",
							  description=f"**Answer:** {data['data'][question_id]['answers'][id]['answer']} \n**Answer by user with ID:** {data['data'][question_id]['answers'][id]['author_id']}",
							  color=red)
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)

	# Reporting an answer 
	elif ctx.custom_id == "report_answer":
		id = ctx.origin_message.embeds[0].author.name
		with open('Python/data.json') as data_file:
			data = json.load(data_file)

		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
							description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		for question in data["data"]:
			try:
				data["data"][question]["answers"][id]
				question_id = question
			except KeyError:
				pass

		embed = discord.Embed(title=f"Report submitted by {ctx.author} ({ctx.author.id})",
                        description=f"""**Answer:** {data['data'][question_id]['answers'][id]['answer']} 
**Answer by user with ID:** {data['data'][question_id]['answers'][id]['author_id']}

**[Jump to answer](https://discord.com/channels/869959165139910736/869988765307908096/{ctx.origin_message_id})**""",
                        color=red)
		channel = client.get_channel(870066564714627073)
		await channel.send(content=None, embed=embed)

		embed = discord.Embed(
			title="Report send!", description="The report has been send to our moderators! Fake reports can get you punished.", color=green)
		await ctx.send(content=None, embed=embed, hidden=True)

	# Removing an answer
	elif ctx.custom_id == "remove_answer":
		id = ctx.origin_message.embeds[0].author.name
		with open('Python/data.json') as data_file:
			data = json.load(data_file)
		for question in data["data"]:
			try:
				data["data"][question]["answers"][id]
				question_id = question
			except KeyError:
				pass

		if str(ctx.author.id) == str(data["data"][question_id]["answers"][id]["author_id"]):
			embed = discord.Embed(color=red, title="Answer deleted",
								  description="This answer has been deleted by the author of this question.")
			await ctx.edit_origin(embed=embed, content=None, components=None)
		elif ctx.author.guild_permissions.manage_messages == True:
			answer = ctx.origin_message.embeds[0].title
			embed = discord.Embed(color=red, title="Answer deleted",
								  description="This answer has been deleted by a moderator.")
			await ctx.edit_origin(embed=embed, content=None, components=None)
			try:
				user = await client.fetch_user(int(data["data"][question_id]["answers"][id]["author_id"]))
				embed = discord.Embed(color=red, title="One of your answers has been removed by a moderator",
									  description=f"\"{answer}\" has been removed by a moderator due to violation of our rules.")
				await user.send(content=None, embed=embed)
			except:
				user = await client.fetch_user(int(data["data"][question_id]["answers"][id]["author_id"]))
				embed = discord.Embed(
					title="Notice", description=f"Could not send a DM to to {user.name} because the user has DMs disabled", color=orange)
				await ctx.send(embed=embed, content=None, hidden=True)
		else:
			embed = discord.Embed(color=red, title="Permission error",
								  description="You are not allowed to delete this answer; you can only delete your own answers!")
			await ctx.send(content=None, embed=embed, hidden=True)

	# Mark an answer as best
	elif ctx.custom_id == "mark_best":
		id = ctx.origin_message.embeds[0].author.name
		with open('Python/data.json') as data_file:
			data = json.load(data_file)
		
		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
								description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		question_id = None
		for question in data["data"]:
			try:
				data["data"][question]["answers"][id]
				question_id = question
			except KeyError:
				pass
		if question_id == None:
			await ctx.send("Hold up! This command can not be executed, the ID could not be found.")
			return

		report_in_dm_unmark = [
			create_button(
				style=ButtonStyle.gray,
				label="Unmark best answer",
				custom_id="unmark_best"
			),
			create_button(
				style=ButtonStyle.red,
				label="Report question",
				custom_id="report_in_dm"
			)
		]
		action_row_unmark = create_actionrow(*report_in_dm_unmark)
		
		await ctx.edit_origin(embed=ctx.origin_message.embeds[0], components=[action_row_unmark], content=None)

		for answer in data["data"][question_id]["answers"]:
			try:
				if data["data"][question_id]["answers"][answer]["best_answer"] == "true":
					data["data"][question_id]["answers"][answer]["best_answer"] = "false"
					if data["data"][question_id]["answers"][answer]["message_id"] != "none":
						message = await ctx.channel.fetch_message(str(data["data"][question_id]["answers"][answer]["message_id"]))
						await message.edit(embed=message.embeds[0], content=None, components=[action_row4])
			except KeyError:
				pass

		data["data"][question_id]["answers"][id]["best_answer"] = "true"

		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))

		embed = discord.Embed(title="Marked answer as best!", description=f"This answer is now marked as the best answer! This change is reflected on the [website](https://ask-bot.gq/question?id={question_id})", color=green)
		await ctx.send(embed=embed, content=None)

	# Unmark an answer as best
	elif ctx.custom_id == "unmark_best":
		id = ctx.origin_message.embeds[0].author.name
		with open('Python/data.json') as data_file:
			data = json.load(data_file)

		# Check if user is banned
		if is_banned(ctx.author.id, data) == True:
			embed = discord.Embed(color=red, title="Error",
							description="You are currently banned, and thus unable to use Ask!.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return

		question_id = None
		for question in data["data"]:
			try:
				data["data"][question]["answers"][id]
				question_id = question
			except KeyError:
				pass
		if question_id == None:
			await ctx.send("Hold up! This command can not be executed, the ID could not be found.")
			return
		
		for answer in data["data"][question_id]["answers"]:
			try:
				if data["data"][question_id]["answers"][answer]["best_answer"] == "true":
					data["data"][question_id]["answers"][answer]["best_answer"] = "false"
					if data["data"][question_id]["answers"][answer]["message_id"] != "none":
						message = await ctx.channel.fetch_message(str(data["data"][question_id]["answers"][answer]["message_id"]))
						await message.edit(embed=message.embeds[0], content=None, components=[action_row4])
			except KeyError:
				pass

		data["data"][question_id]["answers"][id]["best_answer"] = "false"

		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))

		embed = discord.Embed(title="Done!",
		                      description=f"That answer is no longer the best answer!", color=green)
		await ctx.send(embed=embed, content=None)
	
	# Help menu
	elif ctx.custom_id == "help_menu":
		asked_question = ctx.selected_options[0]
		if asked_question == "supercharges":
			embed = discord.Embed(title="Supercharges", description=f"""*What are they?*

Supercharges can be used to boost your question to the front of the page of the [Ask! Question Browser](https://ask-bot.gq/browser) and to give it a special background color so the question is more noticeable.
Some helpful commands and links:
`/my-supercharges` — View how many supercharges you have
`/supercharge`     — Supercharge a question. You can also directly do this when asking the question
[Buy Supercharges](https://ask-bot.gq/supercharges/) — Buy some Supercharges
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)
		elif asked_question == "answer":
			embed = discord.Embed(title="/answer", description="""*Allows you to answer a question*

The `/answer` command allows you to respond to any question, as long as ```
— You know the ID
— The question is not deleted
``` As long as they're both true, you can answer to the question!
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)
			
		elif asked_question == "ask":
			embed = discord.Embed(title="/ask", description="""*Allows you to ask a question*

The `/ask` command allows you to send a question to the Ask! Discord server, where it can be viewed and answered by everyone. 			
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)

		elif asked_question == "create-question":
			embed = discord.Embed(title="/answer", description="""<:AskCheckmark:965160123397992458> *Allows you to create a question with a custom ID*

This command is for people who are verified, this is to prevent spam. If you're interested, you can apply [here](https://forms.gle/7J89gC9sRWePSJxc9).
This command allows you to create a question with almost any ID (nothing inappropriate, every answer is still send to the Ask! Discord server. The question can still be deleted) and it's even possible to send it to the channel you execute the command in! This can be used to for example, host polls that require a longer answer.
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)

		elif asked_question == "edit":
			embed = discord.Embed(title="/edit", description="""*Allows you to edit a question*

The `/edit` allows you to edit **your own questions**. If you know the ID and if the question is not deleted, you are able to edit the question!
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)

		elif asked_question == "help":
			embed = discord.Embed(title="/help", description="""*Gives you information*

The `/help` command gives you information about the commands you can run, and some helpful links.

**PRO TIP:** You actually accessed this text via the help command! :sunglasses: 
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)

		elif asked_question == "mydata":
			embed = discord.Embed(title="/mydata", description="""*Manage and view your data*

`/mydata` allows you to view all your data Ask! stores about you in a file, but it also allows you to remove all of you data.
Please note that you will be automatically banned from using Ask! if you delete your data, because Ask! stores this for moderation.
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)
		elif asked_question == "ping":
			embed = discord.Embed(title="/ping", description=f"""*Gives you the bot's latency*

The `/ping` command gives you the bot's latency in milliseconds. It's {round(client.latency*1000)}ms :)
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)

		elif asked_question == "toggle-dms":
			embed = discord.Embed(title="/toggle-dms", description=f"""*Toggle if Ask! should DM you*

The `/toggle-dms` command allows you to decide whether you want the bot to leave you alone or if it should send you a direct message when a question you asked gets answered.
If you have your Discord DMs disabled, and this enabled, Ask! will ping you in the Discord server. In every other case, Ask! will not ping you.
""", color=ask_magenta)
			await ctx.edit_origin(content=None, embed=embed, components=None)
		

	# Untrust person
	elif ctx.custom_id == "untrust_user": 
		#* Currently unused
		with open('Python/data.json') as data_file:
			data = json.load(data_file)
			
		data["trusted_people"].remove(ctx.author.id)

		await ctx.edit_origin(components=None, content=None)
		embed = discord.Embed(color=green, title=f"{ctx.author.id}")
		await ctx.send(content="Untrusted user.", hidden=True)



		

# DEV TOOLS

# Create invite
@slash.slash(name="create-invite",
	guild_ids=guild_ids,
	description="Creates an invite link to the current server. Ask! admin only.",
)
async def _create_invite(ctx):
	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	invite = await ctx.channel.create_invite(unique=True)
	await ctx.send(str(invite), hidden=True)

@slash.slash(name="clear",
	guild_ids=guild_ids,
	description="Clears channel messages. Ask! admin and server only.",
)
async def _clear(ctx):
	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	await ctx.channel.purge()
	await ctx.send("Cleared messages!", hidden=True)

@slash.slash(name="create-question",
	description="Create a question with a custom ID. Verified people only",
    options=[
            create_option(
                name="id",
                description="The ID you want (has to be unique)",
                option_type=3,
                required=True
            ),
         	create_option(
                name="question",
                description="The question you want to ask",
                option_type=3,
                required=True
            ),
           	create_option(
                name="current_channel",
                description="Send question in current channel too?",
                option_type=3,
                required=True,
				choices=[
					create_choice(
						name="No",
						value="false"
					),
					create_choice(
						name="Yes",
						value="true"
					)
				]
            )
    ]
)
async def _create_question(ctx, id : str, question: str, current_channel: str):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	# Check if user is banned
	if is_banned(ctx.author.id, data) == True:
		embed = discord.Embed(color=red, title="Error", description="You are currently banned, and thus unable to use Ask!.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	if int(ctx.author.id) in data["trusted_people"]:
		try:
			data["data"][id]
			embed = discord.Embed(color=red, title="Error",
                         description="That ID already exists. Please make sure that the ID you filled in has does not already exist.")
			await ctx.send(embed=embed, content=None, hidden=True)
			return
		except KeyError:
			pass
		
		embed = discord.Embed(title=f"{question}", color=ask_blue, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
		embed.set_author(name=id)
		if ctx.author.id in data["trusted_people"]:
			embed.set_footer(
				text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
		else:
			embed.set_footer(text=f"{ctx.author}")
		components = [
				create_button(
					style=ButtonStyle.green,
					label="Ask my question!"
				),
		]
		action_row = create_actionrow(*components)
		msg = await ctx.send(content="**Preview**", embed=embed, hidden=True, components=[action_row])

		button_ctx: ComponentContext = await wait_for_component(client, components=action_row)

		embed = discord.Embed(title=f"{question}", color=green, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
		if ctx.author.id in data["trusted_people"]:
			embed.set_footer(
				text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
		else:
			embed.set_footer(text=f"{ctx.author}")
		author = ctx.author

		await button_ctx.edit_origin(content="**Question asked! You can check it out at https://discord.gg/m25Zd4ZA6s ** \n\nYou will be pinged in the Ask! Discord server if you have your DMs closed", components=None, embed=embed, hidden=True)

		channel = client.get_channel(869988765307908096)

		embed = discord.Embed(title=f"{question}", color=ask_blue, description=f"Asked by {ctx.author} \n\nTo answer this question, copy the ID in the text above and use `/answer` \n\nIf you think something is wrong with this question, hit the report button below. If you are the writer of this question or a moderator, you can remove this question.")
		embed.set_author(name=id)
		if ctx.author.id in data["trusted_people"]:
			embed.set_footer(
				text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
		else:
			embed.set_footer(text=f"{ctx.author}")
		msg = await channel.send(content="<a:Discord_Loading:875322034337493033> Loading question, this shouldn't take longer than a few milliseconds.")
		
		question_options = [
			create_button(
				style=ButtonStyle.red,
				label="Report question",
				custom_id="report",
			),
			create_button(
				style=ButtonStyle.gray,
				label="Send a message with raw ID",
				custom_id="new_raw",
			),
			create_button(
				style=ButtonStyle.URL,
				label="Open on Ask! website",
				url=f"https://ask-bot.gq/question?id={id}"
			),
			create_button(
				style=ButtonStyle.gray,
				label="Remove question",
				custom_id="remove",
			)
		]

		question_action = create_actionrow(*question_options)

		await msg.edit(content=None, embed=embed, components=[question_action])
		if current_channel == "true":
			question_options_local = [
				create_button(
					style=ButtonStyle.gray,
					label="Send a message with raw ID",
					custom_id="new_raw",
				),
				create_button(
					style=ButtonStyle.URL,
					label="Open on Ask! website",
					url=f"https://ask-bot.gq/question?id={id}"
				)
			]
			question_action_local = create_actionrow(*question_options_local)
			embed = discord.Embed(title=f"{question}", color=ask_blue, description=f"Asked by {ctx.author} using Ask! \n\nTo answer this question, copy the ID in the text above and use `/answer`.")
			embed.set_author(name=id)
			if ctx.author.id in data["trusted_people"]:
				embed.set_footer(
					text=f"{ctx.author}", icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png")
			else:
				embed.set_footer(text=f"{ctx.author}")
			await ctx.channel.send(content=None, embed=embed, components=[question_action_local])

		with open('Python/data.json') as data_file:
			data = json.load(data_file)
			data["data"].update({
						f"{id}": {
							"question": f"{question}",
							"author_id": f"{author.id}",
							"message_id": f"{msg.id}",
							"author": f"{author}"
						}
					}
			)

		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))

		button_ctx: ComponentContext = await wait_for_component(client, components=question_action)
	else:
		embed = discord.Embed(color=red, title="Error",
                        description="This command is only for people who are <:AskCheckmark:965160123397992458> Verified!")
		await ctx.send(embed=embed, content=None, hidden=True)
		return



@slash.slash(name="wipe",
             description="Completely delete a question, including the JSON entry. Ask! admins only",
             guild_ids=guild_ids,
             options=[
                create_option(
                    name="id",
                    description="The Ask! ID. Is above question, case sensitive (-d for all deleted)",
                    option_type=3,
                    required=True
                )
             ])
async def _wipe(ctx, id: str):
	with open("Python/data.json") as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	if id == "-d":
		questions_deleted = 0
		delete_questions = []
		for question in data["data"]:
			try:
				if data["data"][question]["deleted"] == "true":
					questions_deleted += 1
					# data["data"].pop(question)
					delete_questions.append(question)
			except:
				pass
		for id_ in delete_questions:
			data["data"].pop(id_)

		embed = discord.Embed(color=green, title="Done!",
		                      description=f"Deleted {questions_deleted} questions!")
		await ctx.send(embed=embed, content=None, hidden=True)
		data["all_deleted_questions_clears"] += 1
		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))
		return

	try:
		data["data"][id]
	except KeyError:
		embed = discord.Embed(color=red, title="Error",
						description="That is not a valid ID. Please make sure that the ID you filled in has the correct casing, aBc instead of for example ABC and make sure the question you are trying view the history of exists.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		channel = client.get_channel(869988765307908096)
		question = await channel.fetch_message(int(data["data"][id]["message_id"]))
		embed = discord.Embed(color=red, title="Answer deleted",
						description="This question has been deleted by a moderator.")
		# await question.edit(content="test", embed=embed, components=[])
		# NOTE: ^ This doesn't work, buttons don't get removed.
		await question.delete()
	except (ValueError, discord.errors.NotFound):
		embed = discord.Embed(title="Notice", description=f"Could not delete the message, because the ID can not be found.", color=orange)
		await ctx.send(embed=embed, content=None, hidden=True)

	data["data"].pop(id)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))
	
	
	embed = discord.Embed(color=green, title="Done!", description=f"The question with ID {id} has been deleted from the data.json file.")
	await ctx.send(embed=embed, content=None, hidden=True)


@slash.slash(name="trust",
             description="Add a person to the list of trusted people. Ask! admin only",
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="The user you want to trust.",
                     option_type=6,
                     required=True
                 )
             ])
async def _trust(ctx, user: str):
	with open("Python/data.json") as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	if user.id in data["trusted_people"]:
		embed = discord.Embed(color=red, title="Error",
						description="This user is already trusted! You can untrust someone by using `/untrust`")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	else:
		data["trusted_people"].append(user.id)

		with open("Python/data.json", 'w') as json_file:
			json.dump(data, json_file, indent=4, separators=(',', ': '))

		embed = discord.Embed(color=green, title="Done!",
						description=f"Questions and anwers send by <@{user.id}> ({user}) will now contain a checkmark! You can untrust someone by using `/untrust`")
		await ctx.send(embed=embed, content=None, hidden=True)

		embed = discord.Embed(color=ask_blue, title="You are now verified!", description="""You are now verified, and every question and answer you send will contain a checkmark! 
		
Ask! has a system of verification, similar to social media, such as Twitter. Your verification will add a feeling of trust to questions and answers you give.
Your checkmark looks something like this: <:AskCheckmark:965160123397992458>, and this will be present under every question you ask while verified and under every answer you send.
You also have access to the `/createquestion` command. This will allow you to create a question with a custom ID. It also gives an option for sending a message in the current channel.
You could use this to set up feedback, for example. Note: the ID still has to be unique.

*Your checkmark will no longer appear if your status as a verified person gets revoked*

**Thank you for using Ask!**
""", inline=False)
		embed.set_author(icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png", name="Official Ask! message")

		try:
			await user.send(content=None, embed=embed)
		except:
			embed = discord.Embed(
				title="Notice", description=f"Could not send a DM to to {user.name} because the user has DMs disabled", color=orange)
			await ctx.send(embed=embed, content=None, hidden=True)


@slash.slash(name="untrust",
             description="Remove someone from the list of trusted people Ask! admin only",
			 guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="The user you want to untrust.",
                     option_type=6,
                     required=True
                 )
             ])
async def _trust(ctx, user: str):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	data["trusted_people"].remove(user.id)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))

	embed = discord.Embed(color=green, title=f"{user.name} is no longer trusted.", description="The verified/trusted status of this person has been revoked.")
	await ctx.send(content=None, embed=embed, hidden=True)

	embed = discord.Embed(color=ask_blue, title="You are no longer verified!", description="""Your status as a verified person has been revoked.

You are no longer verified. Any questions you ask, or answers you send, will no longer contain a sign of verification (<:AskCheckmark:965160123397992458>). You have also lost
access to the `/createquestion` command. You might be able to get verified in the future.

**Thank you for using Ask!**
""", inline=False)
	embed.set_author(icon_url="https://cdn.dantenl.tk/Ask%21%20Checkmark.png", name="Official Ask! message")

	try:
		await user.send(content=None, embed=embed)
	except:
		embed = discord.Embed(
			title="Notice", description=f"Could not send a DM to to {user.name} because the user has DMs disabled", color=orange)
		await ctx.send(embed=embed, content=None, hidden=True)

@slash.slash(name="ban",
             description="Ban someone from using Ask!. Ask! admin only",
			 guild_ids=guild_ids,
             options=[
                create_option(
                    name="user",
                    description="The user ID you want to ban (ask-bot.gq/id)",
                    option_type=3,
                    required=True
                ),
				create_option(
					name="reason",
					description="The reason why you want to ban them",
					option_type=3,
					required=True
				)
             ])
async def _ban(ctx, user: int, reason: str):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
						description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	if is_banned(user, data) == True:
		embed = discord.Embed(color=red, title="Error", description="This user is already banned! You can use `/unban` to unban this user.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	discord_user = await client.fetch_user(user)
	username = discord_user.name
	try:
		data["user_data"][str(user)]
	except KeyError:
		data["user_data"][str(user)] = {}

	try:
		data["user_data"][str(user)]["banned"]
	except KeyError:
		data["user_data"][str(user)]["banned"] = "true"

	if data["user_data"][str(user)]["banned"] == "false":
		data["user_data"][str(user)]["banned"] = "true"

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))
	
	embed = discord.Embed(title="User banned",
                       description=f"{username} is no longer able to interact with Ask! in any way now.", color=green)
	await ctx.send(embed=embed, content=None, hidden=True)

	embed = discord.Embed(title=f"{username}#{discord_user.discriminator} banned", description=f"""User <@{user}> ({username}#{discord_user.discriminator}, `{user}`) was banned by <@{ctx.author.id}> ({ctx.author.name}#{ctx.author.discriminator}, `{ctx.author.id}`) with the following reason:
	
```AskBanReason
{reason}
```""", color=red)
	channel = client.get_channel(970395322926891048)
	await channel.send(embed=embed, content=None)


@slash.slash(name="unban",
             description="Unban someone from Ask!. Ask! admin only",
             guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="The user you want to ban",
                     option_type=6,
                     required=True
                 )
             ])
async def _unban(ctx, user: str):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	if is_banned(user.id, data) == False:
		embed = discord.Embed(color=red, title="Error", description="This user is not banned! You can use `/ban` to ban this user.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		data["user_data"][str(user.id)]
	except KeyError:
		data["user_data"][str(user.id)] = {}

	try:
		data["user_data"][str(user.id)]["banned"]
	except KeyError:
		data["user_data"][str(user.id)]["banned"] = "false"

	if data["user_data"][str(user.id)]["banned"] == "true":
		data["user_data"][str(user.id)]["banned"] = "false"

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))
	
	embed = discord.Embed(title="User unbanned",
                       description=f"{user.name} can interact with Ask! again.", color=green)
	await ctx.send(embed=embed, content=None, hidden=True)

	embed = discord.Embed(title=f"{user.name}#{user.discriminator} unbanned", description=f"""User <@{user.id}> ({user.name}#{user.discriminator}, `{user.id}`) was unbanned by <@{ctx.author.id}> ({ctx.author.name}#{ctx.author.discriminator}, `{ctx.author.id}`).""", color=green)
	channel = client.get_channel(970395322926891048)
	await channel.send(embed=embed, content=None)

@slash.slash(name="give_supercharges",
             description="Give someone Supercharges",
			 guild_ids=guild_ids,
             options=[
                create_option(
                    name="user",
                    description="The user ID you want to give Supercharges to (ask-bot.gq/id)",
                    option_type=3,
                    required=True
                ),
				create_option(
					name="amount",
					description="The amount of Supercharges",
					option_type=4,
					required=True
				),
				create_option(
					name="custom_price",
					description="A custom price",
					option_type=4,
					required=False,
				)
             ])
async def _give_supercharges(ctx, user: int, amount: str, custom_price: int=None):
	with open('Python/data.json') as data_file:
		data = json.load(data_file)

	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		elif str(role.id) == "869962766507724852":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
		# NOTE: 869962766507724852 is for the admin role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return

	try:
		user = await client.fetch_user(user)
	except:
		embed = discord.Embed(color=red, title="That is not a valid user ID", description="Please enter a valid user ID. If you don't know how to get an ID, please click [here](https://ask-bot.gq/id)")
		await ctx.send(embed=embed, content=None, hidden=True)
		return


	price = None
	if custom_price == None:
		if amount == 5:
			price = "3.49"
		elif amount == 10:
			price = "6.99"
		elif amount == 15:
			price = "10.49"
	else:
		price = custom_price
	if price == None:
		embed = discord.Embed(color=red, title="Could not get a price for that amount!", description="If you would like to give this item for free, please set 0 as custom price.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	
	try:
		data["user_data"][str(user.id)]
	except KeyError:
		data["user_data"][str(user.id)] = {}

	try:
		data["user_data"][str(user.id)]["supercharges"]
	except KeyError:
		data["user_data"][str(user.id)]["supercharges"] = 0

	data["user_data"][str(user.id)]["supercharges"] += amount

	try:
		embed = discord.Embed(color=green, title="Supercharges added", description=f"""
Supercharges have been added to your account on <t:{int(time.time())}:F>. Here's a receipt to confirm your purchase!
```AskReceipt
——————————————————————————————
{amount}x Ask! Supercharge     — €{price}

Time:      {datetime.utcnow()} UTC
Purchaser: {user.id} ({user.name}#{user.discriminator})

Thank you for your purchase!
——————————————————————————————
```

*Please note that a refund CAN be requested, but you will lose access to Ask! if you do.*
""")
		await user.send(embed=embed, content=None)
	except:
		embed =  discord.Embed(color=orange, title="No DM send", description="A direct message could not be send to because the user has DMs closed")
		await ctx.send(embed=embed, content=None, hidden=True)

	with open("Python/data.json", 'w') as json_file:
		json.dump(data, json_file, indent=4, separators=(',', ': '))
	
	embed = discord.Embed(color=green, title="Supercharges added!", description=f"{amount} Supercharges have been added to {user.name}!")
	await ctx.send(hidden=True, embed=embed, content=None)


	
@slash.slash(name="restart",
             description="Restarts Ask!. Ask! owner only",
             guild_ids=guild_ids)
async def _restart(ctx):
	correct_roles_found = 0
	for role in ctx.author.roles:
		if str(role.id) == "869962152428056608":
			correct_roles_found += 1
		# NOTE: 869962152428056608 is for the owner role in the Ask! Discord server
	if correct_roles_found == 0:
		embed = discord.Embed(color=red, title="Error",
					description="You do not have permission to run this command.")
		await ctx.send(embed=embed, content=None, hidden=True)
		return
	f = open("ASK_SEND_STATUS_MESSAGE.txt", "w")
	f.write("This is a temporary file. It should delete itself as soon as Ask! starts up. This is so you can safely restart the server without the fear of it sending a message. This file will only appear with a manual restart.")
	f.close()
	embed = discord.Embed(color=orange, title="Restarting bot in 10 seconds!", description="The bot will restart in 10 seconds and should be online soon.")
	await ctx.send(content=None, hidden=True, embed=embed)
	channel = client.get_channel(870225556782870569)
	embed = discord.Embed(color=orange, title="Ask! will restart in about 10 seconds", description="The bot should not be offline for long. You might notice that the commands do not work or that they take a bit longer to respond.")
	await channel.send(embed=embed, content=None)
	await asyncio.sleep(10)
	embed = discord.Embed(color=orange, title="Restarting bot...", description="The bot is restarting now.")
	await ctx.send(content=None, hidden=True, embed=embed)
	restart_bot()

# * When error occurs
@client.event
async def on_slash_command_error(ctx, ex):
	print(f"{bcolors.FAIL}[{current_time()}] Error: {ex}{bcolors.END}")
	embed = discord.Embed(title="That didn't go well...", color=red, description=f"""You find yourself in a strange situation, the command you just executed resulted in an error.

However, this is isn't your regular error, this error was caused with an error in our coding!
A message has been send the [Ask! Discord server](https://discord.gg/m25Zd4ZA6s) server, however, a copy of the error is included below.

```AskErrorMessage
{ex}
```""")
	try:
		await ctx.channel.send(content=None, embed=embed)
	except:
		await ctx.send(content=None, embed=embed)
	embed = discord.Embed(title="Error", color=red, description=f"An error occured while {ctx.author} ({ctx.author.id}) attempted to run a command. \n\n```AskErrorMessage\n{ex}\n```")
	channel = client.get_channel(870066564714627073)
	await channel.send(embed=embed, content=None)
	
	
	

client.run("ODA3MTU1MTAwNTA2MjU5NDU2.Gd4-Hp.8-maxxHoYAXh97YWckCKh4UUHZkPJRO75GcPdc ")
