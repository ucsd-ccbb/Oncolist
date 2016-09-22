import os
import sys
import shutil
import datetime
import threading

import app
import ingest
from util import save_file_metadata, add_id

log = app.get_logger('dropbox')


class Dropbox(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.running = False
        self.files = {}

    def run(self):
        log.info('starting dropbox service')
        self.running = True

        # make dropbox directories, if necessary
        if not os.path.isdir(app.dropbox_path):
            os.makedirs(app.dropbox_path)
            log.info('created dropbox directory %s', app.dropbox_path)

        if not os.path.isdir(app.ingested_path):
            os.makedirs(app.ingested_path)
            log.info('created ingested directory %s', app.ingested_path)

        if not os.path.isdir(app.failed_path):
            os.makedirs(app.failed_path)
            log.info('created failed directory %s', app.failed_path)

        log.info('dropbox is monitoring {}'.format(app.dropbox_path))
        log.info('ingested files are moved to {}'.format(app.ingested_path))
        log.info('failed files are moved to {}'.format(app.failed_path))
        log.info('entering main loop')

        try:
            while self.running:
                # recursively walk the dropbox directory looking for files to ingest
                os.path.walk(app.dropbox_path, self.visit, None)

                # clean up entries after files have been processed and moved from the dropbox
                for filepath, processed in self.files.items():
                    if processed and not os.path.isfile(filepath):
                        del self.files[filepath]

                self.event.clear()
                self.event.wait(5)

        except KeyboardInterrupt:
            log.info('exiting main loop')

    def stop(self):
        log.info('stopping dropbox service')
        self.running = False
        self.event.set()

    def visit(self, _, dirname, names):
        for name in names:
            self.process(os.path.join(dirname, name))

    def process(self, filepath):
        # ignore hidden files (e.g., .gitignore)
        if not os.path.basename(filepath)[0] == '.':
            try:
                processed = self.files[filepath]
            except KeyError:
                log.info('new file in dropbox %s created %s', filepath, datetime.datetime.fromtimestamp(os.path.getctime(filepath)))
                processed = False

            if not processed and not os.path.basename(filepath) == '.gitignore':
                try:
                    _id = ingest.ingest(filepath)

                    # move file to ingested directory
                    dest = add_id(_id, os.path.join(app.ingested_path, os.path.basename(filepath)))
                    log.info('moving ingested file from %s to %s', filepath, dest)
                    shutil.move(filepath, dest)

                except Exception as e:
                    log.warn('failed to ingest %s', filepath)
                    log.warn(e)

                    _id = save_file_metadata(filepath, status='error')

                    # move file to failed directory
                    dest = add_id(_id, os.path.join(app.failed_path, os.path.basename(filepath)))
                    log.info('moving failed file from %s to %s', filepath, dest)
                    shutil.move(filepath, dest)

                processed = True

                self.files[filepath] = processed

    def upload(self, file, parser):
        filepath = os.path.join(app.dropbox_path, file.filename)
        _id = save_file_metadata(filepath, status='uploading', parser=parser)
        filepath = add_id(_id, filepath)
        file.save(filepath)
        log.info('uploaded {} as {}'.format(file.filename, filepath))
        _id = save_file_metadata(filepath, status='uploaded')
        self.event.set()
        return _id


dropbox = Dropbox()


if __name__ == '__main__':
    dropbox.start()
    print 'starting dropbox'
    print 'press ctrl-c to quit'
    try:
        while dropbox.isAlive():
            dropbox.join(10)
    except KeyboardInterrupt:
        log.info('keyboard interrupt')
        dropbox.stop()

    dropbox.join(60)
    sys.exit(0)