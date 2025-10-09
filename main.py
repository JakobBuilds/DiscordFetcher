import os
import csv
from src.Printer import PrinterBuffer
from src.DataHandler import collect_messages, verarbeite_messages, message_ids_load_last, message_id_update_last




def print_discord_thread(channel_id, message_limit, output_name, continue_only):

    download_path = "discord_thread_downloads/" + output_name
    os.makedirs(download_path, exist_ok=True)
    printer_buffer = PrinterBuffer(output_name)

    messages = collect_messages(channel_id, message_limit)

    last_message_id = None
    if continue_only:
        last_messages = message_ids_load_last()
        last_message_id = last_messages[str(channel_id)]
    new_last_message_id = verarbeite_messages(printer_buffer, messages, download_path, last_message_id)

    printer_buffer.build_pdf()
    if new_last_message_id is not None:
        message_id_update_last(channel_id, new_last_message_id)


def start_process():
    config = []
    with open("data/config.csv", mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)  # Verwendet die erste Zeile als Schlüssel
        for row in csv_reader:
            config.append(row)

    for row in config:
        channel_name = row['channel_name']
        channel_id = int(row['channel_id'])
        message_limit = int(row['message_limit'])
        continue_only = row['continue_only_01'] == '1'
        print_discord_thread(channel_id, message_limit, channel_name, continue_only)

start_process()

