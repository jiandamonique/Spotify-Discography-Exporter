"""
Spotify Discography Exporter
------------------------------
Pulls every album/single/EP + track for ANY Spotify artist and saves it
to a CSV -- including title, Spotify URL, and ISRC code.

HOW TO RUN (Google Colab):
1. Paste this whole script into a Colab code cell and run it (Shift+Enter).
2. When prompted, paste in:
     - Your Spotify Client ID
     - Your Spotify Client Secret
     - The Artist ID you want to export (see README for how to find one)
3. It creates spotify_tracks.csv and (in Colab) auto-downloads it to your
   computer's Downloads folder. If running locally, it saves in the same
   folder as this script.

HOW TO RUN (your own computer):
1. Install Python (python.org) if you don't have it.
2. In a terminal:  pip install requests
3. Run:  python spotify_export.py
4. Follow the same prompts as above.

Your Client ID/Secret are sent ONLY to Spotify's own login servers
(accounts.spotify.com) to get a temporary access token -- never anywhere else.
"""

import requests
import base64
import csv
import os
import time
import getpass


def get_access_token(client_id, client_secret):
    """Client Credentials flow -- fine for public catalog data (no user login needed)."""
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64_auth}"},
        data={"grant_type": "client_credentials"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_all_albums(artist_id, token):
    """Fetch every album/single/EP/compilation for the artist, handling pagination."""
    albums = []
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "include_groups": "album,single,compilation,appears_on",
        "limit": 10,          # Spotify's Dev Mode cap as of the Feb 2026 API changes
        "offset": 0,
        "market": "US",       # required by newer Dev Mode apps
    }
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"    [!] Request failed ({resp.status_code}): {resp.text}")
        resp.raise_for_status()
        data = resp.json()
        albums.extend(data["items"])
        url = data.get("next")
        params = None  # 'next' already has query params baked in
        time.sleep(0.1)

    return albums


def get_album_tracks(album_id, token):
    """Returns SIMPLIFIED track objects (no ISRC yet -- see get_track_isrc below)."""
    tracks = []
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    params = {"limit": 10, "offset": 0, "market": "US"}
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"    [!] Request failed ({resp.status_code}): {resp.text}")
        resp.raise_for_status()
        data = resp.json()
        tracks.extend(data["items"])
        url = data.get("next")
        params = None
        time.sleep(0.1)

    return tracks


def get_track_isrc(track_id, token):
    """
    ISRC only comes back on the FULL track object, not the simplified one
    from the album/tracks listing -- so this is one extra call per song.
    """
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params={"market": "US"})
    if resp.status_code != 200:
        return ""
    data = resp.json()
    return data.get("external_ids", {}).get("isrc", "")


def try_colab_download(filepath):
    """If running in Google Colab, trigger an automatic browser download."""
    try:
        from google.colab import files  # only exists inside Colab
        files.download(filepath)
        return True
    except ImportError:
        return False


def main():
    print("Spotify Discography Exporter")
    print("-----------------------------")
    client_id = input("Client ID: ").strip()
    client_secret = getpass.getpass("Client Secret (hidden as you type): ").strip()
    artist_id = input("Spotify Artist ID (from open.spotify.com/artist/...): ").strip()

    fetch_isrc = input("Also fetch ISRC codes? This is slower (one extra request "
                        "per song). [y/N]: ").strip().lower() == "y"

    print("\nGetting access token...")
    token = get_access_token(client_id, client_secret)

    print("Fetching all albums/singles/EPs...")
    albums = get_all_albums(artist_id, token)
    print(f"Found {len(albums)} releases.")

    seen_track_ids = set()
    rows = []
    file_number = 1

    for album in albums:
        album_name = album["name"]
        album_type = album["album_type"]
        release_date = album.get("release_date", "")
        album_url = album["external_urls"].get("spotify", "")

        print(f"  -> {album_name} ({album_type})")
        tracks = get_album_tracks(album["id"], token)

        for t in tracks:
            if t["id"] in seen_track_ids:
                continue  # skip duplicates (e.g. same single appearing in a compilation)
            seen_track_ids.add(t["id"])

            isrc = ""
            if fetch_isrc:
                isrc = get_track_isrc(t["id"], token)
                time.sleep(0.1)

            rows.append({
                "file_number": file_number,
                "title": t["name"],
                "spotify_track_id": t["id"],
                "spotify_url": t["external_urls"].get("spotify", ""),
                "isrc": isrc,
                "album_name": album_name,
                "album_type": album_type,
                "release_date": release_date,
                "album_url": album_url,
            })
            file_number += 1

    out_path = os.path.abspath("spotify_tracks.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "file_number", "title", "spotify_track_id", "spotify_url", "isrc",
            "album_name", "album_type", "release_date", "album_url",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! {len(rows)} unique tracks saved.")
    print(f"File location: {out_path}")

    downloaded = try_colab_download(out_path)
    if downloaded:
        print("(Running in Colab -- a download should have started in your browser.")
        print(" If it didn't, open the folder icon on the left sidebar and download")
        print(" spotify_tracks.csv from there manually.)")
    else:
        print("(Look for spotify_tracks.csv in the same folder you ran this script from.)")


if __name__ == "__main__":
    main()
