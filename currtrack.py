#!/usr/bin/env python3
import sys
import argparse
import socket
from mpd import MPDClient # python-mpd2

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def strfobj(arg):
    if type(arg) != list:
        return str(arg)
    else:
        return strfobj(arg[0])

class Style:
    # default format
    f_s: str
    f_e: str
    # highlight
    hl_s: str
    hl_e: str
    # underline
    und_s: str
    und_e: str

def prettyartist(st: Style, arg):
    if type(arg) != list:
        return st.hl_s + str(arg) + st.hl_e
    else:
        res = st.hl_s
        for i in range(len(arg) - 1):
            if i != 0:
                res += st.hl_e + ", " + st.hl_s
            res += arg[i]
        res += st.hl_e + ' and ' + st.hl_s + arg[-1] + st.hl_e
        return res

def prettydate(st: Style, arg):
    return "%s(%s)%s" % (st.hl_s, strfobj(arg), st.hl_e)

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

    # fill in style vars depending on output
    st = Style()
    if xuncolored:
        # plain ASCII
        st.f_s,   st.f_e   = '',  ''
        st.hl_s,  st.hl_e  = '',  ''
        st.und_s, st.und_e = '"', '"'
    elif not xirc:
        # ANSI
        st.f_s,   st.f_e   = "\033[0;36m", "\033[0m"
        st.hl_s,  st.hl_e  = "\033[0m",    "\033[36m"
        st.und_s, st.und_e = "\033[0;4m",  "\033[0;36m"
    else:
        # IRC
        st.f_s,   st.f_e   = "\00310",   ""
        st.hl_s,  st.hl_e  = "\017",     "\00310"
        st.und_s, st.und_e = "\017\037", "\017\00310"


    #fsong = st.f_s + "♪⟪ "
    fsong = st.f_s + "♪ "

    if 'title' in csong:

        fsong += '"%s%s%s"' % (st.hl_s, csong['title'], st.hl_e)

        if 'album' in csong:
            if ('artist' in csong) and (('albumartist' not in csong) or (csong['artist'] != csong['albumartist'])):
                fsong += " by %s" % prettyartist(st, csong['artist'])

            fsong += " on %s%s%s" % (st.und_s, csong['album'], st.und_e)

            if 'date' in csong:
                fsong += " %s" % prettydate(st, csong['date'])

            if 'albumartist' in csong:
                fsong += " by %s" % prettyartist(st, csong['albumartist'])

        else:
            if 'date' in csong:
                fsong += " %s" % prettydate(st, csong['date'])

            if 'artist' in csong:
                fsong += " by %s" % prettyartist(st, csong['artist'])

    else:
        fname = csong['file']
        sindex = fname.rfind('/')

        fsong += st.hl_s

        if sindex >= 0:
            fsong += fname[sindex+1:]
        else:
            fsong += fname

        fsong += st.hl_e

    #fsong += " ⟫" + st.f_e
    fsong += st.f_e


    print(fsong)


if __name__ == "__main__":
    main()
