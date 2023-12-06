#   Products to sell:
# Coffee beans lists with links, Coffee capsules lists with links
# Main Web Page content, Custom built using HTML.
# Creation of SQL DataBases for each order.


# Web Page stored on ubuntu server.
# Customer Base
# Gathering information about the main suppliers & contacting them for contracts.
#
# Separate DataBases for each Supplier.
# Negotiation of the contracts.


#   Competitors:
#   Markets data:
#   Marketing Strategy
#


import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the source folder and replication folder
source_folder = "path_to_source_folder"
replication_folder = "path_to_replication_folder"


# Define a function to write logs
def write_log(log_type, source_path, replication_path, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (f"File name: {source_path}\nTime: {timestamp}\nType of operation: {log_type}\nSource Folder's "
                   f"initial text/files/code compared to current content inside the Replication folder:\n{content}\n\n")
    with open(replication_path, 'a') as log_file:
        log_file.write(log_message)


# Define a handler to monitor file system events
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        source_path = event.src_path
        replication_path = os.path.join(replication_folder, os.path.relpath(source_path, source_folder))

        if event.event_type == 'modified':
            with open(source_path, 'r') as source_file:
                source_content = source_file.read()
            with open(replication_path, 'r') as replication_file:
                replication_content = replication_file.read()
            if source_content != replication_content:
                write_log("Modified", source_path, replication_path, replication_content)

    def on_deleted(self, event):
        if event.is_directory:
            return
        source_path = event.src_path
        replication_path = os.path.join(replication_folder, os.path.relpath(source_path, source_folder))
        if event.event_type == 'deleted':
            with open(replication_path, 'r') as replication_file:
                replication_content = replication_file.read()
            write_log("Deleted", source_path, replication_path, replication_content)


if __name__ == "__main":
    # Initialize the observer and handler
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
