import ego_resnet as enn
import ego_io as eio
import my_sgf as mysgf
import os
import numpy as np
import shutil
import time

def get_trainset_list():
    for path, dirs, files in os.walk('./sgf_repo/human_dataset'):
        if path == './sgf_repo/human_dataset':
            return files
    return 0


if __name__=="__main__":
    model = None
    empty_flag = False
    while(True):
        print("Init...")
        eio.check_folder()
        mysgf.check_folder()
        filelist = get_trainset_list()
        for files in filelist:
            model =None
            if files == '.DS_Store':
                continue
            dataset_path = './sgf_repo/human_dataset/%s' % files
            x0, x1, y0, y1 = eio.read_dataset(dataset_path)
            data_size = len(x0)
            print("Data size:")
            print(data_size)

            test_idx = int(0.8 * data_size)

            test_x0 = np.copy(x0[test_idx:])
            test_x1 = np.copy(x1[test_idx:])
            test_y0 = np.copy(y0[test_idx:])
            test_y1 = np.copy(y1[test_idx:])
            x0 = np.copy(x0[0:test_idx])
            x1 = np.copy(x1[0:test_idx])
            y0 = np.copy(y0[0:test_idx])
            y1 = np.copy(y1[0:test_idx])
            checkpointname ="./checkpoint_repo/ego_checkpoint0.ckpt"
            print("Data_loaded...")

            try:
                model = enn.load_model(checkpointname)
                print("Try: checkpoint loaded\n Successsful")
            except:
                model = enn.train_init()
                print("Except: checkpoint load_fail!")
            print("Model init...")
            try:
                enn.train_model(model, x0, x1, y0, y1, checkpointname, test_x0, test_x1, test_y0, test_y1)
            except:
                pass

            src_dir = './sgf_repo/human_dataset/' + files
            dst_dir = './sgf_repo/recycle2/' + files

            shutil.move(src_dir, dst_dir)
            del model

        for path, dirs, files in os.walk('./sgf_repo/human_dataset'):
            if path == './sgf_repo/human_dataset':
                for fn in files:
                    if fn != '.DS_Store':
                        empty_flag = False

        if empty_flag:
            time.sleep(300)
