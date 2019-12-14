import tensorflow as tf
import resnet
import matplotlib.pyplot as plt
import numpy as np
(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()
print(train_images)
print(train_labels.dtype)
train_images, test_images = train_images / 255.0, test_images / 255.0
print(test_images.dtype)
print(train_images.shape)
print(train_labels[0])
image_input = tf.keras.Input(shape=(32,32,3),name = 'image_input')
x = resnet.conv_block(image_input, 32, '1')
x = tf.keras.layers.MaxPool2D((3,3),strides=(2,2))(x)
x = resnet.residual_block2(x, [32, 32], 4, '2')
x = tf.keras.layers.MaxPool2D((2,2))(x)
x = resnet.residual_block2(x, [64, 64], 3, '3')

"""x = tf.keras.layers.MaxPool2D((2,2))(x)
x = resnet.residual_block2(x, [128, 128], 3, '4')"""
x = tf.keras.layers.AveragePooling2D((2,2))(x)
x = resnet.output_block(x)
x = tf.keras.layers.Dense(64,activation = 'relu')(x)

label_output = tf.keras.layers.Dense(10,activation = 'softmax', name ='label_output')(x)
model = tf.keras.Model(inputs=[image_input],outputs=[label_output])
#model.summary()

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

p=model.predict(np.array([test_images[0]]))
print(p.shape)

#history = model.fit(train_images, train_labels, epochs=10,
#                    validation_data=(test_images, test_labels))

print(history)
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0.5, 1])
plt.legend(loc='lower right')
plt.show()

test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)

print(test_acc)