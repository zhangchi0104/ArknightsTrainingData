if [ ! -d 'ArknightsGameData' ]; then
    git clone https://github.com/Kengxxiao/ArknightsGameData --depth=1
else
    git -C ArknightsGameData pull
fi

if [ ! -d 'text_renderer' ]; then
    git clone https://github.com/Sanster/text_renderer --depth=1
else
    git -C text_renderer pull
fi

python3 ./wording.py
python3 ./text_renderer/main.py --fonts_list fonts.txt --config_file render.yaml --img_width=0 --corpus_dir output/zh_CN/short/ --corpus_mode=list --num_img 15000 --chars_file=output/zh_CN/keys.txt --strict --output_dir=output/zh_CN/short
python3 ./text_renderer/main.py --fonts_list fonts.txt --config_file render.yaml --img_width=0 --corpus_dir output/zh_CN/long/ --corpus_mode=chn --length=7 --num_img 56000 --chars_file=output/zh_CN/keys.txt --strict --output_dir=output/zh_CN/long