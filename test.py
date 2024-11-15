import curses

def choose(stdscr, question, options):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.curs_set(0)

    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, question, curses.A_BOLD)
        for idx, option in enumerate(options):
            color_pair = 2 if idx == current_row else 1
            stdscr.attron(curses.color_pair(color_pair))
            stdscr.addstr(idx + 1, 0, f"{'>' if idx == current_row else ' '} {option}")
            stdscr.attroff(curses.color_pair(color_pair))
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == ord("\n"):
            break

    return current_row

if __name__ == "__main__":
    answer = curses.wrapper(lambda stdscr: choose(stdscr, "Choose one of these options:" , ["Tell my name", "Tell my age", "Tell something funny"]))
    print(answer)
