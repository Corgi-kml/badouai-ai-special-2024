from __future__ import print_function
from __future__ import absolute_import

import warnings
import numpy as np

from keras.models import Model
from keras import layers
from keras.layers import Activation, Dense, Input, BatchNormalization, Conv2D, MaxPooling2D, AveragePooling2D
from keras.layers import GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.engine.topology import get_source_inputs
from keras.utils.layer_utils import convert_all_kernels_in_model
from keras.utils.data_utils import get_file
from keras import backend as K
from keras.applications.imagenet_utils import decode_predictions
from keras.preprocessing import image


def conv2d_bn(x,
              filters,
              kernel_size,
              strides=(1, 1),
              padding='same',
              name=None):
    if name is not None:
        bn_name = name + '_bn'
        conv_name = name + '_conv'
    else:
        bn_name = None
        conv_name = None
    x = Conv2D(filters, kernel_size, strides=strides, padding=padding, use_bias=False, name=conv_name)(x)
    x = BatchNormalization(scale=False, name=bn_name)(x)
    x = Activation('relu', name=name)(x)
    return x


def inception_v3_base(input_shape=(299, 299, 3), class_num=1000):
    img_input = Input(shape=input_shape)
    x = conv2d_bn(img_input, 32, (3, 3), strides=(2, 2), padding='valid')
    x = conv2d_bn(x, 32, (3, 3), padding='valid')
    x = conv2d_bn(x, 64, (3, 3))
    x = MaxPooling2D((3, 3), strides=(2, 2))(x)

    branch1x1 = conv2d_bn(x, 96, (1, 1))
    branch5x5 = conv2d_bn(x, 48, (1, 1))
    branch5x5 = conv2d_bn(branch5x5, 64, (5, 5))
    branch3x3dbl = conv2d_bn(x, 64, (1, 1))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 32, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=3,
        name='mixed0')

    branch1x1 = conv2d_bn(x, 96, (1, 1))
    branch5x5 = conv2d_bn(x, 48, (1, 1))
    branch5x5 = conv2d_bn(branch5x5, 64, (5, 5))
    branch3x3dbl = conv2d_bn(x, 64, (1, 1))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 32, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=3,
        name='mixed1')

    branch1x1 = conv2d_bn(x, 96, (1, 1))
    branch5x5 = conv2d_bn(x, 48, (1, 1))
    branch5x5 = conv2d_bn(branch5x5, 64, (5, 5))
    branch3x3dbl = conv2d_bn(x, 64, (1, 1))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 32, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch5x5, branch3x3dbl, branch_pool],
        axis=3,
        name='mixed2')
    branch3x3 = conv2d_bn(x, 384, (3, 3), strides=(2, 2), padding='valid')
    branch3x3dbl = conv2d_bn(x, 64, (1, 1))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3))
    branch3x3dbl = conv2d_bn(branch3x3dbl, 96, (3, 3), strides=(2, 2), padding='valid')
    branch_pool = MaxPooling2D((3, 3), strides=(2, 2))(x)
    x = layers.concatenate([branch3x3, branch3x3dbl, branch_pool], axis=3, name='mixed3')

    branch1x1 = conv2d_bn(x, 192, (1, 1))
    branch7x7 = conv2d_bn(x, 128, (1, 1))
    branch7x7 = conv2d_bn(branch7x7, 128, (1, 7))
    branch7x7 = conv2d_bn(branch7x7, 192, (7, 1))
    branch7x7dbl = conv2d_bn(x, 128, (1, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, (1, 7))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 128, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (1, 7))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch7x7, branch7x7dbl, branch_pool],
        axis=3,
        name='mixed4')

    branch1x1 = conv2d_bn(x, 192, (1, 1))
    branch7x7 = conv2d_bn(x, 160, (1, 1))
    branch7x7 = conv2d_bn(branch7x7, 160, (1, 7))
    branch7x7 = conv2d_bn(branch7x7, 192, (7, 1))
    branch7x7dbl = conv2d_bn(x, 160, (1, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (1, 7))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (1, 7))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch7x7, branch7x7dbl, branch_pool],
        axis=3,
        name='mixed5')

    branch1x1 = conv2d_bn(x, 192, (1, 1))
    branch7x7 = conv2d_bn(x, 160, (1, 1))
    branch7x7 = conv2d_bn(branch7x7, 160, (1, 7))
    branch7x7 = conv2d_bn(branch7x7, 192, (7, 1))
    branch7x7dbl = conv2d_bn(x, 160, (1, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (1, 7))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 160, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (1, 7))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch7x7, branch7x7dbl, branch_pool],
        axis=3,
        name='mixed6')

    branch1x1 = conv2d_bn(x, 192, (1, 1))
    branch7x7 = conv2d_bn(x, 192, (1, 1))
    branch7x7 = conv2d_bn(branch7x7, 192, (1, 7))
    branch7x7 = conv2d_bn(branch7x7, 192, (7, 1))
    branch7x7dbl = conv2d_bn(x, 192, (1, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (1, 7))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (7, 1))
    branch7x7dbl = conv2d_bn(branch7x7dbl, 192, (1, 7))
    branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
    branch_pool = conv2d_bn(branch_pool, 192, (1, 1))
    x = layers.concatenate(
        [branch1x1, branch7x7, branch7x7dbl, branch_pool],
        axis=3,
        name='mixed7')

    branch3x3 = conv2d_bn(x, 192, (1, 1))
    branch3x3 = conv2d_bn(branch3x3, 320, (3, 3), strides=(2, 2), padding='valid')
    branch7x7x3 = conv2d_bn(x, 192, (1, 1))
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, (1, 7))
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, (7, 1))
    branch7x7x3 = conv2d_bn(branch7x7x3, 192, (3, 3), strides=(2, 2), padding='valid')
    branch_pool = MaxPooling2D((3, 3), strides=(2, 2))(x)
    x = layers.concatenate([branch3x3, branch7x7x3, branch_pool], axis=3, name='mixed8')

    for i in range(2):
        branch1x1 = conv2d_bn(x, 320, (1, 1))
        branch3x3 = conv2d_bn(x, 384, (1, 1))
        branch3x3_1 = conv2d_bn(branch3x3, 384, (1, 3))
        branch3x3_2 = conv2d_bn(branch3x3, 384, (3, 1))
        branch3x3 = layers.concatenate([branch3x3_1, branch3x3_2], axis=3)
        branch3x3dbl = conv2d_bn(x, 448, (1, 1))
        branch3x3dbl = conv2d_bn(branch3x3dbl, 384, (3, 3))
        branch3x3dbl_1 = conv2d_bn(branch3x3dbl, 384, (1, 3))
        branch3x3dbl_2 = conv2d_bn(branch3x3dbl, 384, (3, 1))
        branch3x3dbl = layers.concatenate([branch3x3dbl_1, branch3x3dbl_2], axis=3)
        branch_pool = AveragePooling2D((3, 3), strides=(1, 1), padding='same')(x)
        branch_pool = conv2d_bn(branch_pool, 192, (1, 1))
        x = layers.concatenate(
            [branch1x1, branch3x3, branch3x3dbl, branch_pool],
            axis=3,
            name='mixed' + str(9 + i))

    # Classification block
    x = GlobalAveragePooling2D(name='avg_pool')(x)
    x = Dense(class_num, activation='softmax', name='predictions')(x)

    # Create model
    model = Model(img_input, x, name='inception_v3')

    return model

def preprocess_input(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x

if __name__ == '__main__':
    model = inception_v3_base(input_shape=(299, 299, 3), class_num=1000)
    model.load_weights('inception_v3_weights_tf_dim_ordering_tf_kernels.h5')
    image_path = 'elephant.jpg'
    img = image.load_img(image_path, target_size=(299, 299))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    print('Predicted:', decode_predictions(preds))