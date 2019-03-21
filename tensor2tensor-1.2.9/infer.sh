export CUDA_VISIBLE_DEVICES=1
ROOT_MODEL=ttest
ii=1
RPATH=/experiments/jive
beamsize=10
decode_alpha=1.0
split=test2016
ext=attfull
img_ext=npy
setup=multi30k
config=zhen_wmt17
lang=fr
srcext=en
firstp=frst22000.transformer.zhen_wmt17_transformer_big_v1.delib_zhen_wmt17.beam10.alpha1.0.decodes

PROBLEM=delib_zhen_wmt17
#MODEL=transformer__delib
MODEL=transformer
#HPARAMS_SET=transformer_delib_big_v2
HPARAMS_SET=zhen_wmt17_transformer_big_v1
#HPARAMS="shared_embedding_and_softmax_weights=0,delib_layers=0;1;2"
DECODE_HPARAMS="beam_size=${beamsize},alpha=${decode_alpha},batch_size=30"

#if [ "$(split)" == 'train' ]; then
#   DECODE_HPARAMS="beam_size=${beamsize},alpha=${decode_alpha},batch_size=50,return_beams=1"
#fi

DATA_DIR=/experiments/jive/${setup}
#ids=$(ls ${RPATH}/${ROOT_MODEL} | grep "model\.ckpt-[0-9]*.index" | grep -o "[0-9]*")

tmpdir=${ROOT_MODEL}_${ii}

  mkdir $tmpdir
  cp ${RPATH}/${ROOT_MODEL}/model.ckpt-${ii}* $tmpdir
  echo model_checkpoint_path: \"model.ckpt-${ii}\" > $tmpdir/checkpoint

  HYP_FILE=/experiments/jive/${setup}/${split}.${lang}${ext}${ii}
 

#JI: numbers file contains indexes of numpy image vectors for each input sentence 
  python tensor2tensor/bin/t2t-decoder \
    --t2t_usr_dir=../${config} \
    --data_dir=$DATA_DIR \
    --problems=$PROBLEM \
    --model=$MODEL \
    --hparams_set=$HPARAMS_SET \
    --output_dir=$tmpdir \
    --decode_hparams=${DECODE_HPARAMS} \
    --decode_from_file=/experiments/jive/${setup}/${split}.${srcext} \
    --decode_from_file_firstP=/experiments/jive/${setup}/${split}.${firstp} \
    --decode_from_file_imageP=/experiments/jive/${setup}/${split}.${img_ext} \
    --decode_from_file_imageP_idx=/experiments/jive/${setup}/${split}.numbers.txt \
    --decode_to_file=${HYP_FILE}

  rm -rf $tmpdir

