import os, time, sys
    
path = 'html_files'
now = time.time()
for f in os.listdir(path):
  if os.stat('html_files/'+f).st_mtime < now - 1 * 6400:
    if os.path.isfile('html_files/'+f):
       os.remove(os.path.join(path, f))