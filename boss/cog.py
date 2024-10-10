import logging
import random
import re
import string
from typing import TYPE_CHECKING

import discord
from ballsdex.core.models import (
    BallInstance,
    Player,
    specials,
)
from ballsdex.core.utils.logging import log_action
from ballsdex.core.utils.transformers import BallInstanceTransform, BallTransform
from ballsdex.settings import settings
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.boss.cog")
FILENAME_RE = re.compile(r"^(.+)(\.\S+)$")

# Health, Attack
SHINY_BUFFS = (1000, 1000)


@app_commands.guilds(*settings.admin_guild_ids)
class Boss(commands.GroupCog):
    """
    Boss commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.boss_enabled = False
        self.balls = []
        self.users = []
        self.usersdamage = []
        self.usersinround = []
        self.currentvalue = ("")
        self.bossHP = 40000
        self.picking = False
        self.round = 0
        self.attack = False
        self.bossattack = 0
        self.bossball = None
        self.bosswild = None

    @staticmethod
    def bound(low, high, value):
        return max(low, min(high, value))

    @staticmethod
    def get_file(name: str):
        random_name = ''.join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.ascii_letters,
            k=15
        ))

        file_name = f"nt_{''.join(random_name)}.{name.split('.')[-1]}"
        return discord.File(f".{name}", filename=file_name)

    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def start(
        self, 
        interaction: discord.Interaction, 
        ball: BallTransform, 
        health: int = 40000
    ):
        """
        Start the boss

        Parameters
        ----------
        health: int
            The amount of health the boss will have.
        """
        if self.boss_enabled:
            return await interaction.response.send_message(
                "There is already an ongoing boss battle", 
                ephemeral=True
            )
        
        self.bossHP = health

        await interaction.response.send_message(
            f"# The boss battle has begun!\n-# HP: {self.bossHP}",
            file=self.get_file(ball.collection_card)
        )

        await interaction.followup.send("Use `/boss join` to join the battle!")

        if ball is not None:
            self.boss_enabled = True
            self.bossball = ball

            self.bosswild = self.get_file(ball.wild_card)

    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def attack(self, interaction: discord.Interaction, damage: int | None = None):
        """
        Starts a round where the boss attacks.

        Parameters
        ----------
        damage: int | None
            The damage the boss will deal. Defaults to 0-2000.
        """
        if not self.boss_enabled:
            return await interaction.response.send_message("Boss is disabled", ephemeral=True)
        
        if self.picking:
            return await interaction.response.send_message(
                "There is already an ongoing round", 
                ephemeral=True
            )
        
        if len(self.users) == 0:
            return await interaction.response.send_message(
                "There are not enough users to start the round", 
                ephemeral=True
            )
        
        if self.bossHP <= 0:
            return await interaction.response.send_message("The boss is dead", ephemeral=True)

        self.round += 1

        await interaction.response.send_message(
            f"Round {self.round}\n# {self.bossball.country} is preparing to attack!",
            file=self.get_file(self.bossball.wild_card)
        )

        await interaction.followup.send(
            f"Use `/boss select` to select your defending {settings.collectible_name}.\n"
            f"Your selected {settings.collectible_name}'s HP will be used to defend."
        )
        self.picking = True
        self.attack = True

        self.bossattack = damage if damage is not None else random.randrange(0, 2000, 100)

    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def defend(self, interaction: discord.Interaction):
        """
        Starts a round where the boss defends.
        """
        if not self.boss_enabled:
            return await interaction.response.send_message("Boss is disabled", ephemeral=True)
        
        if self.picking:
            return await interaction.response.send_message(
                "There is already an ongoing round", 
                ephemeral=True
            )
        
        if len(self.users) == 0:
            return await interaction.response.send_message(
                "There are not enough users to start the round", 
                ephemeral=True
            )
        
        if self.bossHP <= 0:
            return await interaction.response.send_message("The boss is dead", ephemeral=True)
        
        self.round += 1

        await interaction.response.send_message(
            f"Round {self.round}\n# {self.bossball.country} is preparing to defend!",
            file=self.get_file(self.bossball.wild_card)
        )

        await interaction.followup.send(
            f"Use `/boss select` to select your attacking {settings.collectible_name}.\n"
            f"Your selected {settings.collectible_name}'s ATK will be used to attack."
        )

        self.picking = True
        self.attack = False


    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def end_round(self, interaction: discord.Interaction):
        """
        Ends the current round.
        """
        if not self.boss_enabled:
            return await interaction.response.send_message("Boss is disabled", ephemeral=True)

        if not self.picking:
            return await interaction.response.send_message(
                "There are no ongoing rounds, use `/boss attack` or `/boss defend` to start one", 
                ephemeral=True
            )
        
        self.picking = False

        if not self.attack:
            if self.bossHP <= 0:
                await interaction.response.send_message(
                    f"{self.currentvalue}There is 0 HP remaining on the boss, "
                    "the boss has been defeated!",
                )
            else:
                await interaction.response.send_message(
                    f"{self.currentvalue}There is {self.bossHP} HP remaining on the boss",
                )
        else:
            snapshotusers = self.users.copy()
            
            for user in snapshotusers:
                if str(user) not in self.currentvalue:
                    self.currentvalue += f"<@{user}> has not picked on time and ***died!***\n"
                    self.users.remove(user)

            message = f"The boss has dealt {self.bossattack} damage!\n{self.currentvalue}"

            if len(self.users) == 0:
                message += "The boss has won!"
            
            await interaction.response.send_message(message)
        
        self.currentvalue = ""

    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def peek(self, interaction: discord.Interaction):
        """
        Displays the current stats for the boss
        """
        await interaction.response.send_message(
            f"CurrentValue:{self.currentvalue}\n"
            f"Users:{self.users}\n\n"
            f"UsersDamage:{self.usersdamage}\n\n"
            f"Balls:{self.balls}\n\n"
            f"UsersInRound:{self.usersinround}", 
            ephemeral=True
        )


    @app_commands.command()
    async def select(self, interaction: discord.Interaction, ball: BallInstanceTransform):
        """
        Select a countryball to use against the boss.

        Parameters
        ----------
        ball: Ball
            The countryball you want to use.
        """
        if [interaction.user.id, self.round] in self.usersinround:
            return await interaction.response.send_message(
                f"You have already selected an {settings.collectible_name}", ephemeral=True
            )
        
        if not self.boss_enabled:
            return await interaction.response.send_message("Boss is disabled", ephemeral=True)
        
        if not self.picking:
            return await interaction.response.send_message(
                f"It is not time to select an {settings.collectible_name} yet", ephemeral=True
            )

        if interaction.user.id not in self.users:
            return await interaction.response.send_message(
                "You have not joined the boss battle or you died!", ephemeral=True
            )

        if ball in self.balls:
            return await interaction.response.send_message(
                f"You cannot select the same {settings.collectible_name} twice", ephemeral=True
            )
        
        if ball is None:
            return
            
        self.balls.append(ball)
        self.usersinround.append([int(interaction.user.id),self.round])

        # Minimum and maximum attack and health stats 
        ballattack = self.bound(0, 14000, ball.attack)
        ballhealth = self.bound(0, 14000, ball.health)

        messageforuser = (
            f"{ball.description(short=True, include_emoji=True, bot=self.bot)}"
            f"has been selected for this round, with {ballattack} ATK and {ballhealth} HP"
        )

        description = ball.description(short=True, include_emoji=True, bot=self.bot)

        if "✨" in messageforuser:
            messageforuser = (
                f"{description} has been selected for this round, with "
                f"{ballattack}+{SHINY_BUFFS[1]} ATK and {ballhealth}+{SHINY_BUFFS[0]} HP"
            )
            ballhealth += SHINY_BUFFS[0]
            ballattack += SHINY_BUFFS[1]

        if not self.attack:
            self.bossHP -= ballattack
            self.usersdamage.append([interaction.user.id, ballattack])
            
            self.currentvalue += (
                f"<@{interaction.user.id}>'s {description} has dealt {ballattack} damage!\n"
            )
        else:
            if self.bossattack >= ballhealth:
                self.users.remove(interaction.user.id)
                self.currentvalue += (
                    f"<@{interaction.user.id}>'s {description} had {ballhealth} HP "
                    "and ***died!***\n"
                )
            else:
                self.currentvalue += (
                    f"<@{interaction.user.id}>'s {description} had {ballhealth} HP "
                    "and ***survived!***\n"
                )

        await interaction.response.send_message(
            messageforuser, ephemeral=True
        )

    @app_commands.command()
    @app_commands.checks.has_any_role(*settings.root_role_ids, *settings.admin_role_ids)
    async def conclude(self, interaction: discord.Interaction, reward: bool = True):
        """
        Finishes the boss and concludes a winner.

        Parameters
        ----------
        reward: Bool
            Whether the winner should be rewarded or not.
        """
        self.picking = False
        self.boss_enabled = False

        test = self.usersdamage
        test2 = []
        total = ("")
        totalnum = []

        for i in range(len(test)):
            if test[i][0] in test2 or test[i][0] not in self.users:
                continue
            
            temp = 0
            tempvalue = test[i][0]
            test2.append(tempvalue)

            for j in range(len(test)):
                if test[j][0] == tempvalue:
                    temp += test[j][1]
            
            total += f"<@{tempvalue}> has dealt a total of {temp} damage!\n"
            totalnum.append([tempvalue, temp])
        
        bosswinner = 0
        highest = 0

        for k in range(len(totalnum)):
            if totalnum[k][1] > highest:
                highest = totalnum[k][1]
                bosswinner = totalnum[k][0]
        
        if bosswinner == 0:
            self.round = 0
            self.balls = []
            self.users = []
            self.currentvalue = ("")
            self.usersdamage = []
            self.usersinround = []
            self.bossHP = 40000
            self.round = 0
            self.attack = False
            self.bossattack = 0
            self.bossball = None
            self.bosswild = None

            return await interaction.response.send_message(
                "BOSS HAS CONCLUDED\nThe boss has won the boss battle!"
            )
        
        if reward:
            await interaction.response.defer(thinking=True)

            player, _ = await Player.get_or_create(discord_id=bosswinner)
            special = special = [x for x in specials.values() if x.name == "Boss"][0]

            await BallInstance.create(
                ball=self.bossball,
                player=player,
                shiny=False,
                special=special,
                attack_bonus=0,
                health_bonus=0,
            )

            await interaction.followup.send(
                f"BOSS HAS CONCLUDED.\n{total}\n<@{bosswinner}> has won the Boss Battle!\n\n"
                f"`{self.bossball.country}` {settings.collectible_name} was "
                f"successfully given to *<@{bosswinner}>*.\n"
                f"ATK:`0` • Special: `Boss`\n"
                f"HP:`0` • Shiny: `None`"
            )

            await log_action(
                f"`BOSS REWARDS` gave {settings.collectible_name} "
                f"{self.bossball.country} to *<@{bosswinner}>*"
                f"Special=Boss ATK=0 "
                f"HP=0 shiny=None",
                self.bot,
            )
        else:
            await interaction.response.send_message(
                f"BOSS HAS CONCLUDED.\n{total}\n<@{bosswinner}> has won the boss battle!\n\n"
            )
        
        self.round = 0
        self.balls = []
        self.users = []
        self.currentvalue = ("")
        self.usersdamage = []
        self.usersinround = []
        self.bossHP = 40000
        self.round = 0
        self.attack = False
        self.bossattack = 0
        self.bossball = None
        self.bosswild = None

    @app_commands.command()
    async def join(self, interaction: discord.Interaction):
        """
        Joins the current boss battle.
        """

        if not self.boss_enabled:
            return await interaction.response.send_message("Boss is disabled", ephemeral=True)
        
        if [interaction.user.id, self.round] in self.usersinround:
            return await interaction.response.send_message(
                "You have already joined the boss", 
                ephemeral=True
            )
        
        if self.round != 0 and interaction.user.id not in self.users:
            return await interaction.response.send_message(
                "It is too late to join the boss, or you have died", ephemeral=True
            )
        
        if interaction.user.id in self.users:
            return await interaction.response.send_message(
                "You have already joined the boss", ephemeral=True
            )
        
        self.users.append(interaction.user.id)

        await interaction.response.send_message(
            "You have joined the boss battle!", ephemeral=True
        )
