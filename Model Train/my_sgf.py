import ego_resnet
import ego_io as eio
import sgf
import numpy as np
import time
import os
import shutil
import struct


sgf_src = './sgf_repo/raw_sgf/'
sgf_dst = './sgf_repo/recycle/'
dataset_path = './sgf_repo/human_dataset/'
ds_store = '.DS_Store'
def get_neightbour(pos):
    top = np.copy(pos)
    top[0] -= 1
    bot = np.copy(pos)
    bot[0] += 1
    left = np.copy(pos)
    left[1] -= 1
    right = np.copy(pos)
    right[1] += 1
    if pos[0] != 0 and pos[0] != 18 and pos[1] != 0 and pos[1] != 18:
        return [top, bot, left, right]
    elif pos[0] == 0 and pos[1] != 0 and pos[1] != 18:
        return [bot, left, right]
    elif pos[0] == 18 and pos[1] != 0 and pos[1] != 18:
        return [top, left, right]
    elif pos[0] != 0 and pos[0] != 18 and pos[1] == 0:
        return [top, bot, right]
    elif pos[0] != 0 and pos[0] != 18 and pos[1] == 18:
        return [top, bot, left]
    elif pos[0] == 0 and pos[1] == 0:
        return [bot, right]
    elif pos[0] == 0 and pos[1] == 18:
        return [bot, left]
    elif pos[0] == 18 and pos[1] == 0:
        return [top, right]
    elif pos[0] == 18 and pos[1] == 18:
        return [top, left]


def survive(board, pos):
    if board[pos[0], pos[1]] == 0:
        return True
    else:
        return False  # FIXME: ...


def move(board, pos, turn, check_flag = False):
    """

    :param board:  19x19 np.array int64
    :param pos:    2D np.array int64 (e.g. [10,15])
    :param turn:   whose turn to move; -1 or 1  make sure set the blank(empty) as 0
    :param check_flag:  True or False. whether to check the validation of the move. If set as False, assume the move
                        is valid.
    :return:      return a np.array.int64
                    Warning: If the check_flag is set as True and movement is invalid. This function change the content
                    of the original pointer. Thus, make sure dont use this function directly in a tree sturcture.
    """
    board0 = None
    if check_flag:
        board0 = np.copy(board)
    suicide_flag = True #  Forbidden position for suicide
    if check_flag and board[pos[0], pos[1]] != 0:
       # print("Invalid position to move.")
        
    
        return board0
    board[pos[0],pos[1]]=turn

    done = np.zeros((19, 19), np.int64)  # 0: Unsearched, 1: Searched
    done[pos[0], pos[1]] = 1
    nbr = get_neightbour(pos)
    for p in nbr:
        hp = False
        if board[p[0], p[1]] == 0 :
            suicide_flag = False
            continue
        if board[p[0], p[1]] == turn or done[p[0], p[1]] == 1:
            continue

        taken_cdt = []
        undone = []
        head = p
        search = head
        done[p[0], p[1]] = 1

        undone.append(search)
        taken_cdt.append(search)
        while (undone and hp == False):
            search = undone[-1]
            taken_cdt.append(search)
            del undone[-1]

            done[search[0], search[1]] = 1  # mark a node as searched

            temp = get_neightbour(search)

            for s in temp:
                piece = board[s[0], s[1]]
                if piece == 0:
                    hp = True
                    break
                elif piece != turn and done[s[0], s[1]] == 0:
                    undone.append(s)

        if hp == False:
            suicide_flag = False
            for tp in taken_cdt:
                board[tp[0], tp[1]] = 0

    if check_flag ==False:
        return board
    else:
        if suicide_flag ==False:
            return board
        done2 = np.zeros((19, 19), np.int64)  # 0: Unsearched, 1: Searched
        done2[pos[0], pos[1]] = 1
        hp2 = False
        for p2 in nbr:

            if board[p2[0], p2[1]] != turn:
                continue

            undone2 = []
            head2 = p2
            search2 = head2
            done2[p2[0], p2[1]] = 1

            undone2.append(search2)

            while (undone2 and hp2 == False):
                search2 = undone2[-1]

                del undone2[-1]

                done2[search2[0], search2[1]] = 1  # mark a node as searched

                temp2 = get_neightbour(search2)

                for s in temp2:
                    piece2 = board[s[0], s[1]]
                    if piece2 == 0:
                        hp2 = True
                        break
                    elif piece2 == turn and done2[s[0], s[1]] == 0:
                        undone2.append(s)
            if hp2:
                return board
      #  print("Invalid position to move.")
        
        
        return board0

def check_folder():
    if os.path.isdir('./sgf_repo') == False:
        print("** Initializing the sgf repo.")
        os.mkdir('sgf_repo')

    if os.path.isdir('./sgf_repo/recycle') == False:
        print("** Initializing the recycle bin.")
        os.mkdir('./sgf_repo/recycle')

    if os.path.isdir('./sgf_repo/raw_sgf') == False:
        print("** Initializing the raw sgf repo.")
        print("\nWarning: Please Prepare raw sgf first!!!\n")
        os.mkdir('./sgf_repo/raw_sgf')

    if os.path.isdir('./sgf_repo/human_dataset') == False:
        print("** Initializing the dataset repo for human games.")
        os.mkdir('./sgf_repo/human_dataset')


def get_rawlist():
    for path, dirs, files in os.walk('./sgf_repo/raw_sgf'):
        if path == './sgf_repo/raw_sgf':
            if len(files)>80:
                return files[0:80]
            else:
                return files
    return 0


def get_winner(root_node):
    winner_list = root_node.get('RE',None)
    if type(winner_list)!=list:

       return '-1'
    winner = winner_list[0][0]

    if winner == 'W':
        win = '1'
    elif winner == 'B':
        win = '0'
    else:

        return None
    return win

def translate_root(root_node):

    move_list = root_node.get('AB',None)
    ret_list = []

    for str0 in move_list:

        x = ord(str0[0]) - 97

        y = ord(str0[1]) - 97
        ret_list.append(np.array([x,y]))
    return ret_list


def translate(move_dict):

    white_move = move_dict.get("W",None)

    if white_move!=None:
        if white_move[0] == '':
            return None, None
        x = ord(white_move[0][0]) - 97
        y = ord(white_move[0][1]) - 97
        return np.array([x,y],dtype = np.int64), 1
    elif move_dict.get("B",None) !=None:
        black_move = move_dict.get("B",None)[0]

        if black_move == '':
            return None, None
        x = ord(black_move[0]) - 97
        y = ord(black_move[1]) - 97
        return np.array([x, y],dtype = np.int64), -1
    return None, None



def to_dataset(rawlist):
    count = 0
    dataset = []
    src_list =[]
    dst_list =[]

    for filename in rawlist:

        if filename == ds_store:
            continue

        with open(sgf_src + filename) as f:
            collection = sgf.parse(f.read())


        for game in collection:
            try:
                count += 1
                node_list = game.nodes

                dict = node_list[0].properties
                ha = dict.get("HA", ['0'])
                p_record = np.zeros((19, 19), np.int64)
                winner = get_winner(dict)
                if winner == '-1':
                    continue

                if ha[0] != '0':
                    ab_list = translate_root(dict)
                    for pos in ab_list:
                        p_record[pos[0], pos[1]] = -1

                n = len(game.nodes)

                for i in range(1, n, 1):

                    temp0 = np.copy(p_record)

                    node = node_list[i]

                    if node.first:

                        break
                    move_dict = node.properties
                    move_pos, turn = translate(move_dict)

                    if type(move_pos) == np.ndarray:
                        p_record = move(p_record, move_pos, turn, check_flag=True)
                        temp0[move_pos[0], move_pos[1]] = 2
                    else:

                        break
                    temp0 = temp0.ravel()
                    temp0 += 1
                    temp0 = list(map(str, temp0.tolist()))
                    temp0 = ','.join(temp0)
                    temp1 = str(turn)
                    temp2 = winner

                    sample = ';'.join([temp0, temp1, temp2])
                    sample += '\n'


                    dataset.append(sample)
            except:
                print("Exception.")
                continue
       
        src = ''.join([sgf_src,filename])
        dst = ''.join([sgf_dst,filename])

        src_list.append(src)
        dst_list.append(dst)
    time_now = time.time_ns()

    time_now = int(time_now)
    dataset = ''.join(dataset)
    dataset_name = "%shuman_set%d.dat"%(dataset_path,time_now)



    #dataset = struct.pack('b',dataset)
    dataset = dataset.encode('ASCII')

    with open(dataset_name,'wb') as f:
        f.write(dataset)

    for src_dir,dst_dir in zip(src_list,dst_list):
        shutil.move(src_dir,dst_dir)

    return dataset_name


def mcts_dataset(rawlist):
    count = 0
    dataset = []
    src_list =[]
    dst_list =[]

    for filename in rawlist:

        if filename == ds_store:
            continue

        with open(sgf_src + filename) as f:
            collection = sgf.parse(f.read())


        for game in collection:
            try:
                count += 1
                node_list = game.nodes

                dict = node_list[0].properties
                ha = dict.get("HA", ['0'])
                p_record = np.zeros((19, 19), np.int64)
                winner = get_winner(dict)
                if winner == '-1':
                    continue

                if ha[0] != '0':
                    ab_list = translate_root(dict)
                    for pos in ab_list:
                        p_record[pos[0], pos[1]] = -1

                n = len(game.nodes)

                for i in range(1, n, 1):

                    temp0 = np.copy(p_record)
                    print(temp0)
                    print('\n')

                    node = node_list[i]

                    if node.first:
                        break
                    move_dict = node.properties
                    move_pos, turn = translate(move_dict)
                    time.sleep(1)
                    if type(move_pos) == np.ndarray:
                        p_record = move(p_record, move_pos, turn, check_flag=True)
                        temp0[move_pos[0], move_pos[1]] = 2
                    else:

                        break
                    temp0 = temp0.ravel()
                    temp0 += 1
                    temp0 = list(map(str, temp0.tolist()))
                    temp0 = ','.join(temp0)
                    temp1 = str(turn)
                    temp2 = winner

                    sample = ';'.join([temp0, temp1, temp2])
                    sample += '\n'

                    dataset.append(sample)
            except:
                print("Exception.")
                continue
        src = ''.join([sgf_src,filename])
        dst = ''.join([sgf_dst,filename])

        src_list.append(src)
        dst_list.append(dst)
    time_now = time.time_ns()

    time_now = int(time_now)
    dataset = ''.join(dataset)
    dataset_name = "%sreinforce_set%d.dat"%("./sgf_repo/reinforce_learning/",time_now)



    #dataset = struct.pack('b',dataset)
    dataset = dataset.encode('ASCII')

    with open(dataset_name,'wb') as f:
        f.write(dataset)

    for src_dir,dst_dir in zip(src_list,dst_list):
        shutil.move(src_dir,dst_dir)


    return dataset_name


