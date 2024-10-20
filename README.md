# BossPackageBD

> [!NOTE]
> You must have a special called `Boss` in your dex. Make sure the special's end date is before today's date. The `Boss` special will be used to reward the winner.

This package is used to implement boss battles into your dex.
Below is a guide on implementing this package into your Discord dex bot.

------------------

## Installation

To install BossPackageBD, install it through [DexScript](https://github.com/Dotsian/DexScript/wiki/Installing,-Updating,-and-Uninstalling) or manually install it.

<details>
<summary><strong>Manually</strong></summary>

Download the `boss` directory, and add it to your `ballsdex/packages` folder.
Afterward, go to `ballsdex/core/bot.py` and search for the line starting with `PACKAGES` (around line 48).
When you have found the line, add `boss` to the inside of the square brackets, separating it with a comma.

</details>

<details>
<summary><strong>DexScript</strong></summary>

Make sure [DexScript](https://github.com/Dotsian/DexScript/wiki/Installing,-Updating,-and-Uninstalling) is installed on your bot. In Discord, ensure you have eval command permissions and run `b.install https://github.com/MoOfficial0000/BossPackageBD`. 
BossPackageBD will be instantly installed on your bot.

</details>

------------------

## Configuration

If you want to change the shiny buffs, go to line 48 in `cog.py`.
Change the `SHINY_BUFFS` variable, setting the first number to the health buff and the second to the attack buff.

------------------

## Commands

> [!NOTE]
> Some commands can only be used by admins. The commands that admins can only access are used to control the boss's actions.

### Admin Commands

* `/boss start` - Summons a boss. You are required to choose a ball. You can also select the amount of health the boss will have (defaulted at 40,000)
* `/boss attack` - Starts a round, letting the boss attack. You can specify the amount of damage the boss deals. If it is not specified, it will range from zero to 2000.
* `/boss defend` - Starts a round, letting the boss defend.
* `/boss end_round` - Ends the current round and displays users' performance on the round.
* `/boss conclude` - Ends the boss battle and rewards the winner. You can choose not to reward the winner.

### User Commands

* `/boss join` - Allows a player to join the boss battle.
* `/boss select` - Allows the player to select a ball to use.

------------------

## Reporting Bugs

Please submit any bugs you find to `moofficial` on Discord, or submit a bug report on this GitHub page.
