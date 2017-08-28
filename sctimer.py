#!/usr/bin/env python3
import time
import datetime
import curses 
import os
import argparse
from configparser import SafeConfigParser
from collections import namedtuple
import string
SCT_CONF_PATH=os.path.dirname(os.path.abspath(__file__))
SCT_CONF_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sctimer.conf')

#Initializing the curses module.
stdscr=curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.nodelay(1)

sct_parser=argparse.ArgumentParser(description='''
            **A terminal based timer for SpeedCubing***
            \n\r''')
sct_parser.add_argument('--countdown', action='store_true',
                help='Disable the countdown function.\n\r')
sct_parser.add_argument('-f', action='store', dest='filename',
                default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'times.txt'),
                help='Specify file where your solve times will be exported.')
sct_parser.add_argument('--stats', action='store_true',
                help='Return solve time stats.')
sct_parser.add_argument('--config', action='store', dest='cfgfile',
                help='Run SpeedCubingTimer using a different configuration file.')

sct_options = sct_parser.parse_args()

solves = []

def config():
    conf_parser=SafeConfigParser()
    if sct_options.cfgfile:
        if os.path.isfile(sct_options.cfgfile):
            conf_file=sct_options.cfgfile
        else:
            conf_file=SCT_CONF_FILE
            print('Configuration file {} not found. Using default conf file{}.\n'.format(sct_options.cfgfile, SCT_CONF_FILE))
    else:
        conf_file=SCT_CONF_FILE
    try:
        conf_parser.read(conf_file)
        try:
            countdown=conf_parser.getboolean('Countdown', 'Countdown_on')
        except ConfigParser.NoOptionError:
            countdown=True
        try:
            export=conf_parser.getboolean('Exporting', 'Export_always')
        except ConfigParser.NoOptionError:
            export=True
        try:
            filename=conf_parser.get('Exporting', 'Export_file')
        except ConfingParser.NoOptionError:
            filename='times.txt'
    except (ConfigParser.NoSectionError,
            ConfigParser.MissingSectionHeaderError):
        print('File {} contains no section headers.'.format(conf_file))
    Configuration=namedtuple('Config', 'countdown export filename')
    config=Configuration(countdown=countdown, export=export, filename=filename)
    return config

def countdown():
    try:
        key=None
        for num in range(15, 0, -1):
            if key!=ord(' '):
                key=stdscr.getch()
                if num !=0:
                    if num>9:
                        print ('{0}'.format(num), end="\r")
                    else:
                        print ('0'+'{0}'.format(num), end="\r")
                    time.sleep(1)
                else:
                    key=ord(' ')
            else:
                break
    except KeyboardInterrupt:
        termination_handler()

def time_format(time):
    if time == None:
    	return None
    x = lambda time: '{0:.2f}'.format(time) if time < 60 else '%d:%05.2f' % divmod(time, 60)
    return x(time)

def stopwatch(t):
    try:
        key=None
        while key!=ord(' '):
            key=stdscr.getch()
            print(time_format(t), end="\r")
            time.sleep(0.01)
            t+=0.01
        return t
    except KeyboardInterrupt:
        termination_handler()

def avg_x(solves_num, filepath):
    BLKSIZE=4096
    buff=''
    if not filepath.seekable():
        return
    with open(filepath, 'r') as times_file:
        times_file.seek(0, 2)
        lastchar=times_file.read(1)
        trailing_newline=(lastchar=='\n')
        while 1:
            newline_pos=buf.find('\n')
            pos=times_file.tell()
            if newline_pos!=-1:
                # Found a newline
                line = buf[newline_pos+1:]
                buf = buf[:newline_pos]
                if pos or newline_pos or trailing_newline:
                    line+='\n'
                yield line
            elif pos:
                # Need to fill buffer
                toread=min(BLKSIZE, pos)
                times_file.seek(-toread, 0)
                buf+=times_file.read(toread)
                times_file.seek(-toread, 0)
                if pos==toread:
                    buf='\n'+buf
            else:
                return

def export_times(filepath, current_solves):
    with open(filepath, 'w' if not os.path.isfile(filepath) else 'a') as times_file:
        times_file.write(str(datetime.datetime.now().date())+': '+str(current_solves)+'\n')

#Terminating properly the application by reversing the 'curses' settings
def termination_handler():
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    raise SystemExit

def main():
    export_file=sct_options.filename if sct_options.filename else config().filename
    if sct_options.stats:
        for line in avg_x(5, export_file):
            print(eval(line))
        termination_handler()
    else:
        while 1:
            try:
                key=stdscr.getch()
                if key==ord(' '):   #The solve count starts after pressing SPACEBAR
                    if not sct_options.countdown and config().countdown:
                        countdown()
                    solves.append(time_format(stopwatch(0.00)))
                    print ("\rYour solves for this session: {0}".format(solves), end="\n\r")
                elif key==27:       #The application exits after pressing ESCAPE
                    if config().export and len(solves)>0:
                        export_times(export_file, solves)
                        termination_handler()
            except KeyboardInterrupt:
                termination_handler()
    
if __name__=="__main__":
    main()
