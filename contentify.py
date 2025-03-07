from os import mkdir

from obsidian_to_hugo import ObsidianToHugo

mkdir('./content')
obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="./wiki/",
    hugo_content_dir="./content",
)

obsidian_to_hugo.run()
