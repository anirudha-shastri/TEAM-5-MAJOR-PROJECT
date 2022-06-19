import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image as im
import cv2
from dat.models import Img_Auto_Ann
from dat import db
from dat.hourglass104 import StackedHourglassNetwork
from flask_login import current_user

model = StackedHourglassNetwork(
        input_shape=(256, 256, 3), num_stack=2, num_residual=1,
        num_heatmap=19)
model.load_weights('dat/models/automatic_bone_age/model-v0.0.1-epoch-4158-loss-0.8258.h5')

plt.rcParams["figure.figsize"] = (10,10)

def find_max_coordinates(heatmaps):
        flatten_heatmaps = tf.reshape(heatmaps, (4096, 19))
        indices = tf.math.argmax(flatten_heatmaps, axis=0)
        # after flatten, each 64 values represent one row in original heatmap
        y = tf.cast(indices / 64, dtype=tf.int64)
        x = indices - 64 * y
        return tf.stack([x, y], axis=1).numpy()

def extract_keypoints_from_heatmap(heatmaps):
        max_keypoints = find_max_coordinates(heatmaps)
        # pad the heatmap so that we don't need to deal with borders
        padded_heatmap = np.pad(heatmaps, [[1,1],[1,1],[0,0]])
        adjusted_keypoints = []
        for i, keypoint in enumerate(max_keypoints):
            # since we've padded the heatmap, the max keypoint should increment by 1
            max_y = keypoint[1]+1
            max_x = keypoint[0]+1
            # the patch is the 3x3 grid around the max keypoint location
            patch = padded_heatmap[max_y-1:max_y+2, max_x-1:max_x+2, i]
            # assign 0 to max location
            patch[1][1] = 0
            # and the next largest value is the largest neigbour we are looking for
            index = np.argmax(patch)
            # find out the location of it relative to center
            next_y = index // 3
            next_x = index - next_y * 3
            delta_y = (next_y - 1) / 4
            delta_x = (next_x - 1) / 4
            # we can then add original max keypoint location with this offset
            adjusted_keypoint_x = keypoint[0] + delta_x
            adjusted_keypoint_y = keypoint[1] + delta_y
            adjusted_keypoints.append((adjusted_keypoint_x, adjusted_keypoint_y))
        # we do need to clip the value to make sure there's no keypoint out of border, just in case.
        adjusted_keypoints = np.clip(adjusted_keypoints, 0, 64)
        # normalize the points so that we can scale back easily
        normalized_keypoints = adjusted_keypoints / 64
        return normalized_keypoints

def draw_keypoints_on_image(image, keypoints,filename, index=None):
        fig,ax = plt.subplots(1)
        ax.imshow(image)
        joints = []
        for i, joint in enumerate(keypoints):
            joint_x = joint[0] * image.shape[1]
            joint_y = joint[1] * image.shape[0]
            if index is not None and index != i:
                continue
            plt.scatter(joint_x, joint_y, s=10, c='blue', marker='o')
        # plt.show()
        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)
        imgf = im.open(buf)
        imgf.show()
        img_arr = np.array(imgf)
        converted_img = cv2.imencode('.jpg',img_arr)[1].tostring()
        img_name = filename.replace('.jpg','')+"_auto_annotated.jpg"
        user_id = current_user.id
        img_auto = Img_Auto_Ann(user_id = user_id, img = converted_img,name=img_name)
        db.session.add(img_auto)
        db.session.commit()
        buf.close()

def predict(img):
        # encoded = tf.io.read_file(image_path)
        image = tf.io.decode_jpeg(img)
        inputs = tf.image.resize(image, (256, 256))
        inputs = tf.cast(inputs, tf.float32) / 127.5 - 1
        inputs = tf.expand_dims(inputs, 0)
        outputs = model(inputs, training=False)
        heatmap = tf.squeeze(outputs[-1], axis=0).numpy()
        kp = extract_keypoints_from_heatmap(heatmap)
        return image, kp