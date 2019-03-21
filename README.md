DelibNet for MMT

Clone of the repository https://github.com/ustctf/delibnet

See this repository for generic issues.
One of the min requirements Tensorflow 1.3.0rc1 and cuda 8.0:  

```
export LD\_LIBRARY\_PATH=/usr/local/cuda-8.0/lib64
```
# Main changes for MMT are in:

https://github.com/ImperialNLP/MMT-Delib/blob/master/tensor2tensor-1.2.9/tensor2tensor/models/transformer.py 
https://github.com/ImperialNLP/MMT-Delib/blob/master/tensor2tensor-1.2.9/tensor2tensor/models/transformer_delibnet.py

For DelibNet also check:

https://github.com/ImperialNLP/MMT-Delib/blob/master/tensor2tensor-1.2.9/tensor2tensor/utils/model_builder.py

Examples of confgurations are in:

https://github.com/ImperialNLP/MMT-Delib/blob/master/zhen_wmt17/zhen_wmt17_main.py
https://github.com/ImperialNLP/MMT-Delib/blob/master/zhen_wmt17/zhen_wmt17_mydelib.py

Script for inference:

https://github.com/ImperialNLP/MMT-Delib/blob/master/tensor2tensor-1.2.9/infer.sh

Looking into this might also help:
 
https://github.com/ImperialNLP/MMT-Delib/blob/master/tensor2tensor-1.2.9/tensor2tensor/utils/decoding.py

**My comments in all those files start with #JI:**
**Following them should be sufficient to adapt the models to your problem.**

# Launch the code:

1. Generate datasets, for example:
```
tensor2tensor/bin/t2t-datagen --t2t_usr_dir=../zhen_wmt17 --data_dir=/experiments/jive/multi30k/fr-att --tmp_dir=/experiments/jive/tmp --problem=delib_zhen_wmt17
```
2. Examples of commands for either Transformer or DelibNet models (adjust the early stopping criteria to your problem):
```
CUDA_VISIBLE_DEVICES=0 tensor2tensor/bin/t2t-trainer --t2t_usr_dir=../zhen_wmt17 --data_dir=/experiments/jive/multi30k/fr-att --output_dir=/experiments/jive/fr-trans-att-full --problems=delib_zhen_wmt17 --model=transformer --hparams_set=zhen_wmt17_transformer_big_v1 --eval_early_stopping_metric=metrics-delib_zhen_wmt17/approx_bleu_score --eval_early_stopping_steps=50000 --eval_early_stopping_metric_minimize=False --eval_steps=10000 --hparams='batch_size=800' --train_steps=100000 --keep_checkpoint_max=100 --save_checkpoints_secs=1800 >> fr-trans-att-full.txt 2>&1 &
```
```
CUDA_VISIBLE_DEVICES=0 tensor2tensor/bin/t2t-trainer --t2t_usr_dir=../zhen_wmt17 --data_dir=/experiments/jive/multi30k/fr-att --output_dir=/experiments/jive/mm-en-fr-trans-rnd-delib-att --problems=delib_zhen_wmt17 --model=transformer__delib --hparams_set=transformer_delib_big_v2 --eval_early_stopping_metric=metrics-delib_zhen_wmt17/approx_bleu_score --eval_early_stopping_steps=50000 --eval_early_stopping_metric_minimize=False --eval_steps=10000 --hparams='batch_size=800' --train_steps=200000 --keep_checkpoint_max=100 --save_checkpoints_secs=1800 >> mm-en-fr-rnd.txt 2>&1 &
```

For any questions please email: jive at ic.ac.uk
