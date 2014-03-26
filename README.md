lrgx
====

lrgx is like UNIX 'less', but with less functionality, but with regex
colorization. Why? Because when I look at logs I want to see the lines
color-coded by process ID. So now I can do this:

    python lrgx.py --regex 'pid:[0-9]+' 34732.log

Interactive commands supported:

    UpArrow   = scroll one line up
    DownArrow = scroll one line down
    PageUp    = scroll one screen up
    PageDown  = scroll one screen down
    q         = quit
