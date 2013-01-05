import random
import sys
import time
import shutil
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def pront(x): print x

def random_elt(xs):
    for i, x in enumerate(xs):
        if random.randint(0, i) == 0:
            c = x
    return c

class Culler (FileSystemEventHandler):
    def __init__(self, watch_dir, max_files, curr_count=0, strategy='new'):
        self.watch_dir = watch_dir
        self.max_files = max_files
        self.current_count = curr_count
        self.remove_file = {'new': self._rm_new, 
                            'random': self._rm_rand,
                            'old': self._rm_old}.get(strategy, self._rm_new)

    def on_created(self, ev):
        self.current_count += 1

        if not ev.is_directory and self.current_count > self.max_files:
            self.remove_file(ev.src_path)

    def _rm_new(self, path):
        os.remove(path)

    def _rm_rand(self, path):
        os.remove(random_elt(os.path.join(d, f)
            for d, dirs, fs in os.walk(self.watch_dir)
            for f in fs))

    def _rm_old(self, path):
        oldest_file, oldest_t = path, os.path.getatime(path)

        for d, dirs, fs in os.walk(self.watch_dir):
            fs_with_times = []
            for f in fs:
                f = os.path.join(d, f)
                fs_with_times.append((f, os.path.getatime(f)))

            old_f, old_t = min(fs_with_times, key=lambda (x,y): y)

            if old_t < oldest_t:
                oldest_file, oldest_t = old_f, old_t

        os.remove(oldest_file)

    def on_deleted(self, ev):
        self.current_count -= 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='No more clutter')
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', 
        default='.', help='The path you wish to watch. Defaults to current directory')

    parser.add_argument('--max', nargs='?', type=int, default=None,
        help='The maximum number of files allowed in the given directory tree. '
             'Defaults to the current number present.')

    parser.add_argument('--strategy', choices=['random', 'old', 'new'], type=str,
                        default='added', help='Control which file gets deleted when '
                        'a new file is added')

    args = parser.parse_args()

    watch_dir = args.path
    curr_count = len([f for t in os.walk(watch_dir) for f in t[2]])
    max_allowed = args.max if args.max is not None else curr_count

    culler = Culler(watch_dir, max_allowed, curr_count, args.strategy)

    observer = Observer()
    observer.schedule(culler, path=watch_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print
    observer.join()
