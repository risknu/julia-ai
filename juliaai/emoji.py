from __future__ import annotations

import numpy as np
import tensorflow as tf

import json
from typing import Any

from juliaai.utility import AbstractUtilityClass
from juliaai.misc import MetaSettings
meta_settings: MetaSettings = MetaSettings

from tensorflow import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Bidirectional, Dropout


class BidirectionalLSTM_EmojiClassifier(AbstractUtilityClass):
    def __init__(self, data_set: list[dict] = None) -> None:
        super().__init__()
        self.setup_new(data_set)

    def setup_new(self, data_set: list[dict] = None) -> None:
        with open('emojis.json', 'r') as fileIOemojisR:
            emoji_data_file: list[dict] = json.load(fileIOemojisR)
        self.data: list = emoji_data_file if not data_set else data_set

        self.texts: list = [item["text"] for item in self.data]
        self.labels: list = [item["emoji"] for item in self.data]
        
    def tokenizer_method(self) -> None:
        self.tokenizer: Tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(self.texts)
        self.sequences: Any = self.tokenizer.texts_to_sequences(self.texts)
        self.padded_sequences: Any = pad_sequences(self.sequences, 
                                                   maxlen=10, 
                                                   padding='post', 
                                                   truncating='post')

    def model_build(self) -> None:
        self.model = Sequential()
        self.model.add(Embedding(input_dim=len(self.tokenizer.word_index) + 1, 
                                 output_dim=int(meta_settings.output_dim), 
                                 input_length=int(meta_settings.input_length)))
        self.model.add(Bidirectional(LSTM(int(meta_settings.units))))
        self.model.add(Dense(int(meta_settings.units), activation='relu'))
        self.model.add(Dropout(float(meta_settings.rate)))
        self.model.add(Dense(1, activation='sigmoid'))

        self.model.compile(optimizer=meta_settings.optimizer, 
                           loss=meta_settings.loss, 
                           metrics=['accuracy'])
        
    def get_response(self, input_values: list[str] = None) -> list[bool]:
        if not input_values:
            return False
        tokenizer: Tokenizer = Tokenizer()
        new_sequences = tokenizer.texts_to_sequences(input_values)
        new_padded_sequences = pad_sequences(new_sequences, 
                                             maxlen=10, 
                                             padding='post', 
                                             truncating='post')
        loaded_model = tf.keras.models.load_model('model/BidirectionalLSTM_EmojiClassifier.keras')
        predictions = loaded_model.predict(new_padded_sequences)
        list_of_output: list[bool] = []
        for text, pred in zip(input_values, predictions):
            emoji: bool = True if pred > 0.45 else False
            list_of_output.append(emoji)
            print(f"[OUTPUT_TEST]\tCreated new response\tText: {text}, Pred: {pred}, Emoji: {emoji}")
        return list_of_output

    def build_examlpe(self) -> None:
        self.tokenizer_method()
        self.model_build()

        self.labels_np = np.array(self.labels)

        self.model.fit(self.padded_sequences, self.labels_np, 
                       epochs=int(meta_settings.epochs), 
                       batch_size=int(meta_settings.batch_size))
        self.model.save("model/BidirectionalLSTM_EmojiClassifier.keras")
