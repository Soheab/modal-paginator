# ModalPaginator has a classmethod called from_text_inputs that takes a list of discord.ui.TextInput,
# splits it per 5 and construct a list of PaginatorModal with the text inputs.

# This example shows how to use the ModalPaginator.from_text_inputs classmethod and shows a common
# use case of it.


# import the required things

# import the discord.py library
import discord

# import the commands extension
from discord.ext import commands

# import the paginator
from discord.ext.modal_paginator import ModalPaginator, CustomButton


# define a list of text inputs
text_inputs = [  # pyright: ignore [reportUnknownVariableType]
    discord.ui.TextInput(label="What is your name?"),
    discord.ui.TextInput(label="Do you have any hobbies?"),
    discord.ui.TextInput(label="What is your favorite color?"),
    discord.ui.TextInput(label="What is your favorite food?"),
    discord.ui.TextInput(label="What is your favorite animal?"),
    discord.ui.TextInput(label="What is your favorite movie?"),
    discord.ui.TextInput(label="What is your favorite game?"),
    discord.ui.TextInput(label="What is your favorite song?"),
    discord.ui.TextInput(label="What is your favorite book?"),
    discord.ui.TextInput(label="What is your favorite website?"),
    discord.ui.TextInput(label="What is your favorite programming language?"),
    discord.ui.TextInput(label="What is your favorite IDE?"),
    discord.ui.TextInput(label="Which operating system do you use?"),
    discord.ui.TextInput(label="What is your favorite emoji?"),
]
# need a more dynamic way? Use a list comprehension with a list of strings (questions):
# questions = [
# "What is your name?",
# "Do you have any hobbies?",
# "What is your favorite color?",
# "What is your favorite food?",
# "What is your favorite animal?",
# "What is your favorite movie?",
# "What is your favorite game?",
# ...
# ]
# text_inputs = [discord.ui.TextInput(label=question) for question in questions]


# subclass the paginator


class TextInputPaginator(ModalPaginator):
    # define some default settings for the paginator that we can pass to the classmethod later.

    # the title of the modal
    # this defaults to "Enter your information" in from_text_inputs
    MODAL_TITLE = "Enter your information"
    # custom buttons
    # we are going to remove some buttons and change some.
    BUTTONS = {
        # remove cancel button
        "CANCEL": None,
        # remove the next button
        "NEXT": None,
        # change open button's label to "Open Modal" (default is "Open")
        "OPEN": CustomButton(label="Open Modal"),
    }

    # override page_string property to return a different string than the default one
    @property
    def page_string(self) -> str:
        # define two easy to access variables
        total_modals = len(self.modals)
        # add 1 to the current page because the first current page is at 0
        # but the user might find it confusing to see "0/14" instead of "1/14"
        current_modal_index = self.current_page + 1

        # return the custom string
        return f"Please go through all the modals and submit them ({current_modal_index}/{total_modals})."

    # override the on_finish method to send a message when the paginator is finished
    async def on_finish(self, interaction: discord.Interaction) -> None:
        # send a response with all the answers

        # create a list of answers using a list comprehension
        # format: **Label:** Answer
        answers = [f"**{tinput.label}:** {tinput.value}" for tinput in self.text_inputs]
        # using .join() to join the answers with a new line
        # and send the message
        await interaction.response.send_message("\n".join(answers))


bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents(messages=True, guilds=True))


@bot.command()
async def test(ctx: commands.Context[commands.Bot]):
    # let's send the paginator

    # defining an instance of the paginator with the classmethod from_text_inputs.
    # passing the text_inputs list, author_id, modals title and custom buttons.
    paginator = TextInputPaginator.from_text_inputs(
        *text_inputs,  # pyright: ignore [reportUnknownArgumentType]
        author_id=ctx.author.id,
        # passing the class attributes we defined earlier
        default_title=TextInputPaginator.MODAL_TITLE,
        buttons=TextInputPaginator.BUTTONS,  # pyright: ignore [reportGeneralTypeIssues]
        # remove the previous button
        can_go_back=False,
    )
    # sending the paginator
    await paginator.send(ctx)


bot.run("YOUR-BOT-TOKEN")
