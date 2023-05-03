#!/usr/bin/env python3

import iterm2
import sys

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    # Optional first param is the index of the terminal tab to use, defaulting to the current tab
    if len(sys.argv) > 1:
        tab = window.tabs[int(sys.argv[1])]
    else:
        tab = window.current_tab
    session = tab.current_session
    contents = await session.async_get_screen_contents()
    if contents.cursor_coord.y < contents.number_of_lines:
        print(contents.line(contents.cursor_coord.y-1).string)
    elif contents.number_of_lines > 0:
        print(contents.line(contents.number_of_lines-2).string)

iterm2.run_until_complete(main)
#iterm2.run_forever(main)