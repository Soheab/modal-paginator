# the extensions allows you to customize the buttons of the paginator.
# you can change the style, label, emoji and row
# let's do that in this example.

# import the required things

# for type checking
from typing import Optional

# for the paginator
# import the discord.py library
import discord

# import the commands extension
from discord.ext import commands

# import the paginator and paginator modal
from discord.ext.modal_paginator import ModalPaginator, PaginatorModal

# import the custom button class to subclass it
# we could also use the ui.Button class directly
# but we need the on_optional_modal and on_required_modal methods....
from discord.ext.modal_paginator.custom_button import CustomButton


# subclassing the CustomButton
# we are going to use this to change the style, label and emoji of the Open button
class OpenButton(CustomButton):
    # init the button
    def __init__(self) -> None:
        # call the original init method with our default style, label and row
        super().__init__(style=discord.ButtonStyle.gray, label="Open", row=0, emoji="🔓")

    # override the on_optional_modal method
    # we are going to change the emoji and style of the Open button with this when the modal is optional
    def on_optional_modal(self, button: discord.ui.Button[ModalPaginator]) -> None:
        # change the emoji to an unlocked lock emoji
        button.emoji = "🔓"
        # change the style to gray
        button.style = discord.ButtonStyle.gray

    # override the on_required_modal method
    # we are going to change the emoji and style of the Open button with this when the modal is required
    def on_required_modal(self, button: discord.ui.Button[ModalPaginator]) -> None:
        # change the emoji to a locked lock emoji
        button.emoji = "🔒"
        # change the style to red
        button.style = discord.ButtonStyle.red


# subclass the paginator to pass the custom buttons to the buttons kwarg
class Test(ModalPaginator):
    def __init__(self):
        modals = [
            PaginatorModal(discord.ui.TextInput(label="What is your name?"), title="Name", required=True),
            PaginatorModal(discord.ui.TextInput(label="Do you have any hobbies?"), title="Hobbies"),
        ]

        # let's change the buttons...
        # you don't have to pass all the buttons
        # you can pass only the buttons you want to change
        # and the rest will be the default buttons
        # you can also pass None to remove a button
        # valid keys are: "OPEN", "NEXT", "PREVIOUS", "CANCEL" and "FINISH"
        buttons = {
            # change the open button to our custom button
            "OPEN": OpenButton(),
            # change the next button's style to green
            "NEXT": CustomButton(style=discord.ButtonStyle.green),
            # change the previous button's style to red
            "PREVIOUS": CustomButton(style=discord.ButtonStyle.red),
            # remove the cancel button
            "CANCEL": None,
            # change the finish button's label to "All Done!" and style to green
            "FINISH": CustomButton(
                label="All Done!",
            ),
        }

        # call the original init method with our custom buttons (buttons=)
        # and any other args we want to pass to the paginator
        super().__init__(modals, buttons=buttons)

    async def on_finish(self, interaction: discord.Interaction) -> None:
        # send a message saying "Done!" to the user
        # ephemeral=True means only the user can see the message
        await interaction.response.send_message("Done!", ephemeral=True)


bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents(messages=True, guilds=True))


@bot.command()
async def test(ctx: commands.Context[commands.Bot]):
    # let's send the paginator
    # defining an instance of the paginator
    paginator = Test()
    # sending the paginator
    await paginator.send(ctx)


bot.run("YOUR-BOT-TOKEN")
