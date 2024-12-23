"""
File: frogger.py
Author: Daniel Okuwa
Date: THE DATE
Section: 11
E-mail: dokuwa1@umbc.edu
Description: Frogger yay!
"""

import os
import random

# Main map identifiers
FROG_SPOT = "O"
EMPTY_SPOT = "_" # Frog can move here
TAKEN_SPOT = "X" # Frog can move here, but dies
DEAD_SPOT = "!" # Frog died here
GOAL_SPOT = '$' # Land here to win

# Emoji stuff just for the fun of it
FROG_ICON = "🐸"
DEAD_ICON = '💀'
EMPTY_ICON = '⬛'
GOAL_ICON = '🟩'
CAR_ICONS = [
    '🟧',
    '🟨',
    '🟦',
    '🟪',
    '🟫',
]

def select_game_file():
    """
    Determine file to load based on user input

    :return: file
    """

    root, directories, files = next(os.walk('.'))
    maps = [i for i in files if 'frog' in i]

    for i in range(len(maps)):
        print(f'[{i+1}]\t{maps[i]}')

    chosen_file = input("Choose a number or filename: ")

    for i in maps:
        title = i.split('.')[0]
        if chosen_file == "game" + title[-1]:
            return i

    if chosen_file.isnumeric():
        chosen_file = int(chosen_file)

        if chosen_file > 0 and chosen_file <= len(maps):
            return maps[chosen_file-1]

    print("Unable to load file")

    return


def display_board(board):
    b = ''

    for line in board:
        for spot in line:
            b += spot

        b += '\n'

    print(b)


def get_frog_pos(board):
    """
    Returns the x and y coordinates of the frog's location on the board

    :param board:
    :return: list
    """

    for col in range(len(board)):
        for row in range(len(board[0])):
            if board[col][row] == FROG_SPOT or board[col][row] == DEAD_SPOT:
                return [row, col]


def get_player_move(board, can_jump):
    moves = {'w': [0, -1], 's': [0, 1], 'a': [-1, 0], 'd': [1, 0]}
    move = input('w - up, s - down, a - left, d - right, j - jump to: ').lower()

    while move != 'w' and move != 's' and move != 'a' and move != 'd' and move != 'j':
        move = input('Invalid input!\nw - up, s - down, a - left, d - right, j - jump to: ').lower()

    if move == 'j':
        if can_jump:
            print("NOTE: You can only jump 1 row at most!")
            move = input('Input coordinates to jump to (row col): ')
            move = [int(i)-1 for i in move.split(' ') if i != '']

            frog_pos = get_frog_pos(board)

            if frog_pos == move:
                print('Target spot is current spot, no jumps used!')
                return [0, 0], False

            if abs(frog_pos[1] - move[1]) > 1:
                print('Cannot jump more than 1 row!')
                return [0, 0], False

            return move, True
        else:
            print("No more remaining jumps!")
            return [0, 0], False

    return moves[move], False


def next_board(player_move, boards, car_speed, jumped):
    board = boards[0]
    board_display = boards[1]
    frog_pos = get_frog_pos(board)
    target_pos = None

    if jumped:
        # Absolute position on board
        target_pos = player_move
    else:
        # Relative position from frog
        target_pos = [frog_pos[0] + player_move[0], frog_pos[1] + player_move[1]]

    if (target_pos[0] < 0 or target_pos[0] >= len(board[0])) or (target_pos[1] < 0 or target_pos[1] >= len(board)):
        print("Out of bounds!")
        target_pos = frog_pos

    # Remove frog
    frog_pos = get_frog_pos(board)
    board[frog_pos[1]][frog_pos[0]] = EMPTY_SPOT
    board_display[frog_pos[1]][frog_pos[0]] = EMPTY_ICON

    # Rotate board
    for i in range(1, len(board) - 1):
        row_speed = car_speed[i-1]
        board[i] = board[i][-row_speed:] + board[i][:-row_speed]
        board_display[i] = board_display[i][-row_speed:] + board_display[i][:-row_speed]

    # Add frog
    if board[target_pos[1]][target_pos[0]] == TAKEN_SPOT:
        board[target_pos[1]][target_pos[0]] = DEAD_SPOT
        board_display[target_pos[1]][target_pos[0]] = DEAD_ICON
    else:
        board[target_pos[1]][target_pos[0]] = FROG_SPOT
        board_display[target_pos[1]][target_pos[0]] = FROG_ICON

    return board, board_display


def frogger_game(selected_game_file):
    """

    Core game loop

    :param selected_game_file:
    :return:
    """

    if not selected_game_file: return

    print('Loading', selected_game_file)

    with (open(selected_game_file) as file):
        # Init
        settings = {
            "frog": file.readline().strip('\n'),
            "car_speed": [int(i) for i in file.readline().strip('\n').split(' ')],
            "board": [[spot for spot in line.strip('\n')] for line in file.readlines()],
        }

        board = settings['board']
        board_display = []
        line_length = len(settings['board'][0])
        remaining_jumps = int(settings['frog'][2])

        # Frog Spawn
        starting_line = [EMPTY_SPOT for _ in range(line_length)]
        starting_spot = line_length // 2
        starting_line[starting_spot] = FROG_SPOT
        board.insert(0, starting_line)

        # Finish line
        goal_line = [GOAL_SPOT for _ in range(line_length)]
        board.append(goal_line)

        '''
                    Idea: Just for fun, add colors to the cars

                    Example:

                    1 [XXX__XX___XX____]
                    2 [XX__XX___XXX__X_]
                    3 [_XX__XXXX_XX_XX_]

                    1 🟪🟪🟪⬛⬛🟫🟫⬛⬛⬛🟫🟫⬛⬛⬛⬛
                    2 🟧🟧⬛⬛🟪🟪⬛⬛⬛🟦🟦🟦⬛⬛🟪⬛
                    3 ⬛🟨🟨⬛⬛🟪🟪🟪🟪⬛🟨🟨⬛🟧🟧⬛

                    Maybe fill empty spaces with ⬛
                '''

        board_split = []

        for line in board:
            l = [

                # Add first spot for each line
                [
                    line[0]
                ]
            ]
            curr_index = 0

            for i in range(1, len(line)):
                last_spot = line[i - 1]
                curr_spot = line[i]

                if last_spot == curr_spot:
                    l[curr_index].append(curr_spot)
                else:
                    l.append([])
                    curr_index += 1
                    l[curr_index].append(curr_spot)

            board_split.append(l)

        for y in range(len(board_split)):
            line = board_split[y]
            new_line = []

            for x in range(len(line)):
                block = line[x]
                first_spot = block[0]
                target = None

                if first_spot == TAKEN_SPOT:
                    color = CAR_ICONS[random.randint(0, len(CAR_ICONS) - 1)]

                    for _ in block:
                        new_line.append(color)
                else:
                    if first_spot == DEAD_SPOT:
                        target = DEAD_ICON
                    elif first_spot == EMPTY_SPOT:
                        target = EMPTY_ICON
                    elif first_spot == GOAL_SPOT:
                        target = GOAL_ICON
                    elif first_spot == FROG_SPOT:
                        target = FROG_ICON

                    for _ in block:
                        new_line.append(target)

            board_display.append(new_line)

        display_board(board_display)
        print(f"Remaining jumps: {remaining_jumps}")

        # Core game loop
        GAMEOVER = False

        while not GAMEOVER:
            move, jumped = get_player_move(board, remaining_jumps >= 1)

            if jumped:
                remaining_jumps -= 1
                print(f"Remaining jumps: {remaining_jumps}")

            board, board_display = next_board(move, [board, board_display], settings['car_speed'], jumped)
            display_board(board_display)

            frog_pos = get_frog_pos(board)

            if board[frog_pos[1]][frog_pos[0]] == DEAD_SPOT:
                print('You lose, Sorry Frog')
                GAMEOVER = True

            if frog_pos[1] + 1 == len(board):
                print("You won, Frog lives to cross another day")
                GAMEOVER = True


if __name__ == "__main__":
    selected_game_file = select_game_file()
    frogger_game(selected_game_file)