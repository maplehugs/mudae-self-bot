
# Mudae Self Bot

### by GDiazFentanes (Original Project) – Updated by Maple

## Introduction

This project is a **"fork"/update** of [GDiazFentanes’ original Mudae bot](https://github.com/GuilleDiazFentanes/AutoClaim-AutoRoll-AutoReact-MudaeBot-2025) which for some reason crashed on my setup.
I have updated some functions in the original `Function.py`, added a **Sniper** for other people’s rolls, and implemented a **pull list** feature.

With these updates, the bot can:

* Automatically claim Mudae characters (waifus, husbandos, or kakera)
* Snipe cards from other users’ rolls if they match your desired characters or surpass a default power threshold
* Keep track of pulled characters and automatically claim the best ones

This bot still uses the Discord API to interact with Mudae and is intended to run 24/7.

## Features

* **Auto roll** every hour with your preferred command
* **Auto claim** cards from your desired characters or series
* **Auto react** to preferred kakera (fully handled by the sniper)
* **Sniper** other users’ rolls:

  * Claim cards from desired characters (`desiredCharacters`)
  * Claim cards from desired series (`desiredSeries`)
  * Claim cards that meet or exceed a power threshold (`minPower`)
  * Fully configurable with booleans to toggle character/series/power sniping
* **Pull list** to track and prioritize character pulls
* **Repeat** all actions at the minute you prefer
* **Daily Kakera** triggers `/dk` automatically during rolls
* **BONUS** - Uses slash commands for native boosts (10% extra Kakera)
* **Silent rolling** – rolling function no longer prints logs; all tracking is centralized in the sniper

## Files

| File Name     | Purpose                            | Notes                                                                                                              |
| ------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `Vars.py`     | Stores user-configurable variables | Edit this file to set your bot preferences                                                                         |
| `Bot.py`      | Launches the bot                   | Execute this file to start the bot                                                                                 |
| `Function.py` | Contains all bot logic             | Modified from the original to fix crashes and add sniper/pull list features                                        |
| `Sniper.py`   | Snipes rolls from other users      | Reads all messages from Mudae (yours and others) and instantly claims desired characters or cards with 500+ Kakera |

## Requirements

* **Python 3.13.3**
* **Discum** – For Discord message management ([GitHub](https://github.com/Merubokkusu/Discord-S.C.U.M)). Install the latest version directly from GitHub:

```bash
pip install discum
```

* **Schedule** – For precise timed execution:

```bash
pip install schedule
```

> [!IMPORTANT]
> Before using the bot, you must run the `$help` command in your server once.
> This unlocks Mudae’s **slash commands**, which are required for the bot to function correctly.


## How to Set Up / Use

### Packages

Make sure Python 3 is installed along with Discum and Schedule.

### Variables (Vars.py)

Set your bot preferences and account info:

**Mandatory variables:**

* `token` – Your Discord account token
* `channelId` – The channel where the bot will roll
* `serverId` – The server/guild ID

**Optional variables:**

* `rollCommand` – Command for rolling (mx, ma, mg, wx, wg, wa, hx, ha, hg)
* `desiredKakeras` – Case-sensitive array of preferred kakera
* `desiredSeries` – Case-sensitive array of preferred series
* `desiredCharacters` – Array of characters to auto-claim with priority
* `pokeRoll` – Enable Pokeslot rolling (True/False)
* `repeatMinute` – Exact minute to perform rolls (00–59 eg. 11:30 → 12:30 → 1:30 → ...)
* `minPower` – Minimum power for sniper pull (default 500)
* `daily_kakera` - Toggle daily kakera command to be pulled every hour with simpleRoll()
* `catch_from_characters` – Toggle claiming by desired characters (True/False)
* `catch_from_series` – Toggle claiming by desired series (True/False)
* `catch_from_power` – Toggle claiming by power threshold (True/False)

**Example `Vars.py`:**

```python
token = 'YOUR_DISCORD_TOKEN'
channelId = '123456789012345678'
serverId = '987654321098765432'

rollCommand = 'wx'
desiredKakeras = ['kakeraP','kakeraY','kakeraO','kakeraR','kakeraW','kakeraL']
desiredSeries = ['One Piece','Dragon Ball Z','Death Note']
desiredCharacters = ['Luffy','Goku','Light Yagami']

pokeRoll = True
repeatMinute = '25'
minPower = 500

daily_kakera = True

# Sniper options (1. Characters > 2. Series > 3. Power)
catch_from_characters = True
catch_from_series = True
catch_from_power = True
```

### Execution

Run `Bot.py` to start the bot. It will log all rolls, claims, and sniper actions.

* Red heart → already claimed cards
* White heart → not claimed yet

### Possible Errors

> [!WARNING]
> Most issues come from **case sensitivity** or missing server settings. Double-check your `Vars.py` configuration and Mudae toggles before troubleshooting further.

* Mudae has no permission to read/write in the chosen channel
* Discord token may have changed
* Series/character names are case-sensitive
* Your account must have DMs with Mudae enabled

> [!IMPORTANT]
> The following **must** be enabled in Mudae for the bot to work properly:
>
> * `$togglestatistics`
> * `$togglekakstats`
> * `$togglekakerarolls`

## Advanced Features ("Fork" Update)

* **Sniper System** – Automatically claims cards from other users’ rolls based on:

  * Desired characters (`desiredCharacters`)
  * Desired series (`desiredSeries`)
  * Power threshold (`minPower`)
  * Fully configurable with booleans: `catch_from_characters`, `catch_from_series`, `catch_from_power`

* **Silent Roller** – Rolls cards and triggers daily Kakera without console output; all claiming and reactions handled by the sniper.

* **Series & Character Cleaning** – Removes trailing emojis and extra spaces to ensure reliable matching with your desired lists.

* **Pull List Management** – Tracks and prioritizes character pulls automatically.

* **All original features** from GDiazFentanes’ bot are preserved:
  
  * Auto roll every hour
  * Auto claim based on desired series
  * Auto react to preferred Kakera
  * Pokeslot rolling (`pokeRoll`)
  * Repeat actions at a chosen minute
  * Slash command support
  
* **Optional Multi-Bot Support:**

  * You can run multiple accounts simultaneously to maximize auto-claims, sniper pulls, and Kakera collection.