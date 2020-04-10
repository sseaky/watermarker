# marker.py

为图片添加文字水印
可设置文字**大小、颜色、旋转、间隔、透明度**

2020.4.10  
1、增加 --autofit 可以根据图片大小自动设置字体和间隔  
2、增加 --limit_size 可以控制输出文件大小  



# usage

需要PIL库 `pip install Pillow`

```
usage: marker.py [-h] [-f FILE] [-m MARK] [--autofit] [-o OUT] [-c COLOR]
                 [-s SPACE] [-a ANGLE] [--size SIZE] [--opacity OPACITY]
                 [--limit_size LIMIT_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  image file path or directory

WaterMark:
  -m MARK, --mark MARK  watermark content
  --autofit             optimize arg size/space
  -o OUT, --out OUT     image output directory, default is ./output
  -c COLOR, --color COLOR
                        text color like "#000000", default is #8B8B1B
  -s SPACE, --space SPACE
                        space between watermarks, default is 75
  -a ANGLE, --angle ANGLE
                        rotate angle of watermarks, default is 30
  --size SIZE           font size of text, default is 50
  --opacity OPACITY     opacity of watermarks, default is 0.15

File Size:
  --limit_size LIMIT_SIZE
                        limit the output file size in bytes
```

# 效果
`python marker.py --autofit -m "hello, world" --opacity 0.15 -f input\test.png --limit_size 50000`

![](https://github.com/sseaky/watermarker/raw/master/output/test.jpg)


