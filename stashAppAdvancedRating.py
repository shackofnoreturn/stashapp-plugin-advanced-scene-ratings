import os
import sys
import re
from stashapi.stashapp import StashInterface

# Constants
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")

def get_plugin_settings(stash):
    categories_str = stash.get_plugin_setting("categories") or "acting,camera,story,intensity,chemistry"
    categories = [c.strip() for c in categories_str.split(",") if c.strip()]
    minimum_required_tags = int(stash.get_plugin_setting("minimum_required_tags") or 3)
    enable_logging = stash.get_plugin_setting("enable_logging") == "true"
    return categories, minimum_required_tags, enable_logging

def log(msg, enabled):
    if enabled:
        print(msg)

def ensure_tags_exist(stash, categories, enable_logging):
    # Create or find "Advanced Rating" parent tag
    parent_tag = stash.find_tag_by_name("Advanced Rating")
    if not parent_tag:
        parent_tag = stash.create_tag(name="Advanced Rating")
        log("Created parent tag: Advanced Rating", enable_logging)
    parent_id = parent_tag["id"]

    # For each category, create category tag under Advanced Rating
    for cat in categories:
        cat_tag = stash.find_tag_by_name(cat)
        if not cat_tag:
            cat_tag = stash.create_tag(name=cat, parent_id=parent_id)
            log(f"Created category tag: {cat} under Advanced Rating", enable_logging)
        # Create numbered child tags (1 to 5)
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            num_tag = stash.find_tag_by_name(num_tag_name)
            if not num_tag:
                stash.create_tag(name=num_tag_name, parent_id=cat_tag["id"])
                log(f"Created numbered tag: {num_tag_name} under {cat}", enable_logging)

def calculate_rating_for_scene(stash, scene, categories, minimum_required_tags, enable_logging):
    tags = [tag['name'] for tag in scene['tags']]
    scores = {}
    for tag in tags:
        match = TAG_PATTERN.match(tag)
        if match:
            category, score = match.groups()
            if category in categories:
                scores[category] = int(score)

    if len(scores) < minimum_required_tags:
        log(f"Scene '{scene['title']}' skipped, not enough rating tags ({len(scores)})", enable_logging)
        return

    average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
    final_rating = round(average)
    current_rating = scene.get("rating") or 0

    if current_rating != final_rating:
        log(f"Updating scene '{scene['title']}' rating from {current_rating} to {final_rating}", enable_logging)
        stash.update_scene(scene_id=scene['id'], rating=final_rating)
    else:
        log(f"Scene '{scene['title']}' rating unchanged at {current_rating}", enable_logging)

def main():
    stash = StashInterface()

    categories, minimum_required_tags, enable_logging = get_plugin_settings(stash)
    ensure_tags_exist(stash, categories, enable_logging)

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = ""

    if mode == "processScenes" or mode == "rate_all":
        # Process all scenes
        scenes = stash.find_scenes({})
        for scene in scenes:
            calculate_rating_for_scene(stash, scene, categories, minimum_required_tags, enable_logging)

    elif mode == "rate":
        # Process a single updated scene, Stash passes SCENE_ID env var
        scene_id = os.environ.get("SCENE_ID")
        if not scene_id:
            print("Error: SCENE_ID environment variable not found")
            return
        scene = stash.find_scene(scene_id)
        calculate_rating_for_scene(stash, scene, categories, minimum_required_tags, enable_logging)

    else:
        print("No valid mode specified. Use 'rate', 'rate_all', or 'processScenes'.")

if __name__ == "__main__":
    main()
