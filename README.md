DelibNet for MMT

Clone of the repository https://github.com/ustctf/delibnet

See this repository for generic issues.
One of the min requirements Tensorflow 1.3.0rc1 and cuda 8.0:  

export LD\_LIBRARY\_PATH=/usr/local/cuda-8.0/lib64

Main changes for MMT are in:

tensor2tensor/models/transformer.py
tensor2tensor/models/transformer\_delibnet.py

For DelibNet also check:

tensor2tensor/utils/model\_builder.py

Examples of confgurations are in:

zhen\_wmt17/zhen\_wmt17\_main.py
zhen\_wmt17/zhen\_wmt17\_mydelib.py

Script for inference:

infer.sh

Looking into this might also help:

tensor2tensor/utils/decoding.py

My comments in all those files start with #JI:
Following them should be sufficient to adapt the models to your problem.

Launch the code:

1. Generate datasets, for example:
tensor2tensor/bin/t2t-datagen --t2t\_usr\_dir=../zhen\_wmt17 --data\_dir=/experiments/jive/multi30k/fr-rnd-att --tmp\_dir=/experiments/jive/tmp --problem=delib\_zhen\_wmt17

2. Examples of commands for either Transformer or DelibNet models (adjust the early stopping criteria to your problem):

CUDA\_VISIBLE\_DEVICES=0 tensor2tensor/bin/t2t-trainer --t2t\_usr\_dir=../zhen\_wmt17 --data\_dir=/experiments/jive/multi30k/fr-att --output\_dir=/experiments/jive/fr-trans-att-full --problems=delib\_zhen\_wmt17 --model=transformer --hparams\_set=zhen\_wmt17\_transformer\_big\_v1 --eval\_early\_stopping\_metric=metrics-delib\_zhen\_wmt17/approx\_bleu\_score --eval\_early\_stopping\_steps=55000 --eval\_early\_stopping\_metric\_minimize=False --eval\_steps=10000 --hparams='batch\_size=800' --train\_steps=100000 --keep\_checkpoint\_max=100 --save\_checkpoints\_secs=1800 >> fr-trans-att-full.txt 2>&1 &


CUDA\_VISIBLE\_DEVICES=0 tensor2tensor/bin/t2t-trainer --t2t\_usr\_dir=../zhen\_wmt17 --data\_dir=/experiments/jive/multi30k/fr-rnd-att --output\_dir=/experiments/jive/mm-en-fr-trans-rnd-delib-att --problems=delib\_zhen\_wmt17 --model=transformer\_\_delib --hparams\_set=transformer\_delib\_big\_v2 --eval\_early\_stopping\_metric=metrics-delib\_zhen\_wmt17/approx\_bleu\_score --eval\_early\_stopping\_steps=55000 --eval\_early\_stopping\_metric\_minimize=False --eval\_steps=10000 --hparams='batch\_size=800' --train\_steps=200000 --keep\_checkpoint\_max=100 --save\_checkpoints\_secs=1800 >> mm-en-fr-rnd.txt 2>&1 &
