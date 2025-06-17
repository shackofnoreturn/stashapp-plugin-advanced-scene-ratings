import re
from stashapi.stashapp import StashInterface

TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")


class StashRatingPlugin:
    def __init__(self, stash: StashInterface):
        self.stash = stash

    def log(self, msg):
        if self.stash.get_plugin_setting("enable_logging") is True:
            print(msg)

    def get_configured_categories(self):
        raw = self.stash.get_plugin_setting("categories") or ""
        return [cat.strip().lower() for cat in raw.split(",") if cat.strip()]

    def scan_and_rate_scenes(self):
        categories = self.get_configured_categories()
        if not categories:
            self.log("No rating categories configured.")
            return

        min_required_tags = self.stash.get_plugin_setting("minimum_required_tags")
        try:
            min_required_tags = int(min_required_tags) if min_required_tags else 0
        except ValueError:
            min_required_tags = 0

        scenes = self.stash.find_scenes({})

        for scene in scenes:
            tags = [tag['name'] for tag in scene['tags']]
            scores = {}

            for tag in tags:
                match = TAG_PATTERN.match(tag)
                if match:
                    category, score = match.groups()
                    if category in categories:
                        scores[category] = int(score)

            if len(scores) < min_required_tags:
                final_rating = 0
            else:
                average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
                final_rating = round(average)

            if scene.get("rating") != final_rating:
                self.log(f"Updating scene '{scene['title']}' to rating {final_rating}")
                self.stash.update_scene(
                    scene_id=scene['id'],
                    rating=final_rating
                )

    def create_tag_structure(self):
        categories = self.get_configured_categories()
        if not categories:
            self.log("No categories defined to create tag structure.")
            return

        adv_rating = self._get_or_create_tag("Advanced Rating")

        for category in categories:
            parent_tag = self._get_or_create_tag(category, parent_id=adv_rating["id"])
            for i in range(6):  # 0 to 5
                tag_name = f"{category}_{i}"
                self._get_or_create_tag(tag_name, parent_id=parent_tag["id"])
                self.log(f"Ensured tag: {tag_name} under {category}")

    def _get_or_create_tag(self, name, parent_id=None):
        tags = self.stash.find_tags({"name": name})
        if tags:
            return tags[0]
        return self.stash.create_tag({"name": name, "parent_id": parent_id})


def run_plugin(stash: StashInterface):
    plugin = StashRatingPlugin(stash)
    if stash.get_plugin_setting("create_tags_button") == True:
        plugin.create_tag_structure()
    else:
        plugin.scan_and_rate_scenes()
