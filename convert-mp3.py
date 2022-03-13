#!/usr/bin/env python3

import sys
import os
import subprocess

args = sys.argv[1:]

if len(args) != 2:
    print(f'{sys.argv[0]} src_dir dst_dir')
    sys.exit(1)

src_basedir=args[0]
dst_basedir=args[1]

if not os.path.exists(src_basedir):
    print(f'{src_basedir} does not exist')
    sys.exit(1)

if os.path.exists(dst_basedir):
    print(f'{dst_basedir} must not exist')
    sys.exit(1)

os.mkdir(dst_basedir)
dst_dir = dst_basedir

for dirpath, dirnames, filenames in os.walk(src_basedir):
    dir = dirpath.removeprefix(src_basedir)
    dir = dir.removeprefix('/')

    if len(dir) > 0:
        dst_dir = os.path.join(dst_basedir, dir)
        print(f'create {dst_dir}')
        os.mkdir(dst_dir)

    for a_file in filenames:
        # lame -v -b 32 -B 128 -m m "$fullfile" "converted-mp3/${filename}.mp3"
        in_file = os.path.join(dirpath, a_file)
        out_file = os.path.join(dst_dir, a_file)
        # https://timothygu.me/lame/usage.html
        # https://svn.code.sf.net/p/lame/svn/trunk/lame/USAGE
        # https://www.stefaanlippens.net/audio_conversion_cheat_sheet/
        # subprocess.run(['lame', '-b 32', '-B 128', '-m','m', in_file, out_file])
        # subprocess.run(['lame', '--abr', '56', '-m','m', in_file, out_file])
        subprocess.run(['lame', '-V9', '-m','m', in_file, out_file])

        print(f'convert {a_file}')


