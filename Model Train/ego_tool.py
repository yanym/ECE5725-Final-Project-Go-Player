import numpy as np
import ego_resnet as enn
import os
import my_sgf as mysgf
import random

def folder_check():
    if os.path.isdir('./checkpoint_repo')==False:
        print("** Initializing the checkpoint repo.")
        os.mkdir('checkpoint_repo')
    if os.path.exists('./checkpoint_repo/ego_checkpoint0.ckpt') == False:
        print("** Ego Warning: No checkpoint (weights) files available in the default path.")
        print("   Please move the ego_checkpoint(all three files) to './checkpoint_repo/'")


def predict_init(weights_path = './checkpoint_repo/ego_checkpoint0.ckpt'):
    folder_check()
    model = enn.train_init()
    model.load_weights(weights_path)
    return model

def ego_predict(model, x0, x1, color_reverse=False):
    """

     *** Black: 1, White: -1, Blank(empty): 0
        Use para'color_reverse' to reset (Black <==> White,)

    :param model: Initialize a raw model
    :param x0:  array 19x19 (both list or numpy.adarray are fine.)
    :param x1: -1 or 1, who's turn to move. Black -1 and White 1
    :return: ** Two returns: Priority(best 9 moves): dict { tuple: float}
                              A winrate in float
    """
    input0 = np.array([x0],dtype=np.float32)
    input0 = input0.reshape((1,19,19,1))
    input1 = np.array([[x1]],dtype=np.float32)
    if color_reverse:
        input0 *= -1
        input1 *= -1
    p = model.predict({'ego_input0': input0, 'ego_input1': input1})
    prob_arr = p[0][0]
    winrate = p[1][0][0]
    arr_sum = np.sum(prob_arr)
    prob_arr = prob_arr / arr_sum
    move_sort = np.copy(prob_arr)

    move_sort = move_sort * (-1.0)
    idx = np.argsort(move_sort)
    x_arr = np.copy(idx)
    y_arr = np.copy(idx)
    y_arr = y_arr%19
    x_arr = x_arr/19
    x_arr=x_arr.astype(np.int64)

    dict={}
    for i in range(9):
        dict[(x_arr[i],y_arr[i])] =prob_arr[i]
    return dict, winrate


class Pymcts:
    def __init__(self,p_parent):
        self.move =None
        self.parent = p_parent
        self.board = None
        self.winrate = None
        self.child = []
        self.child_move = None
        self.nvisit =0
        self.turn = 0


    def get_parent(self):
        return self.parent

    def extend(self,move,model):
        p_child= Pymcts(self)
        self.child.append(p_child)

        p_child.nvisit += 1
        p_child.move = move
        p_child.parent = self
        if self.turn ==1:
            next_turn =0
        else:
            next_turn =1
        np_move = np.array(move)
        copy_of_board = np.copy(self.board)
        p_child.board = mysgf.move(copy_of_board,np_move,next_turn,check_flag=False)
        prob, child_winrate = ego_predict(model, p_child.board, next_turn, color_reverse=False)
        p_child.winrate = child_winrate
        p_child.child_move = prob

    def backup(self):
        pp = self.get_parent()
        if self.turn==0 and self.winrate>pp.winrate:
            pp.winrate = self.winrate
        elif self.turn==1 and self.winrate<pp.winrate:
            pp.winrate = self.winrate
        return pp

def get_next_search(p_search, final_decision = False):
    dict = p_search.child_move
    max = 0
    max_key = 0

    if not final_decision:
        for item in dict:
            temp = dict[item]+ 0.2*random.random()
            if temp > max:
                max = temp
                max_key = item

    else:
        for item in dict:
            temp = dict[item]
            if temp > max:
                max = temp
                max_key = item
    return max_key


def mcts_predict(p_start,model):
    search_stack = []
    p_search = p_start
    for i in range(128):
        move_tuple = get_next_search(p_search)
        depth = 0
        extend_flag = False
        while((not extend_flag) and depth<32):
            if p_search.move:
                print(p_search.move)
            depth +=1
            if not p_search.child:
                p_search = p_search.extend(move_tuple, model)
                extend_flag = True
            else:
                find_flag = False
                for p in p_search.child:
                    if move_tuple == p.move:
                        p_search = p.move
                        find_flag = True

                if find_flag == True:
                    p_search=p
                else:
                    p_search = p_search.extend(move_tuple, model)
                    extend_flag = True
            search_stack.append(p_search)
        while(search_stack):
            p_backup = search_stack[-1]
            del search_stack[-1]
            p_backup.backup()

    if not p_search.child:
        return (19,0)
    else:
        dict = p_start.child_move
        max = 0
        max_key = 0
        for pointer in p_search.child:
            if p_start.turn ==0:
                temp = dict[pointer.move]*(1.0-pointer.winrate)
                if temp >max:
                    max =temp
                    max_key = pointer.move
            else:
                temp = dict[pointer.move] * pointer.winrate
                if temp > max:
                    max = temp
                    max_key = pointer.move
        return max_key

def actual_move(p_head,move,model):
    for m in p_head.child_move:
        if move == m:
            for item in p_head.child:
                if item.move ==move:
                    return item
            p = p_head.extend(move,model)
            return p
    p = p_head.extend(move,model)
    return p


def mcts_init(model,ha=False):
    p_root = Pymcts(None)
    if ha:
        root_turn = 1
    else:
        root_turn = 0

    p_root.board = np.zeros((19,19),dtype=np.int64)
    prob, child_winrate = ego_predict(model, p_root.board, root_turn, color_reverse=False)
    p_root.winrate = child_winrate
    p_root.child_move = prob
    p_root.nvisit = 1
    p_root.turn = root_turn

    return p_root



