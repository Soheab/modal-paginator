import discord


IS_DPY2_5 = discord.version_info >= (2, 5, 0)
# refs:
# https://canary.discord.com/channels/336642139381301249/1341405833640022098
# https://github.com/Rapptz/discord.py/issues/10107
IS_DPY_2_5_WITH_INTERACTIONEDITFIXED = discord.version_info >= (2, 5, 1)
