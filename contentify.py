from datetime import datetime
from os import mkdir, walk, popen
from os.path import join, isdir, dirname, basename, getmtime
from re import compile
from shutil import copy, copytree, rmtree
from time import time

from obsidian_to_hugo import ObsidianToHugo


def addfrontmatter(wfile, tfile):
    with open(tfile, 'w') as tmpfile:
        if wfile.endswith('_index.md'):
            title = basename(dirname(wfile))
        else:
            title = basename(wfile)[:-3]

        date = popen(f"cd wiki; git log -1 --pretty=format:%ci \"{wfile[7:]}\"").read()
        if not date:
            print("wtf", wfile)
            date = datetime.now().astimezone()
        else:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %z')
        date = date.strftime('%Y-%m-%dT%H:%M:%S%z')
        date = date[:-2] + ':' + date[-2:]

        tmpfile.write('---\n')
        tmpfile.write(f'title: {title}\n')
        tmpfile.write(f'date: {date}\n')
        tmpfile.write('---\n')
        with open(wfile, 'r') as wikifile:
            while buffer := wikifile.read(1024):
                tmpfile.write(buffer)


refre = compile(r"\!\[([^\{\}]*)\]\(\{\{< ref \"([^\{\}]+)\" >\}\}\)")


def imager(content):
    new_content = ""
    while match := refre.search(content):
        s, e = match.span()

        src = match.groups()[1][7:]

        new_content += content[:s]
        new_content += f"{{{{< figure src=\"{src}\" >}}}}"
        content = content[e:]

    new_content += content
        
    return new_content

def main():
    starttime = time()

    contentdir = './content'
    wikidir = './wiki'
    tmpdir = './tmp'
    staticdir = './static'

    isdir(staticdir) and rmtree(staticdir)
    copytree(join(wikidir, "static"), staticdir)

    for path, directories, filenames in walk(wikidir):
        if '/.git' in path:
            continue

        tpath = join(tmpdir, path[7:])
        isdir(tpath) and rmtree(tpath)
        mkdir(tpath)

        if '_index.md' in filenames:
            addfrontmatter(join(path, '_index.md'), join(tpath, '_index.md'))

        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            if filename == 'README.md':
                continue

            if filename != '_index.md':
                fpath = join(tpath, filename[:-3])

                mkdir(fpath)

                addfrontmatter(join(path, filename), join(fpath, '_index.md'))


    isdir(contentdir) or mkdir(contentdir)
    obsidian_to_hugo = ObsidianToHugo(
        obsidian_vault_dir=tmpdir,
        hugo_content_dir=contentdir,
        processors=[imager]
    )

    obsidian_to_hugo.run()

    et = (time() - starttime) * 1000
    print(f'Total in {int(et):,} ms')


if __name__ == '__main__':
    main()
