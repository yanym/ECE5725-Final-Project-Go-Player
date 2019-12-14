import numpy as np
import ego_resnet as enn
import os

model = ''

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

def ego_predict(x0, x1, color_reverse=False):
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
    input1 = np.array([[x1]],dtype=np.float32)
    if color_reverse:
        input0 *= -1
        input1 *= -1
    p = model.predict({'ego_input0': input0, 'ego_input1': input1})
    prob_arr = p[0][0]
    winrate = p[1][0][0]
    move_sort = np.copy(prob_arr)
    move_sort *= -1.0
    idx = np.argsort(move_sort)
    x_arr = np.copy(idx)
    y_arr = np.copy(idx)
    y_arr %= 19
    x_arr /= 19
    x_arr=x_arr.astype(np.int64)

    dict={}
    for i in range(9):
        dict[(x_arr[i],y_arr[i])] =prob_arr[i]
    return dict, winrate


if __name__ == "__main__":

    board0 = np.zeros((19,19),int)
    a = 1
    board1= np.copy(board0)
    board1[3,3] =-1
    b = -1

    # Here are 2 examples
    model = predict_init()

    res0 = ego_predict(model,board0,a)
    res1 = ego_predict(model,board1,b,color_reverse = False)
    print(res0)
    print(res1)