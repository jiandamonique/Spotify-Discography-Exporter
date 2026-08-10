# Spotify-Discography-Exporter
Spotify Discography Exporter - Get a full list of every song you have on Spotify — titles, links, ISRCs, UPCs, copyright info, and more — in one spreadsheet.

Overview

If you're an artist on Spotify, this little tool asks Spotify (using your own free developer account) for a complete list of everything you've released — every album, single, and EP — and saves it as a CSV file (basically a spreadsheet) that you can open in Excel, Google Sheets, or Numbers.

For each song, you get:

- **Title**
- **Spotify link** (the URL you'd share to send someone straight to the song)
- **ISRC code** (optional) — a unique fingerprint code the music industry uses to identify your exact recording, useful for royalties, distribution, and licensing paperwork
- **Album/single name, type, and release date**
- **Album URL and album artwork URL**
- **UPC/EAN** — the barcode-style code for the release as a whole
- **Copyright line** — the ℗/© credit Spotify shows on the release
- **Duration** (mm:ss), **explicit flag**, **disc & track number**
- **Featured artists** on that specific track

Think of it as making your own backup/master list of your Spotify catalog — with the same technical detail you'd want for licensing paperwork or a distributor migration, not just titles and links.

**Want to skip the code entirely?** If you'd rather not touch GitHub, Colab, or anything code-related, there's a point-and-click version of this same tool: [artisanalindie.com/spotify-exporter.html](https://www.artisanalindie.com/spotify-exporter.html). Paste your artist link, get your CSV — same fields as below, no setup beyond the same one-time Client ID/Secret step.

A note on scope: this pulls everything Spotify's own API provides about your catalog. Things Spotify has no way of knowing — songwriter splits, BPM, musical key, sample clearances, lyrics status, whether you kept the stems — aren't in here, because that data doesn't live on Spotify. You'd still track those yourself, alongside this tool's output.

Step 1: Get your free Spotify "keys" (Client ID + Secret)

Think of these like a temporary ID badge that lets the script politely ask Spotify for your own public music data.

Go to developer.spotify.com/dashboard and log in with your normal Spotify account. It will recognize you as long as you were logged into your original account first.

Accept the Terms of Service.

Click "Create app"  

Fill in:
App name: ex:  "My Music Export"
App description: ex: Exporting my  catalog
Redirect URI: paste in https://localhost:8888/callback (will not be used -it's  a required field)
Which API/SDKs are you planning to use? check only "Web API"
Agree to the Developer Terms of Service checkbox if you have not yet (you likely cannot code until you do)
Click Save
You'll land on your app's page — you'll see your Client ID right there
Click "View client secret" to reveal your Client Secret

Keep this tab open — you'll need to copy/paste both values in a minute.

-

Step 2: Find your Spotify Artist ID

This is a unique code Spotify uses to identify your artist profile (different from your Client ID above).

Open Spotify (app or spotify.com) and go to your own artist profile
Click the "..." (three dots) → Share → Copy Link to Artist
You'll get a link that looks like mine @jiandamonique:
   https://open.spotify.com/artist/4zgJ2DkzPUebzvG6LevAdR
The long string after /artist/ — that's your Artist ID. You'll paste that in later too.

Step 3: Run the script in Google Colab (or your tool of choice)
For this use case --
Go to colab.research.google.com and sign in with any Google account
Click "New notebook"
In the first cell, paste this and press Shift+Enter:
   !pip install requests
Click "+ Code" to add a new cell, then paste in the entire contents of spotify_export.py (the file in this repo)
Press Shift+Enter to run it
It will ask you, one at a time:
Client ID → paste it in, press Enter
Client Secret → paste it in, press Enter (it'll show as dots)
Spotify Artist ID → paste it in, press Enter
Also fetch ISRC codes? → type y if you want them (a bit slower), or just press Enter to skip
Watch it work — it'll print out each album/single as it goes. It'll also grab UPC and copyright info for every release in the background (batched, so it's fast even for a big catalog).
When it's done, it'll say "Done!" and tell you where the file is. In Colab, it should also automatically start downloading the CSV to your computer's Downloads folder.

If the automatic download doesn't start, click the little folder icon on the left side of Colab, find spotify_tracks.csv, click the three dots next to it, and choose Download.

-Troubleshooting and Questions

"Invalid limit" error — Spotify changed some of their rules for new developer accounts in 2026. This script already accounts for that, but if Spotify changes things again and you see this error, try lowering the "limit": 10 values near the top of the script to something smaller, like 5.

Nothing happens when I try to type/paste the Client Secret — Click directly into the little input box that appears under the running cell first, then paste.

A red error message instead of a prompt — Something didn't paste correctly, or pip install requests didn't finish first. Re-run both cells in order.

It says my redirect URI isn't secure — Use https://localhost:8888/callback or http://127.0.0.1:8888/callback instead of plain http://.

Is this safe? Will Spotify disallow this?

This uses Spotify's own official, public Developer API — the same one thousands of apps use. You're only pulling public catalog information (titles, links, UPCs, copyright lines, and so on) that's already visible to anyone on Spotify. Your Client ID/Secret never leave your own computer/browser except to talk directly to Spotify's login servers.
If things change or elements are not available, it is likely Spotify made changes and improvements on their end. Feel free to let me know, we'll find a fix. :)

Credit / Notes

I built this for for independent artists like myself who want an easy, personal record of their own catalog — especially useful if you're ever migrating between distributors or just want a backup outside of Spotify's own dashboard.

Cheers!

Jianda Monique

Feel free to fork, modify, or share this with other artists who need the same thing.
