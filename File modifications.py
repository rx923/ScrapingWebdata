import atexit
import configparser
import datetime
import os
import signal
import threading
import time

import playsound
import psutil
import pygame
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Initialize pygame
pygame.mixer.init()


def play_sound(sound_file):
    if os.path.isfile(sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    else:
        print(
            f"Sound file {sound_file} does not exist. Events for this action will print to the screen but will play "
            f"no sound.")


# Flag to indicate whether the script should terminate
terminate_flag = False


# Function to get and validate a folder path from the user
def get_valid_folder_path(prompt):
    while True:
        folder_path = input(prompt)
        if os.path.isdir(folder_path):
            return folder_path
        else:
            print("Invalid folder path. Please provide a valid path.")


# Get the source folder from the user input
source_folder = get_valid_folder_path("Enter the source folder path: ")
# Get the replication folder from the user input
replication_folder = get_valid_folder_path("Enter the replication folder path: ")
# Define the script's duration in seconds (e.g., 3600 seconds for 1 hour)
script_duration = int(input("Enter the script duration in seconds: "))


def get_script_info():
    current_process = psutil.Process(os.getpid())  # Get the current process
    memory_info = current_process.memory_info()  # Get memory info
    script_path = os.path.abspath(__file__)  # Get the script file path

    print("Process ID:", current_process.pid)
    print("Script Path:", script_path)
    print("Memory Usage (RSS):", memory_info.rss, "bytes")
    print("Memory Usage (VMS):", memory_info.vms, "bytes")


# Function to handle script termination
def handle_script_termination(signum, frame):
    global terminate_flag
    print("Script is terminating...")
    # Add any cleanup code if needed
    terminate_flag = True


# Register signal handlers for termination signals (SIGTERM and SIGINT)
signal.signal(signal.SIGTERM, handle_script_termination)
signal.signal(signal.SIGINT, handle_script_termination)

# Load the configuration file
config = configparser.ConfigParser()
config.read("script.ini")

sound_files = {
    # Replace with the local path to your sound files
    "Modified": "C:\\Users\\user\\sound_files\\Modified.mp3",
    "Deleted": "C:\\Users\\user\\sound_files\\Deleted.mp3",
    "Added": "C:\\Users\\user\\sound_files\\Added.mp3",
    "Space Added": "C:\\Users\\user\\sound_files\\Space Added.mp3",
    "Space Removed": "C:\\Users\\user\\sound_files\\Space Removed.mp3"
}


# Define a function to write logs and trigger sounds
def write_log(log_type, source_path, replication_path, content):
    """
    Writes a log message for the specified operation and plays a sound.
    Args:
    log_type (str): The type of operation (e.g., "Modified", "Deleted", "Added", "Space Added", "Space Removed").
    source_path (str): The path of the source file.
    replication_path (str): The path of the replication file.
    content (str): The content of the replication file.

    This function writes a log message with a timestamp, appends it to a log file, and plays a sound based on the
    operation type.
    """

    # Define the log message
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (
        f"Type of operation: {log_type}\n"
        f"File name: {source_path(source_folder)}\n"
        f"Time: {timestamp}\n"
        f"Source Folder's initial text/files/code compared to current content inside the Replication folder:\n{content}"
        f"\n"
        f"\n"
    )

    # Write the log message to the replication folder
    with open(replication_path, 'a') as log_file:
        log_file.write(log_message)

    # Play a sound based on the operation type
    sound_file = sound_files.get(log_type)  # Get the sound file from the dictionary
    if sound_file is not None:
        playsound.playsound(sound_file)
    else:
        print(f"No sound file found for {log_type}")


class MyHandler(FileSystemEventHandler):
    """
    Custom event handler for monitoring file system events.
    This class handles file modification, deletion, addition, and space changes.
    """

    def __init__(self, _source_folder, _replication_folder, _sound_files):
        self._source_folder = source_folder
        self._replication_folder = replication_folder
        self._sound_files = sound_files
        super().__init__()

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_moved(self, event):
        pass

    def on_any_event(self, event):
        """
        Event handler for any file system event.
        """
        # Use os.walk() to check for the intended operations
        for root, dirs, files in os.walk(self._source_folder):
            for file in files:
                source_path = os.path.join(root, file)
                replication_path = os.path.join(self._replication_folder,
                                                os.path.relpath(source_path, self._source_folder))

                # Check for modified files
                if os.path.getmtime(source_path) != os.path.getmtime(replication_path):
                    write_log("Modified", source_path, replication_path, "")
                    playsound.playsound(self._sound_files["Modified"])

                # Check for deleted files
                if not os.path.exists(replication_path):
                    write_log("Deleted", source_path, replication_path, "")
                    playsound.playsound(self._sound_files["Deleted"])

                # Check for added files
                if not os.path.exists(source_path):
                    write_log("Added", source_path, replication_path, "")
                    playsound.playsound(self._sound_files["Added"])

            # Check for moved files
            for dir in dirs:
                source_dir = os.path.join(root, dir)
                replication_dir = os.path.join(self._replication_folder,
                                               os.path.relpath(source_dir, self._source_folder))

                if not os.path.exists(replication_dir):
                    write_log("Space Added", source_dir, replication_dir, "")
                    playsound.playsound(self._sound_files["Space Added"])

                elif not os.path.exists(source_dir):
                    write_log("Space Removed", source_dir, replication_dir, "")
                    playsound.playsound(self._sound_files["Space Removed"])


# Function to periodically check for file system events and process them

OBSERVER = "observer"


def check_for_events(observer, inner_event_handler):
    observer.schedule(inner_event_handler, path=source_folder, recursive=True)
    observer.start()

    try:
        while True:
            # Check for events every 0.25 seconds
            time.sleep(0.25)
            # Check if the script duration has expired
            if time.time() - start_time > script_duration:
                print("Script duration has expired.")
                observer.stop()
                break

    except KeyboardInterrupt:
        observer.stop()
        handle_script_termination(frame="", signum="")

    observer.join()


# Create the event handler
outer_event_handler = MyHandler(source_folder, replication_folder, sound_files)

# Start the event-checking thread
# event_thread = threading.Thread(target=lambda: check_for_events(outer_observer, outer_event_handler))
# event_thread.daemon = True  # Exit the thread when the main program exits
# event_thread.start()
outer_observer = Observer()
# Start time for script duration tracking
start_time = time.time()
# Create the observer instance and event_handler outside the function


# Start the event-checking thread
# event_thread = threading.Thread(target=check_for_events, args=(outer_observer, outer_event_handler))
# Exit the thread when the main program exits
# event_thread.daemon = True
# event_thread.start()

if __name__ == "__main":

    get_script_info()
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read("script.ini")
    # Get the values of the parameters from the configuration file
    replication_folder = config["script"]["replication_folder"]
    sound_files = config["script"]["sound_files"]
    source_folder = config["script"]["source_folder"]

    # Initialize the observer and handler
    event_handler = MyHandler(_replication_folder=replication_folder, _sound_files=sound_files,
                              _source_folder=source_folder)
    outer_observer = Observer()
    outer_observer.schedule(event_handler, path=source_folder, recursive=True)
    outer_observer.start()

    pygame.mixer.quit()
    atexit.register(pygame.mixer.quit)


    def lambda_check_for_events():
        check_for_events(outer_observer, outer_event_handler)


    event_thread = threading.Thread(target=lambda_check_for_events)
    event_thread.daemon = True  # Exit the thread when the main program exits
    event_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        outer_observer.stop()
        outer_observer.join()
    finally:
        outer_observer.stop()
        # Call the termination handler
        handle_script_termination(None, None)
        outer_observer.join()
