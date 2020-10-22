#!/usr/bin/env python3
import sys
import argparse
import socket
from mpd import MPDClient

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def strfobj(arg):
    if type(arg) != list:
        return str(arg)
    else:
        return strfobj(arg[0])

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', default='localhost', dest='host')
    parser.add_argument('-p', '--port', default=6600, type=int, dest='port')
    parser.add_argument('-i', '--irc', action='store_const', const=True, default=False, dest='irc')
    parser.add_argument('-u', '--uncolored', action='store_const', const=True, default=False, dest='uncolored')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, dest='verbose')
    parser.add_argument('--help', action='help')
    args = parser.parse_args()

    xhost      = args.host
    xport      = args.port
    xirc       = args.irc
    xuncolored = args.uncolored
    xverbose   = args.verbose


    client = MPDClient()

    client.timeout = 10
    client.idletimeout = None

    shost = xhost.split('@', 1)
    nhost, passw = None, None
    if len(shost) != 2:
        nhost = xhost
    else:
        nhost, passw = shost[1], shost[0]

    try:
        client.connect(nhost, xport)
        if passw:
            client.password(passw)
    except socket.timeout:
        if xverbose:
            eprint("err: socket.timeout")
        sys.exit(1)
    except socket.gaierror:
        if xverbose:
            eprint("err: socket.gaierror")
        sys.exit(1)
    except socket.error:
        if xverbose:
            eprint("err: socket.error")
        sys.exit(1)

    csong = client.currentsong()
    if xverbose:
        eprint(csong)
    if len(csong) <= 0:
        # nothing playing right now
        sys.exit(0)

    f_s, f_e = None, None
    hl_s, hl_e = None, None
    und_s, und_e = None, None
    if xuncolored:
        f_s, f_e = "", ""
        hl_s, hl_e = "", ""
        und_s, und_e = "\"", "\""
    elif not xirc:
        f_s, f_e = "\033[0;36m", "\033[0m"
        hl_s, hl_e = "\033[0m", "\033[36m"
        und_s, und_e = "\033[0;4m", "\033[0;36m"
    else:
        f_s, f_e = "\00310", ""
        hl_s, hl_e = "\017", "\00310"
        und_s, und_e = "\017\037", "\017\00310"
    #fsong = f_s + "♪⟪ "
    fsong = f_s + "♪ "
    if 'title' in csong:
        fsong += "\"%s%s%s\"" % (hl_s, csong['title'], hl_e)
        if 'album' in csong:
            if ('artist' in csong) and (('albumartist' not in csong) or (csong['artist'] != csong['albumartist'])):
                fsong += " by %s%s%s" % (hl_s, csong['artist'], hl_e)
            fsong += " on %s%s%s" % (und_s, csong['album'], und_e)
            if 'date' in csong:
                fsong += " %s(%s)%s" % (hl_s, strfobj(csong['date']), hl_e)
            if 'albumartist' in csong:
                fsong += " by %s%s%s" % (hl_s, csong['albumartist'], hl_e)
        else:
            if 'date' in csong:
                fsong += " %s(%s)%s" % (hl_s, strfobj(csong['date']), hl_e)
            if 'artist' in csong:
                fsong += " by %s%s%s" % (hl_s, csong['artist'], hl_e)
    else:
        fname = csong['file']
        sindex = fname.rfind('/')
        fsong += hl_s
        if sindex >= 0:
            fsong += fname[sindex+1:]
        else:
            fsong += fname
        fsong += hl_e
    #fsong += " ⟫" + f_e
    fsong += f_e

    print(fsong)


if __name__ == "__main__":
    main()
