from datetime import datetime
from os import mkdir, walk, popen, remove
from os.path import join, isdir, dirname, basename, getmtime, isfile
from re import compile, split
from shutil import copy, copytree, rmtree
from time import time

from obsidian_to_hugo import ObsidianToHugo


def addfrontmatter(wfile, tfile):
    with open(tfile, 'w') as tmpfile:
        if wfile.endswith('_index.md'):
            title = '대문'
        else:
            title = basename(wfile)[:-3]

        date = popen(f"cd wiki; git log -1 --pretty=format:%ci \"{wfile[7:]}\"").read()
        if not date:
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


def fillfrontmatter(path):
    title = basename(dirname(path))
    date = datetime.now().astimezone()
    date = date.strftime('%Y-%m-%dT%H:%M:%S%z')
    date = date[:-2] + ':' + date[-2:]

    with open(path, 'w') as file:
        file.write("---\n")
        file.write(f"title: {title}\n")
        file.write(f"date: {date}\n")
        file.write("---\n")


refre = compile(r"\!\[([^\{\}]*)\]\(\{\{< ref \"([^\{\}]+)\" >\}\}\)")


def imager(content):
    new_content = ""
    while match := refre.search(content):
        s, e = match.span()

        src = match.groups()[1][7:]

        new_content += content[:s]
        new_content += f"{{{{< figure src=\"/{src}\" >}}}}"
        content = content[e:]

    new_content += content
        
    return new_content


iscommitre = compile(r'^[0-9a-f]{7} .*')


def main():
    starttime = time()

    contentdir = './content'
    wikidir = './wiki'
    tmpdir = './tmp'
    staticdir = './static'
    changesdir = './wiki/changes.md'

    isdir(staticdir) and rmtree(staticdir)
    copytree(join(wikidir, "static"), staticdir)

    isdir(tmpdir) and rmtree(tmpdir)


    # -- recent changes
    changesraw = popen(
        'git config core.quotepath false ; '
        'cd wiki ; '
        'git log --pretty=format:"%h %s - %an" --name-only -n 50 -z'
    ).read()
    # changesraw = changesraw.split('\n')
    changesraw = split(r'\n|\0', changesraw)
    changes = list()
    for i in range(len(changesraw)):
        line = changesraw[i].strip()
        iscommit = iscommitre.match(changesraw[i])

        if not line:
            continue

        if iscommit:
            prefix = '- '
            line = line[8:]
        else:
            if line.endswith(".md"):
                line = line[:-3]
            if isdir(join(wikidir, line)) or isfile(join(wikidir, line) + ".md"):
                line = f'[[{line}]]'
            prefix = '  - '

        changesraw[i] = prefix + line

    with open(changesdir, 'w') as file:
        file.write('\n'.join(changesraw))


    for path, directories, filenames in walk(wikidir):
        if '/.git' in path:
            continue

        tpath = join(tmpdir, path[7:])
        isdir(tpath) or mkdir(tpath)
        isfile(join(tpath, '_index.md')) or fillfrontmatter(join(tpath, '_index.md'))

        bn = basename(path)

        if '_index.md' in filenames:
            addfrontmatter(join(path, '_index.md'), join(tpath, '_index.md'))

        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            if filename == 'README.md':
                continue
            if filename == '_index.md':
                continue

            fbn = filename[:-3]

            isdir(join(tpath, fbn)) or mkdir(join(tpath, fbn))
            addfrontmatter(join(path, filename), join(tpath, fbn, '_index.md'))

    rmtree(join(tmpdir, 'static'))


    isdir(contentdir) or mkdir(contentdir)
    obsidian_to_hugo = ObsidianToHugo(
        obsidian_vault_dir=tmpdir,
        hugo_content_dir=contentdir,
        processors=[imager]
    )

    obsidian_to_hugo.run()

    remove(changesdir)

    et = (time() - starttime) * 1000
    print(f'Total in {int(et):,} ms')


if __name__ == '__main__':
    main()
