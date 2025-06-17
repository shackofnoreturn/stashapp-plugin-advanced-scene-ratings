import stashapi.log as log
from stashapi.stashapp import StashInterface
import os
import sys
import re
import json

# Constants
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")

def processScenes():
    log.info("Processing all scenes ...")
    # if skip_tag not in tags_cache:
    #     tags_cache[skip_tag] = stash.find_tag(skip_tag, create=True).get("id")
    # count = stash.find_scenes(
    #     f={
    #         "tags": {
    #             "depth": 0,
    #             "excludes": [tags_cache[skip_tag]],
    #             "modifier": "INCLUDES_ALL",
    #             "value": [],
    #         }
    #     },
    #     filter={"per_page": 1},
    #     get_count=True,
    # )[0]
    # log.info(str(count) + " scenes to process.")
    # i = 0
    # for r in range(1, int(count / per_page) + 2):
    #     log.info(
    #         "adding tags to scenes: %s - %s %0.1f%%"
    #         % (
    #             (r - 1) * per_page,
    #             r * per_page,
    #             (i / count) * 100,
    #         )
    #     )
    #     scenes = stash.find_scenes(
    #         f={
    #             "tags": {
    #                 "depth": 0,
    #                 "excludes": [tags_cache[skip_tag]],
    #                 "modifier": "INCLUDES_ALL",
    #                 "value": [],
    #             }
    #         },
    #         filter={"page": r, "per_page": per_page},
    #     )
    #     for s in scenes:
    #         processScene(s)
    #         i = i + 1
    #         log.progress((i / count))
    #         time.sleep(1)

def get_plugin_settings(stash):
    log.info("Getting plugin settings ...")
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
    ## RETURN
    return categories, minimum_required_tags


# Ensure tags exist in Stash
def ensure_tags_exist(stash, categories ):
    log.info("Ensure the needed tags exist ...")
    # Create or find "Advanced Rating" parent tag
    parent_tag = stash.find_tag_by_name("Advanced Rating")
    if not parent_tag:
        parent_tag = stash.create_tag(name="Advanced Rating")
        log.info("Created parent tag: Advanced Rating")
    parent_id = parent_tag["id"]

    # For each category, create category tag under Advanced Rating
    for cat in categories:
        cat_tag = stash.find_tag_by_name(cat)
        if not cat_tag:
            cat_tag = stash.create_tag(name=cat, parent_id=parent_id)
            log.info("Created category tag: {cat} under Advanced Rating" )
        # Create numbered child tags (1 to 5)
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            num_tag = stash.find_tag_by_name(num_tag_name)
            if not num_tag:
                stash.create_tag(name=num_tag_name, parent_id=cat_tag["id"])
                log.info("Created numbered tag: {num_tag_name} under {cat}" )


# Calculate rating for a scene based on its tags
def calculate_rating_for_scene(stash, scene, categories, minimum_required_tags ):
    log.info("Calculating rating of scene '{scene['title']}' based on it's tags ...")
    tags = [tag['name'] for tag in scene['tags']]
    scores = {}
    for tag in tags:
        match = TAG_PATTERN.match(tag)
        if match:
            category, score = match.groups()
            if category in categories:
                scores[category] = int(score)

    if len(scores) < minimum_required_tags:
        log.info("Scene '{scene['title']}' skipped, not enough rating tags ({len(scores)})" )
        return 1

    average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
    final_rating = round(average)
    current_rating = scene.get("rating") or 0

    if current_rating != final_rating:
        log.info("Updating scene '{scene['title']}' rating from {current_rating} to {final_rating}" )
        stash.update_scene(scene_id=scene['id'], rating=final_rating)
    else:
        log.info("Scene '{scene['title']}' rating unchanged at {current_rating}" )


# MAIN
log.info("Starting Stash Advanced Rating Plugin ...")
json_input = json.loads(sys.stdin.read())
FRAGMENT_SERVER = json_input["server_connection"]
stash = StashInterface(FRAGMENT_SERVER)

# Configuration Setup
log.info("Retrieving plugin configuration ...")
config = stash.get_configuration()["plugins"]
log.info("Here's the entire CONFIG variable: {config}")
settings = {
    "categories": "",
    # "categories": "video_quality,acting,camera,story,intensity,chemistry",
    "minimum_required_tags": 5
}
log.info("Here's the entire SETTINGS varoble before changes: {settings}")
if "advancedRating" in config:
    settings.update(config["advancedRating"])
    log.info("Here's the entire SETTINGS varoble after changes: {settings}")

# Final settings
log.info("And here are the final settings: {categories}, {minimum_required_tags}")
categories = settings["categories"].split(",") if settings["categories"] else []
minimum_required_tags = settings["minimum_required_tags"]

# categories, minimum_required_tags  = get_plugin_settings(stash)
# ensure_tags_exist(stash, categories )

if "mode" in json_input["args"]:
    PLUGIN_ARGS = json_input["args"]["mode"]
    log.debug(json_input)
    if "processScenes" in PLUGIN_ARGS:
        # Process all scenes
        scenes = stash.find_scenes({})
        for scene in scenes:
            calculate_rating_for_scene(stash, scene, categories, minimum_required_tags )

    #JUNK
        # if "scene_id" in json_input["args"]:
        #     scene = stash.find_scene(json_input["args"]["scene_id"])
        #     processScene(scene)
        # else:
        #     processScenes()

elif "hookContext" in json_input["args"]:
    id = json_input["args"]["hookContext"]["id"]
    if json_input["args"]["hookContext"]["type"] == "Scene.Update.Post":
        stash.run_plugin_task("stashAppAdvancedRating", "Process all", args={"scene_id": id})
#       scene = stash.find_scene(id)
#       processScene(scene)



# Task Execitop, Modes
# if len(sys.argv) > 1:
#     mode = sys.argv[1]
# else:
#     mode = ""

# if mode == "processScenes" or mode == "rate_all":
#     # Process all scenes
#     scenes = stash.find_scenes({})
#     for scene in scenes:
#         calculate_rating_for_scene(stash, scene, categories, minimum_required_tags )

# elif mode == "rate":
#     # Process a single updated scene, Stash passes SCENE_ID env var
#     scene_id = os.environ.get("SCENE_ID")
#     if not scene_id:
#         print("Error: SCENE_ID environment variable not found")

#     scene = stash.find_scene(scene_id)
#     calculate_rating_for_scene(stash, scene, categories, minimum_required_tags )

# else:
#     print("No valid mode specified. Use 'rate', 'rate_all', or 'processScenes'.")
