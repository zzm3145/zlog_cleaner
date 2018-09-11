#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import glob
import re
import zipfile
import zlib
import logging
import logging.handlers

# Dir settings
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../')).replace('\\', '/')
log_dir = root_dir + '/logs/'
log_zip_dir = root_dir + '/logs/zip/'

# Behavior settings
# compress log files older than
zip_before = 3
# remove zip files ...
remove_old_zip = True
# .. that are older than
remove_before = 30

# Match pattern
re_date_log = re.compile(r'(.+)_(\d+)-.*')
re_date_zip = re.compile(r'(.+)_(\d+).*')


def clean_log():
    try:
        if not os.path.exists(log_zip_dir):
            os.makedirs(log_zip_dir)

        zip_date = datetime.datetime.now() + datetime.timedelta(days=-zip_before)
        for i in glob.glob(log_dir + '*'):
            if not os.path.isfile(i):  # File may be deleted by previous call
                continue

            basename = os.path.basename(i)
            log_info = re_date_log.search(basename)
            if not log_info:
                continue

            log_name_and_level = log_info.group(1)
            log_date = datetime.datetime.strptime(log_info.group(2), '%Y%m%d')

            if log_date < zip_date:
                log_names = log_name_and_level + '_' + log_info.group(2)
                try:
                    zf = zipfile.ZipFile(log_zip_dir + log_names + '.zip', mode='a',
                                         compression=zipfile.ZIP_DEFLATED)

                    for j in glob.glob(log_dir + '*' + log_names + '*'):
                        zf.write(j, os.path.basename(j))
                        os.remove(j)
                except Exception as e:
                    logging.error('Error processing %s %s' % log_name_and_level % e)
                finally:
                    zf.close()

        if remove_old_zip:
            remove_zip_before_date = datetime.datetime.now() + datetime.timedelta(days=-remove_before)
            for i in glob.glob(log_zip_dir + '*'):
                basename = os.path.basename(i)
                zip_info = re_date_zip.search(basename)
                if not zip_info:
                    logging.warning('Invalid name %s' % basename)
                    continue

                zip_date = datetime.datetime.strptime(zip_info.group(2), '%Y%m%d')

                if zip_date < remove_zip_before_date:
                    try:
                        os.remove(i)
                        logging.info('Removed %s' % basename)
                    except Exception as e:
                        logging.warning('Error processing %s ' % i % e)

    except Exception as e:
        logging.warning(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)-8s  %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir + 'logcleaner', 'D', 1, 0)
    file_handler.suffix = '_%Y%m%d-.log'
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)

    logging.info('Log cleaner start')
    clean_log()
