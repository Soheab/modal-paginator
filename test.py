from typing import Optional
import discord

from discord.ext import commands

from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
from discord.ext.modal_paginator.custom_button import CustomButton


class OpenButton(CustomButton):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Open", row=0, emoji="🔓")

    def on_optional_modal(self, button) -> None:  # pyright: ignore [reportIncompatibleMethodOverride]
        print("on optiomal modal called")
        button.emoji = "🔓"
        button.style = discord.ButtonStyle.gray

    def on_required_modal(self, button) -> None:  # pyright: ignore [reportIncompatibleMethodOverride]
        print("on requred modal called")
        button.emoji = "🔒"
        button.style = discord.ButtonStyle.red


class Test(ModalPaginator):
    def __init__(self):
        modals = [
            PaginatorModal(discord.ui.TextInput(label="test"), title="nice."),
            PaginatorModal(discord.ui.TextInput(label="test1"), title="nice.", required=True),
            PaginatorModal(discord.ui.TextInput(label="test2"), title="nice."),
        ]

        buttons: dict[str, Optional[CustomButton]] = {
            "OPEN": OpenButton(),
            "NEXT": CustomButton(style=discord.ButtonStyle.green),
            "PREVIOUS": CustomButton(style=discord.ButtonStyle.red),
            # "CANCEL": CustomButton(label="Stop", style=discord.ButtonStyle.red),
            # "CANCEL": discord.ui.Button(emoji="🔴", style=discord.ButtonStyle.blurple, label=None),
            "CANCEL": None,
            "FINISH": CustomButton(label="All Done!", style=discord.ButtonStyle.green),
        }

        super().__init__(modals, buttons=buttons)

    async def on_finish(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Done!", ephemeral=True)


bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents(messages=True, guilds=True))


@bot.command()
async def test(ctx):
    await Test().send(ctx)


bot.run("lol")
