import re
from stashapi.stashapp import StashInterface

TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")


class StashRatingPlugin:
    def __init__(self, stash: StashInterface):
        self.stash = stash

    def scan_and_rate_scenes(self):
        # Get plugin settings
        raw = self.stash.get_plugin_setting("categories") or ""
        categories = [cat.strip().lower() for cat in raw.split(",") if cat.strip()]
        enable_logging = self.stash.get_plugin_setting("enable_logging") is True
        min_required = int(self.stash.get_plugin_setting("minimum_required_tags") or 0)

        if enable_logging:
            print(f"Using categories: {categories}")
            print(f"Minimum required tags: {min_required}")

        scenes = self.stash.find_scenes({})

        for scene in scenes:
            tags = [tag['name'].lower() for tag in scene['tags']]
            scores = {}

            for tag in tags:
                match = TAG_PATTERN.match(tag)
                if match:
                    category, score = match.groups()
                    if category in categories:
                        scores[category] = int(score)

            if len(scores) < min_required:
                continue  # Not enough category tags found

            # Compute average score
            average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
            final_rating = round(average)

            if scene.get("rating") != final_rating:
                if enable_logging:
                    print(f"Updating scene '{scene['title']}' to rating {final_rating}")
                self.stash.update_scene(
                    scene_id=scene['id'],
                    rating=final_rating
                )
