from obsidian_to_hugo import ObsidianToHugo

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="./wiki/",
    hugo_content_dir="./content/wiki",
)

obsidian_to_hugo.run()
