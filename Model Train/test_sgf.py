import numpy as np
import time
import my_sgf

B = -1  # black
N = 0  # none
W = 1  # white
# B and W do not matter when call the function. Because this is onyl a test file.
# But make sure set the blank(empty) as 0.

if __name__ == "__main__":
    """
     ------------------------------------------
     move(board, pos, turn, check_flag = False)
     ------------------------------------------
     
    :param board:  19x19 np.array
    :param pos:    2D np.array (e.g. [10,15])
    :param turn:   whose turn to move; -1 or 1  make sure set the blank(empty) as 0
    :param check_flag:  True or False. whether to check the validation of the move. If set as False, assume the move 
                        is valid.
    :return:      return a np.array.
                    Warning: If the check_flag is set as True and movement is invalid. This function change the content
                    of the original pointer. Thus, make sure dont use this function directly in a tree sturcture. 
"""
    print("start")

    brd = np.zeros((19, 19), np.int64)

    white_pos = np.array([1, 1],dtype = np.int64)
    brd[0,1]= -1
    brd[0, 2] = 1
    brd[0, 3] = 1
    brd[0, 4] = 1

    brd[1, 0] = -1
    brd[1, 2] = -1
    brd[1, 3] = -1
    brd[1, 4] = 1

    brd[2, 0] = 1
    brd[2, 1] = -1
    brd[2, 2] = -1
    brd[2, 3] = -1
    brd[2, 4] = 1

    brd[3, 1] = 1
    brd[3, 2] = 1
    brd[3, 3] = 1
    print("-"*20)
    print("     Before:")
    print("-" * 20)
    print(brd)
    print("Calculating 10000 times...\nPlease wait.")
    st =time.time()
    brd0=None
    for i in range(10000):
        brd0=np.copy(brd)
        ret = my_sgf.move(brd0,white_pos,W,check_flag=False)


    print("-" * 20)
    print("     After:")
    print("-" * 20)
    print(ret)
    ed = time.time()
    print("\nTime usage: %f s per 10000times" % (ed-st))


    time.sleep(2)
    print("\nExtreme test:")
    time.sleep(1)
    st=time.time()
    print("-" * 20)
    print("     Before:")
    print("-" * 20)

    brd2 = brd = np.zeros((19, 19), np.int64)
    brd2 += -1
    brd[9,9]=0
    white_pos = np.array([9, 9],dtype = np.int64)
    print(brd2)
    print("Calculating 10000 times...\nPlease wait.")
    for i in range(10000):
        my_sgf.move(brd2, white_pos, W)
    print("-" * 20)
    print("     After:")
    print("-" * 20)
    print(brd2)
    ed = time.time()
    print("\nTime usage: %f s per 10000 times" % (ed - st))
    
