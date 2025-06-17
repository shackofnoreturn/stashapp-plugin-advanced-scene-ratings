import re
from stashapi.stashapp import StashInterface

TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")

class StashRatingPlugin:
    def __init__(self, stash: StashInterface):
        self.stash = stash

    def get_configured_categories(self):
        category_str = self.stash.settings.get('categories', 'acting,camera,story,intensity,chemistry')
        return [cat.strip().lower() for cat in category_str.split(',') if cat.strip()]

    def scan_and_rate_scenes(self):
        categories = self.get_configured_categories()
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

            if scores:
                average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
                final_rating = round(average)
            else:
                final_rating = 0

            if scene.get("rating") != final_rating:
                print(f"Updating scene '{scene['title']}' to rating {final_rating}")
                self.stash.update_scene(
                    scene_id=scene['id'],
                    rating=final_rating
                )
