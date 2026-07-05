import asyncio
import time

from database import add_egg_with_check, add_entry, check_key, delete_entry, delete_key, get_value, list_decoded_entries, get_amount_of_entries, show_specific_entry
import discord
from discord import app_commands
from discord.ext import commands
from utility import command_check
from globals import APPROVED_ROLES, BOT_BLACKLIST, CHANNELS, I_SPY, WISDOM, FUN_ROLES
from rated import DEFER, EDIT_MESSAGE, FOLLOWUP, INTERACTION, PURGE_ROLES, REMOVE_ROLES, ADD_ROLES, SEND, SEND_VIEW
from views import ButtonEgg_Throw

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    channel_choices = [
        discord.app_commands.Choice(name=ch.title(), value=ch) 
        for ch in sorted(CHANNELS.keys())
    ]

    @discord.app_commands.command(name="invite", description="Give access to Drone Masters chat")
    async def invite(self, interaction: discord.Interaction, target: discord.Member):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await CHANNELS["drone-masters"].set_permissions(target, view_channel=True, send_messages=True)
            await asyncio.sleep(1)
            await FOLLOWUP(f"Permissions granted. {target.mention} has been ushered into the Drone Master chambers.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/invite`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="bid_farewell", description="Remove access from Drone Masters chat")
    async def bid_farewell(self, interaction: discord.Interaction, target: discord.Member):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await CHANNELS["drone-masters"].set_permissions(target, view_channel=False, send_messages=False)
            await FOLLOWUP(f"Farewell, {target.display_name}. Their access to the Drone Master channel has been dissolved.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/bid_farewell`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="wisdoms", description="Show the number of wisdoms")
    async def wisdoms(self, interaction: discord.Interaction):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await FOLLOWUP(f"I have {len(WISDOM)} wisdoms.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/wisdoms`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="nr", description="Add a new secret role.")
    async def nr(self, interaction: discord.Interaction, name: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            add_entry(name, "dummy")
            await FOLLOWUP("Role created successfully.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/nr`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="check_key", description="Check if a key exists in the database.")
    async def check_key(self, interaction: discord.Interaction, key: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            responses = []

            if check_key(key):
                value = list_decoded_entries(key)

                if not value:
                    value = get_value(key)
                
                responses.append(f"Key `{key}` found! Value: {value}")

            if responses:
                await FOLLOWUP("\n".join(responses), interaction)
            else:
                await FOLLOWUP(f"No key found for '{key}'.", interaction)
                
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/check_key`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="delete_key", description="Delete a key from the database.")
    async def delete_key(self, interaction: discord.Interaction, key: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            delete_key(key)
            await FOLLOWUP(f"Key '{key}' deleted successfully.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/delete_key`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="assign", description="Assign a role to a user.")
    async def assign(self, interaction: discord.Interaction, user: discord.Member, role: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            if not any(role in category_data for category_data in FUN_ROLES.values()) and role not in APPROVED_ROLES:
                await FOLLOWUP("You cannot assign this role through my commands.", interaction)
                return

            if (role not in APPROVED_ROLES and str(user.id) in list_decoded_entries(role)) or (role in APPROVED_ROLES and APPROVED_ROLES[role] in user.roles):
                await asyncio.sleep(1)
                await FOLLOWUP("They already own this role, duh.", interaction)
                return

            if role in (FUN_ROLES["Easter"] + FUN_ROLES["Easter26"] + FUN_ROLES["Easter27"]):
                await add_egg_with_check(role, user)
            elif role in APPROVED_ROLES:
                await ADD_ROLES(user, APPROVED_ROLES[role])
            else:
                add_entry(role, str(user.id))

            await asyncio.sleep(1)
            await FOLLOWUP(f"I gave the role to {user.mention}.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/assign`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="unassign", description="Remove a role from a user.")
    async def unassign(self, interaction: discord.Interaction, user: discord.Member, role: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return
        
        entries = []

        await DEFER(interaction)

        try:
            if not any(role in category_data for category_data in FUN_ROLES.values()) and role not in APPROVED_ROLES:
                await FOLLOWUP("You cannot unassign this role through my commands.", interaction)
                return

            if role not in APPROVED_ROLES:
                entries = list_decoded_entries(role)

            if (role not in APPROVED_ROLES and not str(user.id) in entries) or (role in APPROVED_ROLES and not APPROVED_ROLES[role] in user.roles):
                await asyncio.sleep(1)
                await FOLLOWUP("They do not own the role. Are you ok?", interaction)
                return

            if role not in APPROVED_ROLES:
                index = entries.index(str(user.id))
                delete_entry(role, index)
            else:
                await REMOVE_ROLES(user, APPROVED_ROLES[role])

            await asyncio.sleep(1)
            await FOLLOWUP(f"Took the role away from {user.mention}.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/unassign`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="purge", description="Purge a role.")
    async def purge(self, interaction: discord.Interaction, user: discord.Member, role: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            if not any(role in category_data for category_data in FUN_ROLES.values()) and role not in APPROVED_ROLES:
                await FOLLOWUP("You cannot purge this role through my commands.", interaction)
                return
            
            if role in APPROVED_ROLES:
                await PURGE_ROLES(APPROVED_ROLES[role])
            else:
                delete_key(role)

            await asyncio.sleep(1)
            await FOLLOWUP("The role is gone.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/purge`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="enlist", description="Add an user to the blacklist, or remove them if they are already blacklisted.")
    @discord.app_commands.choices(list=[
        discord.app_commands.Choice(name='Blacklist', value='blacklist'),
        discord.app_commands.Choice(name='Whitelist', value='whitelist')
    ])
    async def enlist(self, interaction: discord.Interaction, list: str, target: discord.Member):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            finalMsg = ""
            if list == 'blacklist':
                if str(target.id) not in BOT_BLACKLIST:
                    BOT_BLACKLIST.append(str(target.id))
                    finalMsg = f"{target.mention} has been blacklisted."
                else:
                    finalMsg = f"{target.mention} is already blacklisted."
            elif list == 'whitelist':
                if str(target.id) in BOT_BLACKLIST:
                    BOT_BLACKLIST.remove(str(target.id))
                    finalMsg = f"{target.mention} has been whitelisted."
                else:
                    finalMsg = f"{target.mention} is not in the blacklist."

            await FOLLOWUP(finalMsg, interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/delete_key`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="ispy", description="Begin a game of ispy.")
    @discord.app_commands.choices(channel=channel_choices)
    async def ispy(self, interaction: discord.Interaction, channel: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await FOLLOWUP(f"Starting ispy game in {channel}...", interaction)

            I_SPY['channel'] = CHANNELS[channel]
            I_SPY['status'] = 0

            await SEND(I_SPY['channel'], I_SPY['questions'][0])

            await asyncio.sleep(I_SPY['maxwait'])

            if I_SPY['status'] == 0:
                I_SPY['status'] = None
                await SEND(I_SPY['channel'],'Whatever.')
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/ispy`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="architect", description="Drop Architect Egg.")
    @discord.app_commands.choices(channel=channel_choices)
    async def architect(self, interaction: discord.Interaction, channel: str, countdown: int):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await FOLLOWUP(f"Launching Architect Egg in {channel}...", interaction)
            await asyncio.sleep(1)

            arcMsg = await SEND(CHANNELS[channel], f"The Architect Egg is falling at terminal velocity in this channel! Take cover <t:{round(time.time() + countdown)}:R>.")
            await asyncio.sleep(countdown)

            view = ButtonEgg_Throw(timeout=30)
            view.thrower = None
            view.disabled = False

            view.type = "Architect"

            view.channel = CHANNELS[channel]
            view.toolate = True
            view.message = await SEND_VIEW(CHANNELS[channel], "The Architect Egg fell from the sky!", view)
            await asyncio.sleep(1)
            await EDIT_MESSAGE(arcMsg, "The Architect Egg landed gracefully.")

            await view.wait()
            await view.too_late()
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/architect`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="makesay", description="Have the drone speak your words.")
    @discord.app_commands.choices(channel=channel_choices)
    async def makesay(self, interaction: discord.Interaction, channel: str, txt: str):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            await FOLLOWUP(f"I'm clearing my voice...", interaction)
            await asyncio.sleep(1)
            await SEND(CHANNELS[channel], txt)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/makesay`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="quiz_new", description="Add quiz question to the database.")
    async def quiz_new(
        self, interaction: discord.Interaction, 
        question: str, 
        correct_answer: str, 
        answer2: str, 
        answer3: str, 
        answer4: str, 
        good_response: str, 
        bad_response: str
    ):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            data = "|".join([question, correct_answer, answer2, answer3, answer4, good_response, bad_response])
            add_entry("quiz", data)
            await FOLLOWUP("Successfully added new quiz question.", interaction)
        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/quiz new`: {exc}", interaction)
            raise

    @discord.app_commands.command(name="quiz_manage", description="Manage quiz questions")
    @discord.app_commands.choices(type=[
        discord.app_commands.Choice(name="Amount", value="amount"),
        discord.app_commands.Choice(name="Print", value="print"),
        discord.app_commands.Choice(name="List", value="list"),
        discord.app_commands.Choice(name="Delete", value="delete"),
    ])
    async def quiz_manage(
        self,
        interaction: discord.Interaction,
        type: str,
        index: int = None
    ):
        stopMsg = command_check(interaction, True)
        if stopMsg:
            await INTERACTION(interaction, stopMsg, True)
            return

        await DEFER(interaction)

        try:
            if type == "amount":
                await FOLLOWUP(f"There are {get_amount_of_entries("quiz")} questions in the database.", interaction)

            elif type == "print":
                if index is None:
                    await FOLLOWUP("You must provide an index for the `print` type.", interaction)
                    return
                question = show_specific_entry("quiz", index)
                q_split = question.split("|")
                to_send = (
                    f"Q:\n{q_split[0]}\n"
                    f"Correct Answer:\n{q_split[1]}\n"
                    f"A2:\n{q_split[2]}\n"
                    f"A3:\n{q_split[3]}\n"
                    f"A4:\n{q_split[4]}\n"
                    f"Good response:\n{q_split[5]}\n"
                    f"Bad response:\n{q_split[6]}"
                )
                await FOLLOWUP(to_send, interaction)

            elif type == "list":
                entries = list_decoded_entries("quiz")
                if not entries:
                    await FOLLOWUP("No quiz questions found.", interaction)
                    return

                response_lines = []
                for i, entry in enumerate(entries):
                    parts = entry.split("|")
                    if len(parts) != 7:
                        continue
                    response_lines.append(
                        f"**Question {i}:**\n"
                        f"Q: {parts[0]}\n"
                        f"Correct: {parts[1]} | A2: {parts[2]} | A3: {parts[3]} | A4: {parts[4]}\n"
                        f"Good: {parts[5]} | Bad: {parts[6]}\n"
                    )
                text = "\n".join(response_lines)
                if len(text) <= 2000:
                    await FOLLOWUP(text, interaction)
                else:
                    await FOLLOWUP("The list is too long. Sending first 2000 characters:", interaction)
                    await FOLLOWUP(text[:2000], interaction)

            elif type == "delete":
                if index is None:
                    await FOLLOWUP("You must provide an index for the `delete` type.", interaction)
                    return
                delete_entry("quiz", index)
                await FOLLOWUP(f"Question at index {index} has been deleted.", interaction)

        except Exception as exc:
            await FOLLOWUP(f"Something went wrong with `/quiz manage`: {exc}", interaction)
            raise