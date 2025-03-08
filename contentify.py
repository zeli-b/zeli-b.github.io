from os import mkdir, walk
from os.path import join, isdir
from shutil import copy, rmtree

from obsidian_to_hugo import ObsidianToHugo


def addfrontmatter(wfile):
    print(wfile)


def main():
    contentdir = './content'
    wikidir = './wiki'
    tmpdir = './tmp'

    for path, directories, filenames in walk(wikidir):
        if '/.git' in path:
            continue

        tpath = join(tmpdir, path[7:])
        isdir(tpath) and rmtree(tpath)
        mkdir(tpath)
        print(tpath)

        if '_index.md' in filenames:
            copy(wfile := join(path, '_index.md'), join(tpath, '_index.md'))
            addfrontmatter(wfile)

        for filename in filenames:
            if not filename.endswith('.md'):
                continue
            if filename == 'README.md':
                continue

            if filename != '_index.md':
                fpath = join(tpath, filename[:-3])

                mkdir(fpath)
                print(fpath)

                copy(wfile := join(path, filename), join(fpath, '_index.md'))
                addfrontmatter(wfile)


    isdir(contentdir) or mkdir(contentdir)
    obsidian_to_hugo = ObsidianToHugo(
        obsidian_vault_dir=tmpdir,
        hugo_content_dir=contentdir,
    )

    obsidian_to_hugo.run()


if __name__ == '__main__':
    main()
