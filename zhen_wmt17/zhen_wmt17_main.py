# coding=utf-8
""" Problem definition for translation from Chinese to English."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import numpy as np
import tensorflow as tf
import struct


from tensor2tensor.data_generators.translate import TranslateProblem
from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.utils import registry
from tensor2tensor.models import transformer

from sklearn import decomposition
from sklearn import datasets
from sklearn.preprocessing import StandardScaler

# Chinese to English translation datasets.
LOCATION_OF_DATA = '/experiments/jive/multi30k/'

_ZHEN_TRAIN_DATASETS = [
    LOCATION_OF_DATA+'train.en',
    LOCATION_OF_DATA+'train.fr',
    LOCATION_OF_DATA+'train.fr',
    LOCATION_OF_DATA+'train.npy'
]

_ZHEN_DEV_DATASETS = [
    LOCATION_OF_DATA+'val.en',
    LOCATION_OF_DATA+'val.fr',
    LOCATION_OF_DATA+'val.fr',
    LOCATION_OF_DATA+'val.npy'
]


_ZHEN_STRAIN_DATASETS = [
]

_ZHEN_VOCAB_FILES = [
    LOCATION_OF_DATA+'train_en.dict',
    LOCATION_OF_DATA+'train_fr.dict'
]


def bi_vocabs_token2id_generator(source_path, target_path, source_token_vocab, target_token_vocab, eos=None):
    """Generator for sequence-to-sequence tasks that uses tokens.

    This generator assumes the files at source_path and target_path have
    the same number of lines and yields dictionaries of "inputs" and "targets"
    where inputs are token ids from the " "-split source (and target, resp.) lines
    converted to integers using the token_map.

    Args:
      source_path: path to the file with source sentences.
      target_path: path to the file with target sentences.
      source_token_vocab: text_encoder.TextEncoder object.
      target_token_vocab: text_encoder.TextEncoder object.
      eos: integer to append at the end of each sequence (default: None).

    Yields:
      A dictionary {"inputs": source-line, "targets": target-line} where
      the lines are integer lists converted from tokens in the file lines.
    """
    eos_list = [] if eos is None else [eos]
    with tf.gfile.GFile(source_path, mode="r") as source_file:
        with tf.gfile.GFile(target_path, mode="r") as target_file:
            source, target = source_file.readline(), target_file.readline()
            while source and target:
                source_ints = source_token_vocab.encode(source.strip()) + eos_list
                target_ints = target_token_vocab.encode(target.strip()) + eos_list
                yield {"inputs": source_ints, "targets": target_ints}
                source, target = source_file.readline(), target_file.readline()

def tri_vocabs_token2id_generator(source_path, target_path, firstP_path, imageP_path, source_token_vocab, target_token_vocab, eos=None):
    """Generator for sequence-to-sequence tasks that uses tokens.

    This generator assumes the files at source_path and target_path have
    the same number of lines and yields dictionaries of "inputs" and "targets"
    where inputs are token ids from the " "-split source (and target, resp.) lines
    converted to integers using the token_map.

    Args:
      source_path: path to the file with source sentences.
      firstP_path: path to the file with firstP sentences.
      target_path: path to the file with target sentences.
      source_token_vocab: text_encoder.TextEncoder object.
      target_token_vocab: text_encoder.TextEncoder object.
      eos: integer to append at the end of each sequence (default: None).

    Yields:
      A dictionary {"inputs": source-line, "targets": target-line, "firstP": firstP-line} where
      the lines are integer lists converted from tokens in the file lines.
    """
    eos_list = [] if eos is None else [eos]
    with tf.gfile.GFile(source_path, mode="r") as source_file:
        with tf.gfile.GFile(target_path, mode="r") as target_file:
            with tf.gfile.GFile(firstP_path, mode="r") as firstP_file:         
                image_array = np.load(imageP_path)
                source, target, firstP = source_file.readline(), target_file.readline(), firstP_file.readline()
                counter = 0
                while source and target and firstP:
                    source_ints = source_token_vocab.encode(source.strip()) + eos_list
                    target_ints = target_token_vocab.encode(target.strip()) + eos_list
                    firstP_ints = target_token_vocab.encode(firstP.strip()) + eos_list
                    #JI: add image vectors to inputs
                    imageP = image_array[counter].flatten().tolist()
                    #JI: a hack image vector is the first element of an input list other wise we have to increase max input length and that is tricky
                    imageP_ints = [np.array(imageP)]
                    yield {"inputs": source_ints, "targets": target_ints, "firstP": firstP_ints, "imageP": imageP_ints}
                    source, target, firstP = source_file.readline(), target_file.readline(), firstP_file.readline()
                    counter+=1
                    #JI: hacky counter to repeat image vectors when we use the firstP translation for delibnet
                    if counter == 29000:
                        counter=0

@registry.register_problem
class DelibZhenWmt17(TranslateProblem):
    """Problem spec for WMT17 Zh-En translation."""

    @property
    def targeted_vocab_size(self):
        return 40000 - 1 # subtract for compensation

    @property
    def num_shards(self):
        return 1

    @property
    def source_vocab_name(self):
        return "train_en.dict"

    @property
    def target_vocab_name(self):
        return "train_fr.dict"

    @property
    def input_space_id(self):
        return problem.SpaceID.ZH_TOK

    @property
    def target_space_id(self):
        return problem.SpaceID.EN_TOK
    
    
    # Pre-process two vocabularies and build a generator.
    def generator(self, data_dir, tmp_dir, train):
        # Load source vocabulary.
        tf.logging.info("Loading and processing source vocabulary for %s from:" % ("training" if train else "validation"))
        print('    ' + _ZHEN_VOCAB_FILES[0] + ' ... ', end='')
        sys.stdout.flush()
        with open(_ZHEN_VOCAB_FILES[0], 'rb') as f:
            vocab_src_list = f.read().decode('utf8', 'ignore').splitlines()
        print('Done')
        
        # Load target vocabulary.
        tf.logging.info("Loading and processing target vocabulary for %s from:" % ("training" if train else "validation"))
        print('    ' + _ZHEN_VOCAB_FILES[1] + ' ... ', end='')
        sys.stdout.flush()
        with open(_ZHEN_VOCAB_FILES[1], 'rb') as f:
            vocab_trg_list = f.read().decode('utf8', 'ignore').splitlines()
        print('Done')
        
        # Truncate the vocabulary depending on the given size (strip the reserved tokens).
        #vocab_src_list = vocab_src_list[3:self.targeted_vocab_size+1]
        #vocab_trg_list = vocab_trg_list[3:self.targeted_vocab_size+1]
    
        # Insert the <UNK>.
        #vocab_src_list.insert(0, "<UNK>")
        #vocab_trg_list.insert(0, "<UNK>")    

        # Auto-insert the reserved tokens as: <pad>=0 <EOS>=1 and <UNK>=2.
        source_vocab = text_encoder.TokenTextEncoder(vocab_filename=None, vocab_list=vocab_src_list,
                                                     replace_oov="<UNK>", num_reserved_ids=text_encoder.NUM_RESERVED_TOKENS)
        target_vocab = text_encoder.TokenTextEncoder(vocab_filename=None, vocab_list=vocab_trg_list,
                                                     replace_oov="<UNK>", num_reserved_ids=text_encoder.NUM_RESERVED_TOKENS)
        
        # Select the path: train or dev (small train).
        datapath = _ZHEN_TRAIN_DATASETS if train else _ZHEN_DEV_DATASETS
        
        # Build a generator.
        #return bi_vocabs_token2id_generator(datapath[0], datapath[1], source_vocab, target_vocab, text_encoder.EOS_ID)
        return tri_vocabs_token2id_generator(datapath[0], datapath[1], datapath[2], datapath[3], source_vocab, target_vocab, text_encoder.EOS_ID)
    
    
    def example_reading_spec(self):
      
      #JI: define image input shape here
      data_fields = {
        "inputs": tf.VarLenFeature(tf.int64),
        "targets": tf.VarLenFeature(tf.int64),
        "firstP": tf.VarLenFeature(tf.int64),
        "imageP": tf.FixedLenFeature([1, 19600], tf.float32)
      }
      
      data_items_to_decoders = None
      return (data_fields, data_items_to_decoders)
    
    
    # Build bi-vocabs feature encoders for decoding.
    def feature_encoders(self, data_dir):
        # Load source vocabulary.
        tf.logging.info("Loading and processing source vocabulary from: %s" % _ZHEN_VOCAB_FILES[0])
        with open(_ZHEN_VOCAB_FILES[0], 'rb') as f:
            vocab_src_list = f.read().decode('utf8', 'ignore').splitlines()
        tf.logging.info("Done")
        
        # Load target vocabulary.
        tf.logging.info("Loading and processing target vocabulary from: %s" % _ZHEN_VOCAB_FILES[1])
        with open(_ZHEN_VOCAB_FILES[1], 'rb') as f:
            vocab_trg_list = f.read().decode('utf8', 'ignore').splitlines()
        tf.logging.info("Done")
        
        # Truncate the vocabulary depending on the given size (strip the reserved tokens).
        #vocab_src_list = vocab_src_list[3:self.targeted_vocab_size+1]
        #vocab_trg_list = vocab_trg_list[3:self.targeted_vocab_size+1]        

        # Insert the <UNK>.
        #vocab_src_list.insert(0, "<UNK>")
        #vocab_trg_list.insert(0, "<UNK>")
    
        # Auto-insert the reserved tokens as: <pad>=0 <EOS>=1 and <UNK>=2.
        source_encoder = text_encoder.TokenTextEncoder(vocab_filename=None, vocab_list=vocab_src_list, replace_oov="<UNK>", 
                                                       num_reserved_ids=text_encoder.NUM_RESERVED_TOKENS)
        target_encoder = text_encoder.TokenTextEncoder(vocab_filename=None, vocab_list=vocab_trg_list, replace_oov="<UNK>",
                                                       num_reserved_ids=text_encoder.NUM_RESERVED_TOKENS)       
        return {"inputs": source_encoder, "targets": target_encoder, "firstP": target_encoder}

    
    # inherent the function "hparams"
    def hparams(self, defaults, unused_model_hparams):
        p = defaults
        p.stop_at_eos = int(True)
        target_vocab_size = self._encoders["targets"].vocab_size
        if self.has_inputs:
            source_vocab_size = self._encoders["inputs"].vocab_size
            #JI: define input modality as Generic
            p.input_modality = {
              "inputs": (registry.Modalities.SYMBOL, source_vocab_size),
              "firstP": (registry.Modalities.SYMBOL, target_vocab_size),
              "imageP": (registry.Modalities.GENERIC, None)
            }
        
        p.target_modality = (registry.Modalities.SYMBOL, target_vocab_size)
        if self.has_inputs:
            p.input_space_id = self.input_space_id
        p.target_space_id = self.target_space_id
        if self.is_character_level:
            p.loss_multiplier = 2.0
    

@registry.register_hparams
def zhen_wmt17_transformer_big_v1():
    
    hparams = transformer.transformer_base_v1()
    hparams.hidden_size = 1024
    hparams.filter_size = 4096
    hparams.num_heads = 16
    # hparams.batching_mantissa_bits = 2
    hparams.learning_rate = 0.05
    hparams.layer_prepostprocess_dropout = 0.1
    hparams.learning_rate_warmup_steps = 8000
    hparams.add_hparam("update_delib_only", False)
    #hparams.add_hparam("init_checkpoint", "/experiments/jive/mm-en-de-trans-gaps/model.ckpt-127678")
    return hparams
    

@registry.register_hparams
def transformer_delib_big_v2():
    """HParams for transfomer big delibnet model on WMT."""
    hparams = transformer.transformer_base_v1()
    hparams.hidden_size = 1024
    hparams.filter_size = 4096
    hparams.num_heads = 16
    # hparams.batching_mantissa_bits = 2
    hparams.learning_rate = 0.05
    hparams.layer_prepostprocess_dropout = 0.1
    hparams.learning_rate_warmup_steps = 8000
    
    #hparams = transformer.transformer_big()
    hparams.add_hparam("delib_layers", "0;1;2")
    #hparams.num_hidden_layers = 6
    hparams.add_hparam("update_delib_only", False)
    #JI: for delib set the initilaizing checkpoint here
    hparams.add_hparam("init_checkpoint", "/experiments/jive/mm-en-de-trans-gaps/model.ckpt-127678")
    hparams.shared_embedding_and_softmax_weights = int(False)
    
    return hparams
