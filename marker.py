#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops

TTF_FONT = './font/青鸟华光简琥珀.ttf'


class WaterMark:

    def __init__(self, file, mark=None, size=50, opacity=0.15, color='#8B8B1B', angle=30, space=75, out='output',
                 limit_size=None, autofit=False, **kwargs):
        self.file = file
        self.mark = mark
        self.size = size
        self.opacity = opacity
        self.color = color
        self.angle = angle
        self.space = space
        self.out = out
        self.autofit = autofit
        self.limit_size = limit_size
        self.kwargs = kwargs
        self.cache = {}

    def _set_opacity(self, im):
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity)
        im.putalpha(alpha)
        return im

    @staticmethod
    def _crop_mark(im):
        bg = Image.new(mode='RGBA', size=im.size)
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        return im

    def _gen_mark(self):
        if isinstance(self.mark, str) and sys.version_info[0] < 3:
            self.mark = self.mark.decode('utf-8')
        # 字体宽度
        width = len(self.mark) * self.size

        # 创建水印图片(宽度、高度)
        mark_pic = Image.new(mode='RGBA', size=(width, self.size))

        # 生成文字
        draw_table = ImageDraw.Draw(im=mark_pic)
        draw_table.text(xy=(0, 0),
                        text=self.mark, fill=self.color,
                        font=ImageFont.truetype(TTF_FONT, size=self.size))

        # 裁剪空白
        mark_pic = self._crop_mark(mark_pic)

        # 透明度
        self._set_opacity(mark_pic)
        return mark_pic

    def add_mark(self, im):
        ''' 在im图片上添加水印 im为打开的原图'''

        # 计算斜边长度
        diagonal = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))

        mark_pic = self._gen_mark()

        # 以斜边长度为宽高创建蒙板（旋转后蒙板才足以覆盖原图）
        mask = Image.new(mode='RGBA', size=(diagonal, diagonal))

        # 在大图上生成水印文字，此处mark为上面生成的水印图片
        y, idx = 0, 0
        while y < diagonal:
            # 制造x坐标错位
            x = -int((mark_pic.size[0] + self.space) * 0.5 * idx)
            idx = (idx + 1) % 2

            while x < diagonal:
                # 在该位置粘贴mark水印图片
                mask.paste(mark_pic, (x, y))
                x = x + mark_pic.size[0] + self.space
            y = y + mark_pic.size[1] + self.space

        # 将大图旋转一定角度
        mask = mask.rotate(self.angle)

        # 在原图上添加大图水印
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        im.paste(mask,  # 大图
                 (int((im.size[0] - diagonal) / 2), int((im.size[1] - diagonal) / 2)),  # 坐标
                 mask=mask.split()[3])
        return im

    def save(self, im):
        if im:
            if not Path(self.out).exists():
                Path(self.out).mkdir()
            _path = Path(self.out) / Path(self.file).name
            *_, suffix = str(_path).split('.')
            if self.cache.get('jpeg'):
                new_path = '.'.join(_) + '.jpg'
                im.save(new_path)
            else:
                new_path = '.'.join(_) + '.png'
                im = im.convert('RGB')
                im.save(new_path)
            print('Add mark "{}" to {} successfully, save to {} .'.format(self.mark, self.file, new_path))
        else:
            print('Add mark to {} fail.'.format(self.file))

    def resize(self, im):
        from io import BytesIO
        tmp = BytesIO()
        im.save(tmp, 'png')
        fs = tmp.tell()
        if self.limit_size and fs > self.limit_size:
            # 转成jpeg能减小体积
            if len(im.split()) == 4:
                r, g, b, a = im.split()
                im = Image.merge("RGB", (r, g, b))
                print('Change file type to JPEG.')
                self.cache['jpeg'] = True
            tmp = BytesIO()
            im.save(tmp, 'jpeg')
            fs = tmp.tell()
            im1 = im
            ratio = 1
            # 继续减小尺寸
            while fs > self.limit_size:
                ratio = math.sqrt(self.limit_size / fs) * ratio
                x, y = im.size
                im1 = im.resize((math.floor(x * ratio), math.floor(y * ratio)), Image.ANTIALIAS)
                tmp = BytesIO()
                im1.save(tmp, 'jpeg')
                fs = tmp.tell()
            print('Resize from {} to {}, ratio: {:.2}.'.format(im.size, im1.size, ratio))
            return im1
        return im

    def auto_args(self, im):
        # 垂直方向5行字符，4行空白，字符与空白1:2
        line = 4
        self.size = math.floor(im.size[1] / (line * 3 + 1) * math.cos(math.pi * self.angle / 180))
        self.space = self.size * 2

    def do(self):
        im = Image.open(self.file)
        if self.autofit:
            self.auto_args(im)
        if self.mark:
            im = self.add_mark(im)
        if self.limit_size:
            im = self.resize(im)
        self.save(im)


def parse():
    parse = argparse.ArgumentParser()
    parse1 = parse.add_argument_group(title='WaterMark')
    parse.add_argument('-f', '--file', type=str, help='image file path or directory')
    parse1.add_argument('-m', '--mark', type=str, help='watermark content')
    parse1.add_argument('--autofit', action='store_true', help='optimize arg size/space')
    parse1.add_argument('-o', '--out', default='./output', help='image output directory, default is ./output')
    parse1.add_argument('-c', '--color', default='#8B8B1B', type=str,
                        help='text color like "#000000", default is #8B8B1B')
    parse1.add_argument('-s', '--space', default=75, type=int, help='space between watermarks, default is 75')
    parse1.add_argument('-a', '--angle', default=30, type=int, help='rotate angle of watermarks, default is 30')
    parse1.add_argument('--size', default=50, type=int, help='font size of text, default is 50')
    parse1.add_argument('--opacity', default=0.15, type=float, help='opacity of watermarks, default is 0.15')
    parse2 = parse.add_argument_group(title='File Size')
    parse2.add_argument('--limit_size', type=int, help='limit the output file size in bytes')

    args = parse.parse_args()
    return args.__dict__


if __name__ == '__main__':
    d = parse()
    wm = WaterMark(**d)
    wm.do()
