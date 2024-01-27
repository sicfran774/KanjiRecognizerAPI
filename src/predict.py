# Model and code taken from DaKanji-Single-Kanji-Recognition by CaptainDario
# https://github.com/CaptainDario/DaKanji-Single-Kanji-Recognition

import ast

import numpy as np
import urllib.request
import tensorflow as tf
import cv2

class Predictor():
    """ Can predict hand drawn Kanji characters from images using tf_lite.

    Attributes:
        kanji_interpreter  (Interpreter) : The tf_lite interpreter which is used to predict characters
        input_details             (dict) : The input details of 'kanji_interpreter'.
        output_details            (dict) : The output details of 'kanji_interpreter'.
        labels          (LabelBinarizer) : A list of all labels the CNN can recognize (ordered).
    """

    def __init__(self, dataURI) -> None:
        self.kanji_interpreter = None
        self.input_details     = None
        self.output_details    = None
        self.labels   = None
        self.uri      = dataURI
        self.image    = None

        self.init_labels()
        self.init_tf_lite_model()
        self.preprocess_image()
    
    def init_labels(self):
        """ Load the list of labels which the CNN can recognize
        """

        with open("../labels.txt", "r", encoding="utf8") as f:
            self.labels = ast.literal_eval(f.read())

    def init_tf_lite_model(self):
        """ Load the tf_lite model from the 'data'-folder.
        """

        # load model
        path_to_model = "../../model/tflite/model.tflite"
        self.kanji_interpreter = tf.lite.Interpreter(model_path=path_to_model)
        self.kanji_interpreter.allocate_tensors()

        # get in-/output details
        self.input_details = self.kanji_interpreter.get_input_details()
        self.output_details = self.kanji_interpreter.get_output_details()

    def preprocess_image(self):
        response = urllib.request.urlopen(self.uri)
        with open('image.png', 'wb') as f:
            f.write(response.file.read())
        img = cv2.imread('image.png')
        resized = cv2.resize(img, dsize=(64, 64))

        # Convert to grayscale
        img_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Convert to float32
        float32_img = img_gray.astype(np.float32)

        # Add batch and channel dimensions (1 image, image x, image y, 1 channel [grayscale])
        input_tensor = np.expand_dims(float32_img, axis=0)
        input_tensor = np.expand_dims(input_tensor, axis=-1)

        self.image = input_tensor


    def predict(self, cnt_predictions : int) -> [str]:
        """ Predict a character from an input image.

        Args:
            image      (np.array) : A numpy array with shape (1, 64, 64, 1) and dtype 'float32' 
            cnt_predictions (int) : How many predictions should be returned ('cnt_predictions' most likely ones)

        Returns:
            A list with the 'cnt_predictions' most confident predictions.
        """

        # make prediction
        print("Input Tensor Details:", self.input_details) 
        self.kanji_interpreter.set_tensor(self.input_details[0]["index"], self.image)
        self.kanji_interpreter.invoke()
        output_data = self.kanji_interpreter.get_tensor(self.output_details[0]["index"])
        out_np = np.array(output_data)

        # get the 'cnt_predictions' most confident predictions
        preds = []
        for i in range(cnt_predictions):
            pred = self.labels[out_np.argmax()]
            preds.append(pred[0])

            # 'remove' this prediction from all
            out_np[out_np.max() == out_np] = 0.0

        return preds