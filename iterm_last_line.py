#!/usr/bin/env python3

import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    #tab = window.current_tab
    tab = window.tabs[0]
    session = tab.current_session
    contents = await session.async_get_screen_contents()
    if contents.number_of_lines > 0:
        print(contents.line(contents.cursor_coord.y-1).string)

iterm2.run_until_complete(main)
#iterm2.run_forever(main)