# Boss Package

> [!NOTE]
> You must have a special called `Boss` in your dex. Make sure the end date is before today's date. This special will be used to reward the winner.

This package is used to implement boss battles into your dex. <br>Below is a guide on implementing this package into your Discord dex bot.

------------------

## Installation

Download the `boss` directory, and add it to your `ballsdex/packages` folder. <br>
After that, go to `ballsdex/core/bot.py` and search for the line that starts with `PACKAGES` (around line 48). <br>
When you have found the line, add `boss` to the inside of the square brackets, separating it with a comma.

If you want to change the shiny buffs, go to lines 238-239 in `cog.py`.

------------------

## Commands

> [!NOTE]
> Some commands can only be used by admins. The commands that can only be accessed by admins control the boss's actions.

### Admin Commands:
* `/boss start` - Summons a boss. You are required to choose a ball. You can also choose the amount of health the boss will have (defaulted at 40,000)
* `/boss attack` - Starts a round, letting the boss attack. You can specify the amount of damage the boss deals. If it is not specified, it will range from zero to 2000.
* `/boss defend` - Starts a round, letting the boss defend.
* `/boss end_round` - Ends the current round and displays users' performance on the round.
* `/boss conclude` - Ends the boss battle and rewards the winner. You can choose to not reward the winner.

### User Commands:
* `/boss join` - Allows a player to join the boss battle.
* `/boss select` - Allows the player to select a ball to use.

------------------

## Reporting Bugs

Please submit any bugs you find to `moofficial` on Discord, or submit a bug report on this GitHub page.
