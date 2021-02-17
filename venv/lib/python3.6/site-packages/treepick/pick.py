import os
import cgitb
import curses
from .paths import Paths
from .keys import parse
from .color import Color

# Get more detailed traceback reports
cgitb.enable(format="text")  # https://pymotw.com/2/cgitb/


def process(screen, parent, action, curline):
    '''
    Traverse parent object & process the action returned from keys.parse
    '''
    line = 0
    for child, depth in parent.traverse():
        if depth == 0:
            continue  # don't process root node
        if line == curline:
            if action == 'expand':
                curline = child.expand(curline)
            elif action == 'expand_all':
                curline = child.expand(curline, recurse=True)
            elif action == 'toggle_expand':
                curline = child.expand(curline, toggle=True)
            elif action == 'collapse':
                curline = child.collapse(parent, curline, depth)
            elif action == 'collapse_all':
                curline = child.collapse(parent, curline, depth, recurse=True)
            elif action == 'toggle_pick':
                curline = child.pick(curline)
            elif action == 'pickall':
                curline = child.pick(curline, parent)
            elif action == 'nextparent':
                curline = child.nextparent(parent, curline, depth)
            elif action == 'prevparent':
                curline = child.prevparent(parent, curline, depth)[0]
            elif action == 'getsize':
                curline = child.getsize(curline, parent)
            elif action == 'getsizeall':
                curline = child.getsize(curline, parent, sizeall=True)
            action = None  # reset action
        line += 1  # keep scrolling!
    return curline, line


def get_picked(relative, root, picked):
    if relative:
        if root.endswith(os.path.sep):
            length = len(root)
        else:
            length = len(root + os.path.sep)
        return [p[length:] for p in picked]
    return picked


def showpicks(win, picked):
    win.erase()
    win.attrset(curses.color_pair(0))
    try:
        if picked:
            win.chgat(0, 0, curses.color_pair(3) | curses.A_BOLD)
            win.addstr(0, 0, "\n".join(picked))
            win.addstr(len(picked) + 1, 0, "Press any key to return.")
            win.chgat(len(picked) + 1, 0, curses.color_pair(3) | curses.A_BOLD)
        else:
            win.addstr(0, 0, "You haven't picked anything yet!")
            win.chgat(0, 0, curses.color_pair(1) | curses.A_BOLD)
            win.addstr(2, 0, "Press any key to return.")
            win.chgat(2, 0, curses.color_pair(3) | curses.A_BOLD)
    except curses.error:
        pass
    win.getch()


def mkheader(screen, y, x):
    Color(screen)
    header = curses.newwin(0, x, 0, 0)
    msg = "[hjkl/HJKL] move/jump [SPC/v/:] pick/all/glob [s/S] size/all [TAB] expand"
    startch = [i for i, ltr in enumerate(msg) if ltr == "["]
    endch = [i for i, ltr in enumerate(msg) if ltr == "]"]
    try:
        header.addstr(0, 0, msg)
        for i in range(len(startch)):
            header.chgat(0, startch[i], endch[i] - startch[i] + 1,
                         curses.A_BOLD | curses.color_pair(3))
    except curses.error:
        pass
    screen.refresh()
    header.refresh()
    return header


def mkfooter(screen, y, x):
    Color(screen)
    footer = curses.newwin(0, x, y - 1, 0)
    msg = "[?] show keys [.] toggle hidden [/] find [p] view picks [r] reset [q] quit"
    startch = [i for i, ltr in enumerate(msg) if ltr == "["]
    endch = [i for i, ltr in enumerate(msg) if ltr == "]"]
    try:
        footer.addstr(0, 0, msg)
        for i in range(len(startch)):
            footer.chgat(0, startch[i], endch[i] - startch[i] + 1,
                         curses.A_BOLD | curses.color_pair(3))
    except curses.error:
        pass
    screen.refresh()
    footer.refresh()
    return footer


def txtbox(screen, footer, prompt):
    from curses.textpad import Textbox
    length = len(prompt)
    y, x = screen.getmaxyx()
    footer.erase()
    footer.addstr(prompt)
    footer.chgat(0, 0, length, curses.A_BOLD | curses.color_pair(3))
    curses.curs_set(1)
    footer.refresh()
    tb = footer.subwin(y - 1, length)
    box = Textbox(tb)
    box.edit()
    curses.curs_set(0)
    mkfooter(screen, y, x)
    return box.gather()


def reset(win, root, hidden, picked):
    parent = Paths(win, root, hidden, picked=picked,
                   expanded=set([root]), sized=dict())
    action = None
    curline = 0
    return parent, action, curline


def init(screen, win=None, resize=False):
    screen.erase()
    curses.curs_set(0)  # get rid of cursor
    y, x = screen.getmaxyx()
    header = mkheader(screen, y, x)
    footer = mkfooter(screen, y, x)
    if resize:
        win.resize(y - 3, x)
    else:
        win = curses.newwin(y - 3, x, 2, 0)
    screen.refresh()
    win.refresh()
    return header, win, footer


def pick(screen, root, hidden=True, relative=False, picked=[]):
    picked = [root + p for p in picked]
    header, win, footer = init(screen)
    parent, action, curline = reset(win, root, hidden, picked)
    lastpath, lasthidden = (None,)*2
    matches = []
    while True:
        # to reset or toggle view of dotfiles we need to create a new Path
        # object before erasing the screen & descending into process function.
        if action == 'reset':
            parent, action, curline = reset(win, root, hidden, picked=[])
        elif action == 'toggle_hidden':
            if parent.hidden:
                # keep two copies of record so we can restore from state when
                # re-hiding
                curpath, lastpath = (parent.children[curline],)*2
                # this needs to be reset otherwise we use the old objects
                parent.paths = None
                parent.hidden = False
                parent.drawtree(curline)
                curline = parent.children.index(curpath)
                if lastpath and lasthidden in parent.children:
                    curline = parent.children.index(lasthidden)
                else:
                    curline = parent.children.index(curpath)
            else:
                # keep two copies of record so we can restore from state
                curpath, lasthidden = (parent.children[curline],)*2
                parent.paths = None
                parent.hidden = True
                parent.drawtree(curline)
                if curpath in parent.children:
                    curline = parent.children.index(curpath)
                elif lastpath:
                    curline = parent.children.index(lastpath)
            action = None
            continue
        elif action == 'find':
            string = txtbox(screen, footer, "Find: ").strip()
            if string:
                curline, matches = parent.find(curline, string)
        elif action == 'findnext':
            curline = parent.findnext(curline, matches)
        elif action == 'findprev':
            curline = parent.findprev(curline, matches)
        elif action == 'match':
            globs = txtbox(screen, footer, "Pick: ").strip().split()
            if globs:
                parent.pick(curline, parent, globs)
        elif action == 'resize':
            screen.erase()
            win.erase()
            init(screen, win=win, resize=True)
        elif action == 'showpicks':
            showpicks(win, get_picked(relative, root, parent.picked))
        elif action == 'quit':
            return get_picked(relative, root, parent.picked)
        curline, line = process(screen, parent, action, curline)
        parent.drawtree(curline)
        action, curline = parse(screen, win, curline, line)
