import stashapi.log as log
from stashapi.stashapp import StashInterface
import sys
import re
import json

# Variables
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")

settings = {
    "categories": "video_quality,acting,camera,story,intensity,chemistry",
    "minimum_required_tags": 5
}
log.debug(f"Displaying contents of `settings`: {settings}")

SVG_IMAGE = (
    "data:image/svg+xml;base64,PCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIi"
    "AiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KDTwhLS0gVXBsb2FkZW"
    "QgdG86IFNWRyBSZXBvLCB3d3cuc3ZncmVwby5jb20sIFRyYW5zZm9ybWVkIGJ5OiBTVkcgUmVwbyBNaXhlciBUb2"
    "9scyAtLT4KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD"
    "0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KDTxnIGlkPSJTVkdSZXBvX2JnQ2Fycm"
    "llciIgc3Ryb2tlLXdpZHRoPSIwIi8+Cg08ZyBpZD0iU1ZHUmVwb190cmFjZXJDYXJyaWVyIiBzdHJva2UtbGluZW"
    "NhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KDTxnIGlkPSJTVkdSZXBvX2ljb25DYXJyaWVyIj"
    "4gPHBhdGggZD0iTTUuNjM2MDUgNS42MzYwNUwxOC4zNjQgMTguMzY0TTUuNjM2MDUgMTguMzY0TDE4LjM2NCA1Lj"
    "YzNjA1TTIxIDEyQzIxIDE2Ljk3MDYgMTYuOTcwNiAyMSAxMiAyMUM3LjAyOTQ0IDIxIDMgMTYuOTcwNiAzIDEyQz"
    "MgNy4wMjk0NCA3LjAyOTQ0IDMgMTIgM0MxNi45NzA2IDMgMjEgNy4wMjk0NCAyMSAxMloiIHN0cm9rZT0iI2ZmZm"
    "ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPiA8L2c+Cg08L3N2Zz4="
)

tag_rating_parent = {
    "name": "Advanced Rating System",
    "description": "Advanced Rating System: Parent tag for all rating categories",
    "image": SVG_IMAGE
}

def main():
    log.info(f"Starting Stash Advanced Rating Plugin ...")
    global stash

    global json_input
    json_input = json.loads(sys.stdin.read())

    log.debug(f"Initializing Stash Interface with server connection: {json_input['server_connection']}")
    stash = StashInterface(json_input["server_connection"])

    log.info(f"Retrieving plugin configuration ...")
    config = stash.get_configuration()["plugins"]
    log.debug(f"Displaying contents of `config`: {config}")

    if "stashAppAdvancedRating" in config:
        settings.update(config["stashAppAdvancedRating"])
        log.debug(f"Here's the entire SETTINGS varoble after changes: {settings}")

    # Final settings
    categories = settings["categories"].split(",") if settings["categories"] else []
    minimum_required_tags = settings["minimum_required_tags"]
    log.info(f"And here are the final categories: {categories} - and min tags: {minimum_required_tags}")

    mode_arg = json_input["args"]["mode"]
    if mode_arg == "process_scenes":
        processScenes(stash, categories, minimum_required_tags)
    if mode_arg == "create_tags":
        createTags(categories)
    if mode_arg == "remove_tags":
        removeTags(categories)

    if "hookContext" in json_input["args"]:
        id = json_input["args"]["hookContext"]["id"]
        if json_input["args"]["hookContext"]["type"] == "Scene.Update.Post":
            stash.run_plugin_task("stashAppAdvancedRating", "Process all", args={"scene_id": id})
            scene = stash.find_scene(id)
            processScene(scene)
            log.debug(f"Made it through the hook ...")

def processScene(scene):
    log.debug("processing scene: %s" % (scene["id"],))
    # When the scene does not meet minimum_required_tags, skip it
    if False:
        pass
    else:
        log.debug("skipping scene")

def processScenes(stash, categories, minimum_required_tags):
    log.info(f"Processing all scenes ...")
    scenes = stash.find_scenes({})
    for scene in scenes:
        calculate_rating_for_scene(stash, scene, categories, minimum_required_tags)
        if "scene_id" in json_input["args"]:
            scene = stash.find_scene(json_input["args"]["scene_id"])
            processScene(scene)
        # else:
            # processScenes()


def find_tag(name, create=False):
    find_tag_tag = stash.find_tag(name, create)
    if find_tag_tag is None:
        log.error(f"Tag does not exist: {name}")
    else:
        log.info(f"Found Tag - ID:{find_tag_tag['id']} Name: {find_tag_tag['name']}")
    return find_tag_tag

def create_tag(obj):
    create_tag_tag = stash.create_tag(obj)
    if create_tag_tag is None:
        log.error(f'Tag already exists: {tag_rating_parent["name"]}')
    else:
        log.info(f"Created Tag - ID:{create_tag_tag['id']} Name: {create_tag_tag['name']}")
    return create_tag_tag

def createTags(categories):
    log.info(f"Ensure the needed tags exist ...")
    find_rating_parent = find_tag(tag_rating_parent)
    if find_rating_parent is None:
        find_rating_parent = create_tag(tag_rating_parent)
        log.info(f"Created parent tag")
    parent_id = find_rating_parent["id"]

    # For each category, create category tag under Advanced Rating
    for cat in categories:
        cat_tag = find_tag(cat, create=True)
        if not cat_tag:
            # cat_tag = stash.create_tag(name=cat, parent_id=parent_id)
            log.info(f"Created category tag: {cat} under Advanced Rating")
        # Create numbered child tags (1 to 5)
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            num_tag = find_tag(num_tag_name)
            # if not num_tag:
            #     stash.create_tag(name=num_tag_name, parent_id=cat_tag["id"])
            #     log.info(f"Created numbered tag: {num_tag_name} under {cat}")

def removeTags(categories):
    log.info(f"Removing tags ...")
    for cat in categories:
        remove_tag(cat)
        
def remove_tag(name):
    remove_tag_tag = find_tag(name)
    if remove_tag_tag is not None:
        stash.destroy_tag(remove_tag_tag['id'])
        log.info(f"Deleted Tag - ID:{remove_tag_tag['id']}: Name: {remove_tag_tag['name']}")


def find_scenes(find_scenes_tag):
    scene_count, scenes = stash.find_scenes(
    f={
        "file_count": {"modifier": "GREATER_THAN", "value": 1},
        "tags": {"modifier": "EXCLUDES", "value": find_scenes_tag},
    },
    filter={
        "per_page": "-1"
    },
    get_count=True,
)
    return scene_count, scenes


def get_plugin_settings(stash):
    log.info(f"Getting plugin settings ...")
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


# Calculate rating for a scene based on its tags
def calculate_rating_for_scene(stash, scene, categories, minimum_required_tags ):
    log.info(f"Calculating rating of scene {scene['title']} based on it's tags ...")
    tags = [tag['name'] for tag in scene['tags']]
    scores = {}
    for tag in tags:
        match = TAG_PATTERN.match(tag)
        if match:
            category, score = match.groups()
            if category in categories:
                scores[category] = int(score)

    if len(scores) < minimum_required_tags:
        log.info(f"Scene '{scene['title']}' skipped, not enough rating tags {scores}")
        return 1

    average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
    final_rating = round(average)
    current_rating = scene.get("rating") or 0

    if current_rating != final_rating:
        log.info(f"Updating scene '{scene['title']}` rating from {current_rating} to {final_rating}")
        stash.update_scene(scene_id=scene['id'], rating=final_rating)
    else:
        log.info(f"Scene '{scene['title']}' rating unchanged at {current_rating}")

if __name__ == "__main__":
    main()
