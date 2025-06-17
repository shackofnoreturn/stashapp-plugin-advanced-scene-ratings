import re
import sys
from stashapi.stashapp import StashInterface

# Constants
CATEGORIES_DEFAULT = ["acting", "camera", "story", "intensity", "chemistry"]
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")
PARENT_TAG_NAME = "Advanced Rating"

class StashRatingPlugin:
    def __init__(self, stash: StashInterface):
        self.stash = stash

    def get_categories(self):
        # Read configured categories or fallback to default
        categories_str = self.stash.get_plugin_setting("categories")
        if categories_str:
            categories = [c.strip() for c in categories_str.split(",") if c.strip()]
            if categories:
                return categories
        return CATEGORIES_DEFAULT

    def scan_and_rate_scenes(self):
        categories = self.get_categories()
        min_required_tags = self.stash.get_plugin_setting("minimum_required_tags") or 1
        enable_logging = self.stash.get_plugin_setting("enable_logging") or False

        scenes = self.stash.find_scenes({})
        for scene in scenes:
            tags = [tag['name'] for tag in scene.get('tags', [])]
            scores = {}

            for tag in tags:
                match = TAG_PATTERN.match(tag)
                if match:
                    category, score_str = match.groups()
                    if category in categories:
                        scores[category] = int(score_str)

            if len(scores) >= min_required_tags:
                average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
                final_rating = round(average)
            else:
                final_rating = 0

            if scene.get("rating") != final_rating:
                if enable_logging:
                    print(f"Updating scene '{scene['title']}' to rating {final_rating}")
                self.stash.update_scene(
                    scene_id=scene['id'],
                    rating=final_rating
                )

    def create_tag_structure(self):
        categories = self.get_categories()

        # Check if parent tag exists
        parent_tag = self.stash.find_tag_by_name(PARENT_TAG_NAME)
        if not parent_tag:
            if self.stash.get_plugin_setting("enable_logging"):
                print(f"Creating parent tag '{PARENT_TAG_NAME}'")
            parent_tag = self.stash.create_tag({"name": PARENT_TAG_NAME, "description": "Parent tag for advanced ratings"})

        # Create category tags under parent if missing
        for category in categories:
            cat_tag = self.stash.find_tag_by_name(category)
            if not cat_tag:
                if self.stash.get_plugin_setting("enable_logging"):
                    print(f"Creating category tag '{category}' under '{PARENT_TAG_NAME}'")
                cat_tag = self.stash.create_tag({"name": category, "parent_id": parent_tag['id']})

            # Create numbered tags under each category
            for i in range(1, 6):
                numbered_tag_name = f"{category}_{i}"
                numbered_tag = self.stash.find_tag_by_name(numbered_tag_name)
                if not numbered_tag:
                    if self.stash.get_plugin_setting("enable_logging"):
                        print(f"Creating tag '{numbered_tag_name}' under '{category}'")
                    self.stash.create_tag({"name": numbered_tag_name, "parent_id": cat_tag['id']})

def run_plugin(stash: StashInterface):
    plugin = StashRatingPlugin(stash)

    if len(sys.argv) > 1 and sys.argv[1] == "create-tags":
        plugin.create_tag_structure()
    else:
        plugin.scan_and_rate_scenes()

if __name__ == "__main__":
    stash = StashInterface()  # Assumes environment variables or config handle auth
    run_plugin(stash)
