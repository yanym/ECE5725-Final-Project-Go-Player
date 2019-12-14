import os
import numpy as np

def check_folder():
    """
    Initialize the folder for the purpose of storing the checkpoints.(saved model weights)
    """
    if os.path.isdir('./checkpoint_repo')==False:
        print("** Initializing the checkpoint repo.")
        os.mkdir('checkpoint_repo')

    if os.path.isdir('./model_info')==False:
        print("** Initializing the model information.")
        os.mkdir('model_info')

    if os.path.isdir('./dataset_repo')==False:
        print("** Initializing the dataset repo.")
        os.mkdir('dataset_repo')

    if os.path.isdir('./data_info')==False:
        print("** Initializing the dataset information.")
        os.mkdir('data_info')

    if os.path.isdir('./sgf_repo/recycle2') == False:
        print("** Initializing the recycle bin.")
        os.mkdir('./sgf_repo/recycle2')
def latest_model():
    """

    :return: latest_model_name , next_model_name
    """
    for path, dirs, files in os.walk('./checkpoint_repo'):
        if path == './checkpoint_repo':
            latest_num = len(files) - 1
            if '.DS_Store' in files:
                latest_num -= 1
            if latest_num == -1:
                print('** Ego Warning: No checkpoints are currently stored in the repo.')
                return "", "./checkpoint_repo/ego_checkpoint0.ckpt"

            else:
                target_name = "ego_checkpoint_%d.ckpt" % latest_num
                next_name = "./checkpoint_repo/ego_checkpoint_%d.ckpt" % (latest_num+1)
                if target_name in files:
                    target_name ="./checkpoint_repo/ego_checkpoint_%d.ckpt"% latest_num
                    return target_name,next_name
                else:
                    i = latest_num
                    while(i>=0):
                        if "ego_checkpoint_%d.ckpt" % i in files:
                            target_name = "./checkpoint_repo/ego_checkpoint_%d.ckpt" % i
                            next_name = "./checkpoint_repo/ego_checkpoint_%d.ckpt" % (i + 1)
                            return target_name, next_name
    return 0

def best_model():
    """
    :return: a filename for the best model in this phase.
    """
    if os.path.exists('./model_info/ego_logs.txt'):
        with open('./model_info/ego_logs.txt','r') as f:
            log = f.read()
            # TODO: get info for best model
            #....
            #return filename
    else:
        print("Ego Error: No log for the *best model* is found.")
    return 0

def untrained_dataset():
    if os.path.exists('./model_info/ego_logs.txt'):
        with open('./model_info/ego_logs.txt','r') as f:
            log = f.read()
            # TODO: get info for best model
            #....
            #return filename
    else:
        print("Ego Error: No log for the *dataset* is found.")
    return 0

def ds_reinforce(board):
    rein_set =[]
    rein_set.append(board)

    b1=np.copy(board)
    b1 = np.rot90(b1,1)
    rein_set.append(b1)

    b2 = np.copy(b1)
    b2 = np.rot90(b2, 1)
    rein_set.append(b2)

    b3=np.copy(b2)
    b3 = np.rot90(b3,1)
    rein_set.append(b3)

    b4 = np.copy(b3)
    b4 = np.fliplr(b4)
    rein_set.append(b4)

    b5 = np.copy(b4)
    b5 = np.rot90(b5, 1)
    rein_set.append(b5)

    b6 = np.copy(b5)
    b6 = np.rot90(b6, 1)
    rein_set.append(b6)

    b7 = np.copy(b5)
    b7 = np.rot90(b7, 1)
    rein_set.append(b7)
    return rein_set


def read_dataset(filepath):
    """
    input: black 0, none 1, white 2, next_move 3
    output: black -1, none 0, white 1
    :param filepath: string with extensions if there are
    :return:
    """
    str = ""

    #FIXME: PATH + FILENAME
    with open(filepath, 'rb') as f:
        content = f.read()
        str = content.decode(encoding="ASCII")
    dataset = str.split("\n")
    length = len(dataset) -1
    input0 = []
    input1 = []
    output0 = []
    output1 =[]

    del dataset[length]
    for data in dataset:
        try:
            temp = data.split(";")
            temp_input0 = temp[0]
            temp_input0 = temp_input0.split(",")
            temp_input0 = list(map(int, temp_input0))
            temp_input0 = np.array(temp_input0)
            temp_input0 = temp_input0.reshape((19, 19))

            input1_arr = np.array([int(temp[1])])
            output1_arr = np.array([int(temp[2])])
            rein_set = ds_reinforce(temp_input0)
            if (len(rein_set) != 8):
                print("** Reinforced set size is not 8!")
            for i in range(8):
                rein_input0 = np.copy(rein_set[i])
                idx = np.argwhere(rein_input0 == 3)

                if len(idx) != 0:

                    output0.append(np.array([idx[0, 0] * 19 + idx[0, 1]]))
                    rein_input0[idx[0, 0], idx[0, 1]] = 1
                else:
                    output0.append(np.array([361]))

                rein_input0 -= 1
                rein_input0 = rein_input0.reshape([19, 19, 1])
                input0.append(rein_input0)

                input1.append(np.copy(input1_arr))
                output1.append(np.copy(output1_arr))
        except:
            print("Exception...")
            continue

    input0 = np.array(input0,dtype = np.float32)
    input1 = np.array(input1, dtype = np.float32)
    output0 = np.array(output0,dtype = np.int64)
    output1 = np.array(output1, dtype=np.int64)

    return input0,input1,output0,output1


