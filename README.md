
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
* **Auto claim** cards from your desired series
* **Auto react** to preferred kakera
* **Sniper** other users’ rolls based on a desired list or minimum power (default >500)
* **Pull list** to track and prioritize character pulls
* **Repeat** all actions at the minute you prefer
* **Daily Kakera** does the /dk everytime it rolls, so it will get the daily Kakera for sure
* **BONUS** - Uses slash commands for native boosts (10% extra Kakera)

## Files

| File Name     | Purpose                            | Notes                                                                                                              |
| ------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `Vars.py`     | Stores user-configurable variables | Edit this file to set your bot preferences                                                                         |
| `Bot.py`      | Launches the bot                   | Execute this file to start the bot                                                                                 |
| `Function.py` | Contains all bot logic             | Modified from the original to fix crashes and add sniper/pull list features                                        |
| `Sniper.py`   | Snipes rolls from other users      | Reads all messages from Mudae (yours and others) and instantly claims desired characters or cards with 500+ Kakera |

## Requirements

* **Python 3.13.3**
* **Discum** – For Discord message management. Install the latest version directly from GitHub:

```bash
python -m pip install --user --upgrade git+https://github.com/Merubokkusu/Discord-S.C.U.M.git#egg=discum
```

* **Schedule** – For precise timed execution:

```bash
pip install schedule
```

For more information on Discum, check the [official GitHub repository](https://github.com/Merubokkusu/Discord-S.C.U.M).

---

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
* `pokeRoll` – Enable Pokeslot rolling (True/False)
* `repeatMinute` – Exact minute to perform rolls (00–59 eg. 11:30 -> 12:30 -> 1:30 -> ...)
* `desiredCharacters` – New: Array of characters to auto-claim with priority
* `minPower` – New: Minimum power for sniper pull (default 500)

**Example `Vars.py`:**

```python
token = 'YOUR_DISCORD_TOKEN'
channelId = '123456789012345678'
serverId = '987654321098765432'
rollCommand= 'wa'
desiredKakeras= ['kakeraP','kakeraY','kakeraO','kakeraR','kakeraW','kakeraL']
desiredSeries = ['One Piece','Dragon Ball Z','Death Note']
desiredCharacters = ['Luffy','Goku','Light Yagami']
pokeRoll = True
repeatMinute = '25'
minPower = 500
```

### Execution

Run `Bot.py` to start the bot. It will log all rolls, claims, and sniper actions.

* Red heart → already claimed cards
* White heart → not claimed yet

### Possible Errors

* Mudae has no permission to read/write in the chosen channel
* Discord token may have changed
* Series/character names are case-sensitive
* Your account must have DMs with Mudae enabled
* If the server does not display Kakera amounts or character info (name/series), the bot may fail to read messages or catch any rolls/cards properly.
  **At minimum, the following Mudae settings/commands must be enabled:**

  * `$togglestatistics`
  * `$togglekakstats`
  * `$togglekakerarolls`


## Advanced Features ("Fork" Update)

* **Sniper**: Automatically claim cards from other users if they match your `desiredCharacters` or exceed `minPower`
* **Pull List**: Tracks pulls and automatically claims the best available
* **All original features** from GDiazFentanes’ bot