import tensorflow as tf
import numpy as np



def residual_unit(inputs, depth, block_num, unit_num,l2_value = 0.00001):
    f1, f2, f3 = depth
    main_path = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-%s-1' % (block_num, unit_num))(inputs)
    main_path = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-%s-1' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Conv2D(filters=f1, kernel_size=(1, 1), kernel_initializer='he_uniform',
                                       name='Conv2D_Unit_%s-%s-1' % (block_num, unit_num),kernel_regularizer =
                                       tf.keras.regularizers.l2(l=l2_value))(main_path)

    main_path = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-%s-2' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-%s-2' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Conv2D(filters=f2, kernel_size=(3, 3), kernel_initializer='he_uniform',
                                       padding='same', name='Conv2D_Unit_%s-%s-2' % (block_num, unit_num),
                                       kernel_regularizer = tf.keras.regularizers.l2(l=l2_value))(main_path)

    main_path = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-%s-3' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-%s-3' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Conv2D(filters=f3, kernel_size=(1, 1), kernel_initializer='he_uniform',
                                       name='Conv2D_Unit_%s-%s-3' % (block_num, unit_num),kernel_regularizer
                                       =tf.keras.regularizers.l2(l=l2_value))(main_path)

    block_output = tf.keras.layers.Add()([inputs, main_path])

    return block_output

def residual_unit2(inputs, depth, block_num, unit_num,l2_value=0.00001):
    f1, f2 = depth
    main_path = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-%s-1' % (block_num, unit_num))(inputs)
    main_path = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-%s-1' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Conv2D(filters=f1, kernel_size=(3, 3), kernel_initializer='he_uniform',
                                       padding = 'same', name='Conv2D_Unit_%s-%s-1' % (block_num, unit_num),kernel_regularizer
                                       =tf.keras.regularizers.l2(l=l2_value)
                                      )(main_path)

    main_path = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-%s-2' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-%s-2' % (block_num, unit_num))(main_path)
    main_path = tf.keras.layers.Conv2D(filters=f2, kernel_size=(3, 3), kernel_initializer='he_uniform',
                                       padding='same', name='Conv2D_Unit_%s-%s-2' % (block_num, unit_num),kernel_regularizer
                                       =tf.keras.regularizers.l2(l=l2_value)
                                       )(main_path)


    block_output = tf.keras.layers.Add()([inputs, main_path])

    return block_output

def conv_block(inputs, depth, block_num, l2_v = 0.00001):

    inputs = tf.keras.layers.Conv2D(filters=depth, kernel_size=(3, 3), kernel_initializer='he_uniform',
                                    padding='same', name='Conv2D_Unit_%s' % block_num,
                                    kernel_regularizer = tf.keras.regularizers.l2(l=l2_v))(inputs)
    inputs = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s' % block_num)(inputs)
    inputs = tf.keras.layers.Activation('relu', name='Activation_Unit_%s' % block_num)(inputs)
    return inputs


def connection_block(inputs, depth_out, block_num):

    inputs = tf.keras.layers.Conv2D(filters=depth_out, kernel_size=(1, 1), kernel_initializer='he_uniform',
                                    name='Conv2D_Unit_%s-0' % block_num,kernel_regularizer
                                    = tf.keras.regularizers.l2(l=0.00003))(inputs)
    inputs = tf.keras.layers.BatchNormalization(axis=-1, name='BN_Unit_%s-0' % block_num)(inputs)
    inputs = tf.keras.layers.Activation('relu', name='Activation_Unit_%s-0' % block_num)(inputs)
    return inputs


def residual_block(inputs, depth, int_unit_num, block_num,l2_v=0.00001):

    inputs = connection_block(inputs, depth[2], block_num)
    for i in range(int_unit_num):
        inputs = residual_unit(inputs, depth, block_num, str(i+1),l2_value=l2_v)
    return inputs

def residual_block2(inputs, depth, int_unit_num, block_num,l2_v=0.00001):

    inputs = connection_block(inputs, depth[1], block_num,)
    for i in range(int_unit_num):
        inputs = residual_unit2(inputs, depth, block_num, str(i+1),l2_value=l2_v)
    return inputs


def output_block(inputs):
    inputs = tf.keras.layers.Flatten()(inputs)
    return inputs

def create_model():
    ego_input0 = tf.keras.Input(shape=(19, 19,1), name='ego_input0')
    ego_input1 = tf.keras.Input(shape=(1,), name="ego_input1")   # Who's turn to move

    x = conv_block(ego_input0, 16, '1')
    x = tf.keras.layers.MaxPool2D((3, 3),strides=(1,1))(x)
    x = residual_block(x, [8,8,32 ], 2, '2')

    # winrate branch:
    y = tf.keras.layers.MaxPool2D((5, 5), strides=(2, 2))(x)
    y = residual_block(y, [16, 16,32], 2, 'A3',l2_v=0.001)
    y = tf.keras.layers.MaxPool2D((3, 3), strides=(2, 2))(y)
    y = residual_block(y, [32, 32,64], 1, 'A4',l2_v=0.001)
    y = tf.keras.layers.AveragePooling2D((3, 3))(y)
    y = output_block(y)
    y2 = tf.keras.layers.concatenate([y, ego_input1])
    y2 = tf.keras.layers.Dense(32, activation='relu',kernel_regularizer = tf.keras.regularizers.l2(l=0.003))(y2)
    ego_output1 = tf.keras.layers.Dense(2, activation='softmax', name='ego_output1')(y2)

    # next move branche:
    z = tf.keras.layers.MaxPool2D((3, 3), strides=(1, 1))(x)
    z = residual_block(z, [16, 16,64], 2, 'B3')
    z = tf.keras.layers.MaxPool2D((4, 4),strides=(2 , 2))(z)
    z = residual_block(z, [32, 32,64], 3, 'B4')
    z = tf.keras.layers.MaxPool2D((2, 2),strides=(2,2))(z)
    z = residual_block(z, [64, 64,256], 1, 'B5')
    z = tf.keras.layers.AveragePooling2D((2, 2))(z)
    z = output_block(z)
    z2 = tf.keras.layers.concatenate([z, ego_input1])
    z2 = tf.keras.layers.Dense(512, activation='relu',kernel_regularizer = tf.keras.regularizers.l2(l=0.003))(z2)
    ego_output0 = tf.keras.layers.Dense(362, activation='softmax', name='ego_output0')(z2)
    model = tf.keras.Model(inputs=[ego_input0,ego_input1], outputs=[ego_output0,ego_output1])
    model.summary()

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train_model(model,input0,input1,output0,output1,checkpoint_name,testx0,testx1,testy0,testy1):

    check_path = checkpoint_name
    cb_end = tf.keras.callbacks.EarlyStopping(monitor = 'val_loss',patience=3)
    cb_save = tf.keras.callbacks.ModelCheckpoint(check_path, save_weights_only = True, monitor ='val_loss',
                                                 save_best_only =True,mode = 'auto',verbose = 1,save_freq= 'epoch')
    history = model.fit({'ego_input0': input0, 'ego_input1': input1}, {'ego_output0': output0, 'ego_output1': output1},
                        epochs=10, callbacks= [cb_end, cb_save], batch_size=128,
                        validation_data = ({'ego_input0': testx0, 'ego_input1': testx1}, {'ego_output0': testy0, 'ego_output1': testy1}))

    """
    print(history)
    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0, 1])
    plt.legend(loc='lower right')
    plt.show()
    """

def load_model(checkpoint_name):
    """
    Input the number of checkpoint
    Return the loaded model.
    """
    check_path = checkpoint_name
    model = create_model()
    model.load_weights(check_path)
    return model


def train_init():
    model = create_model()
    return model

def ego_predict(model,checkpoint_path,input0,input1):
    model.load_weights(checkpoint_path)
    p = model.predict({'ego_input0': input0, 'ego_input1': input1})
    move_arr = p


def train_resume():
    pass
