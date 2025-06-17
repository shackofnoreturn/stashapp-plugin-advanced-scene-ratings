import stashapi.log as log
from stashapi.stashapp import StashInterface
import os
import sys
import re
import json

# Constants
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")


# Defaults if nothing has changed in the stash ui
settings = {"categories": "video_quality,acting,camera,story,intensity,chemistry",
            "minimum_required_tags": 5,
            "enable_logging": False}


def get_plugin_settings(stash):
    # Retrieve each setting or use fallback from the default 'settings' dict
    ## Categories
    categories_str = stash.get_configuration("categories")
    if not categories_str:
        categories_str = settings["categories"]
    categories = [c.strip() for c in categories_str.split(",") if c.strip()]

    ## Minimum required tags
    minimum_required_tags_str = stash.get_configuration("minimum_required_tags")
    try:
        minimum_required_tags = int(minimum_required_tags_str)
    except (TypeError, ValueError):
        minimum_required_tags = settings["minimum_required_tags"]

    ## Enable logging
    enable_logging_str = stash.get_configuration("enable_logging")
    if enable_logging_str:
        enable_logging = enable_logging_str.strip().lower() == "true"
    else:
        enable_logging = settings["enable_logging"]

    ## RETURN
    return categories, minimum_required_tags, enable_logging


# Logging function
def log(msg, enabled):
    if enabled:
        print(msg)


# Ensure tags exist in Stash
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


# Calculate rating for a scene based on its tags
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


# Main function to run the plugin
def main():
    json_input = json.loads(sys.stdin.read())

    FRAGMENT_SERVER = json_input["server_connection"]
    stash = StashInterface(FRAGMENT_SERVER)

    # Example usage of StashInterface to find a scene
    # scene_data = stash.find_scene(1234)
    # log.info(scene_data)
    # log(f"Scene '{scene_data}'", enable_logging)

    # categories, minimum_required_tags, enable_logging = get_plugin_settings(stash)
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
