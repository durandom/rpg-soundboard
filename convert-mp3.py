#!/usr/bin/env python3

from re import I
import sys
import os
import subprocess
import pathlib
import tempfile
import shutil

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
tmp_directory = tempfile.mkdtemp()


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

        ext = pathlib.Path(in_file).suffix.lower()
        if ext != '.mp3':
            if ext in ['.ogg', '.wav']:
                print(f'convert to mp3: {a_file}')
                tmp_out_file = os.path.join(tmp_directory, a_file + '.mp3')
                subprocess.run(['sox', in_file, tmp_out_file])

                stem = pathlib.Path(in_file).stem
                out_file = os.path.join(dst_dir, stem + '.mp3')
                in_file = tmp_out_file
            else:
                print(f'cant convert {in_file}')
                continue
        else:
            out_file = os.path.join(dst_dir, a_file)

        # https://timothygu.me/lame/usage.html
        # https://svn.code.sf.net/p/lame/svn/trunk/lame/USAGE
        # https://www.stefaanlippens.net/audio_conversion_cheat_sheet/
        # subprocess.run(['lame', '-b 32', '-B 128', '-m','m', in_file, out_file])
        # subprocess.run(['lame', '--abr', '56', '-m','m', in_file, out_file])
        subprocess.run(['lame', '-V9', '-m','m', in_file, out_file])
        print(f'converted {a_file}')


shutil.rmtree(tmp_directory)
