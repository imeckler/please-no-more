import sys
import time
import shutil
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Culler (FileSystemEventHandler):
    def __init__(self, max_files, curr_count=0):
        self.max_files = max_files
        self.current_count = curr_count

    def on_created(self, ev):
        self.current_count += 1

        if not ev.is_directory:
            if self.current_count > self.max_files:
                os.remove(ev.src_path)

    def on_deleted(self, ev):
        self.current_count -= 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='No more clutter')
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', 
        default='.', help='The path you wish to watch. Defaults to current directory')

    parser.add_argument('--max', nargs='?', type=int, default=None,
        help='The maximum number of files allowed in the given directory tree. '
             'Defaults to the current number present.')

    args = parser.parse_args()

    watch_path = args.path
    curr_count = len([f for t in os.walk(watch_path) for f in t[2]])
    max_allowed = args.max if args.max is not None else curr_count

    culler = Culler(max_allowed, curr_count)

    observer = Observer()
    observer.schedule(culler, path=watch_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()