import io
import requests
import os
from datetime import datetime, timedelta
import json
from pathlib import Path


def message_ids_load_last():
    STATE_FILE = Path("data/last_message_ids.json")
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except (json.JSONDecodeError, OSError):
        data = {}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return data


def message_ids_save_last(data):
    """Speichert das Dictionary mit message_ids in die JSON-Datei."""
    STATE_FILE = Path("data/last_message_ids.json")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def message_id_update_last(channel_id, message_id):
    """Aktualisiert die last_message_id für einen Thread und speichert sie."""
    data = message_ids_load_last()
    data[str(channel_id)] = str(message_id)
    message_ids_save_last(data)


def collect_messages(channel_id, message_limit):

    request_limit = min(message_limit, 100)

    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=" + str(request_limit)
    folder_path = 'data'
    file_path = os.path.join(folder_path, 'auth.txt')
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, mode='r', encoding='utf-8') as file:
        token = file.read()
        token = token.rstrip()
    access__token = {'authorization': token}

    r = requests.get(url, headers=access__token)
    r.raise_for_status()
    messages = json.loads(r.text)

    while len(messages) < message_limit:
        aelteste_message_id = messages[-1]["id"]
        url_before = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100&before={aelteste_message_id}"
        with open('data/auth.txt', mode='r', encoding='utf-8') as file:
            token = file.read()
            token = token.rstrip()
        access__token = {'authorization': token}
        req = requests.get(url_before, headers=access__token)
        req.raise_for_status()
        messages.extend(json.loads(req.text))
    return messages

def verarbeite_messages(printer_buffer, messages, download_path, continue_from_message_id = None):
    last_message_id = 0
    previous_last_message_encountered = False
    while messages:
        m = messages.pop()
        author = m["author"]["username"] + "#" + m["author"]["discriminator"]
        timestamp = m["timestamp"]
        content = m["content"]
        message_id = m["id"]
        last_message_id = message_id

        if continue_from_message_id is not None and continue_from_message_id == message_id:
            previous_last_message_encountered = True

        if not continue_from_message_id or previous_last_message_encountered:
            dt = datetime.fromisoformat(timestamp)
            dt = dt + timedelta(hours=2)
            timestamp_formatted = dt.strftime("%d.%m.%y-%H:%M")

            # save images if there are attachments
            attachment_files = []
            imgs_runtime = []
            for att in m.get("attachments", []):

                url = att["url"]  # direct CDN URL
                filename = att["filename"]      # get the attribute with title "filename" -> get original filename
                filename = str(message_id) + " - " + filename
                filepath = os.path.join(download_path, filename)

                # download the file
                img = requests.get(url)
                imgs_runtime.append(io.BytesIO(img.content))
                with open(filepath, "wb") as f:
                    print("file written: ", filepath)
                    f.write(img.content)

                attachment_files.append(filepath)

            printer_buffer.add_message(author, timestamp_formatted, content, message_id, imgs_runtime)
    return last_message_id