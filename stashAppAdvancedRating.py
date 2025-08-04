from stashapi.stashapp import StashInterface
import stashapi.log as log
import sys
import re
import json

# TAGS
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")
SVG_IMAGE_PARENT = (
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
TAG_RATING_PARENT = {
    "name": "Advanced Rating System",
    "description": "Advanced Rating System: Parent tag for all rating categories",
    "image": SVG_IMAGE_PARENT
}

# GLOBALS
settings = {
    "categories": "video_quality,acting,camera,story,intensity,chemistry",
    "minimum_required_tags": 5
}


# MAIN
def main():
    # get_plugin_settings(stash)
    log.info(f"USER SETTINGS: LOADING ...")
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            raise ValueError("USER SETTINGS: No input received from stdin")
        global json_input
        json_input = json.loads(raw_input)
        log.info(f"USER SETTINGS: OK")
    except json.JSONDecodeError as e:
        log.error(f"USER SETTINGS: Failed to decode JSON: {e}")
        json_input = {}
    except ValueError as e:
        log.error(f"USER SETTINGS: Input error: {e}")
        json_input = {}


    log.info(f"STASH INTERFACE: CONNECTING ...")
    try:
        server_connection = json_input["server_connection"]
        global stash
        stash = StashInterface(server_connection)
        log.info(f"STASH INTERFACE: OK")
    except KeyError:
        log.error("STASH INTERFACE: Missing 'server_connection' in user settings.")
        stash = None
    except Exception as e:
        log.error(f"STASH INTERFACE: Failed to initialize stash interface: {e}")
        stash = None
        stash = StashInterface(json_input["server_connection"])


    log.info("PLUGIN CONFIGURATION: LOADING ...")
    try:
        config = stash.get_configuration().get("plugins", {})
        log.debug(f"CONFIG: {config}")
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to load plugin configuration: {e}")
        config = {}

    if "stashAppAdvancedRating" in config:
        try:
            settings.update(config["stashAppAdvancedRating"])
            log.debug(f"SETTINGS-POST: {settings}")
        except Exception as e:
            log.error(f"PLUGIN CONFIGURATION: Failed to update settings: {e}")
    try:
        global categories
        categories = settings.get("categories", "")
        categories = categories.split(",") if categories else []
        log.debug(f"CATEGORIES: {categories}")
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to process categories: {e}")
        categories = []
    try:
        global minimum_required_tags
        minimum_required_tags = settings["minimum_required_tags"]
        log.debug(f"MINIMUM REQUIRED TAGS: {minimum_required_tags}")
    except KeyError:
        log.error("PLUGIN CONFIGURATION: Missing 'minimum_required_tags' in settings.")
        minimum_required_tags = None
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to load minimum required tags: {e}")
        minimum_required_tags = None
    log.info("PLUGIN CONFIGURATION: OK")


    # ACTIONS
    # Buttons
    if "mode" in json_input["args"]:
        mode_arg = json_input["args"]["mode"]
        if mode_arg == "process_scenes":
            processScenes(stash, categories, minimum_required_tags, allScenes=True)
        if mode_arg == "process_scenes_unrated":
            processScenes(stash, categories, minimum_required_tags, allScenes=False)
        if mode_arg == "create_tags":
            createTags(categories)
        if mode_arg == "remove_tags":
            removeTags(categories)
    
    # Hooks
    if "hookContext" in json_input["args"]:
        sceneID = json_input["args"]["hookContext"]["id"]
        if json_input["args"]["hookContext"]["type"] == "Scene.Update.Post":
            # stash.run_plugin_task("stashAppAdvancedRating", "Process all", args={"scene_id": id})
            scene = stash.find_scene(sceneID)
            processScene(scene)


# FUNCTIONS
def processScene(scene):
    log.debug("PROCESSING SCENE: %s" % (scene["id"],))
    if scene:
        calculate_rating(stash, scene, categories, minimum_required_tags)
    else:
        log.debug("PROCESSING SCENE: SKIPPING ...")

def processScenes(stash, categories, minimum_required_tags, allScenes=True):
    global scenes
    if allScenes:
        log.info("PROCESSING SCENES: ALL ...")
        scenes = stash.find_scenes({})
    else:
        log.info("PROCESSING SCENES: UNRATED ...")
        scenes = stash.find_scenes({})
    
    log.info(f"SCENES {scenes}")
    for scene in scenes:
        calculate_rating(stash, scene, categories, minimum_required_tags)


def find_scenes(find_scenes_tag, scene_rating):
    if scene_rating:
        scene_count, scenes = stash.find_scenes(
            f={
                "file_count": {"modifier": "GREATER_THAN", "value": 1},
                "tags": {"modifier": "EXCLUDES", "value": find_scenes_tag},
                "rating100": {"modifier": "EQUALS", "value": scene_rating}
            },
            filter={
                "per_page": "-1"
            },
            get_count=True
        )
    else:
        scene_count, scenes = stash.find_scenes(
            f={
                "file_count": {"modifier": "GREATER_THAN", "value": 1},
                "tags": {"modifier": "EXCLUDES", "value": find_scenes_tag}
            },
            filter={
                "per_page": "-1"
            },
            get_count=True
        )
    return scene_count, scenes


def find_tag(name, create=False, parent_id=None):
    tag = stash.find_tag(name, create=False)
    if tag is None:
        log.info(f"FIND TAG: {name} not found")
        if create:
            log.info(f"CREATE TAG: {name}")
            try:
                # Create without parent_id (not supported in create_tag)
                tag = stash.create_tag({"name": name})
                if tag:
                    log.info(f"CREATE TAG: {tag['name']} created")
                    # Parent must be set via update_tag
                    if parent_id:
                        try:
                            stash.update_tag({
                                "id": tag["id"],
                                "parent_ids": [parent_id]
                            })
                            log.info(f"UPDATE TAG: Set parent of {tag['name']} to {parent_id}")
                        except Exception as e:
                            log.error(f"UPDATE TAG ERROR: {e}")
                else:
                    log.error(f"CREATE TAG: Failed to create {name}")
            except Exception as e:
                log.error(f"CREATE TAG ERROR: {e}")
                tag = None
    else:
        log.info(f"FIND TAG: {tag['name']} found")
    return tag


def create_tag(obj):
    created_tag = stash.create_tag(obj)
    if created_tag is None:
        log.error(f"CREATE TAG: {obj['name']} already exists")
        return find_tag(obj["name"])
    else:
        log.info(f"CREATE TAG: {created_tag['name']} created")
        return created_tag

def createTags(categories):
    log.info("CREATE TAGS: IN PROGRESS ...")

    # Ensure root tag exists or create it
    root_tag = find_tag(TAG_RATING_PARENT["name"], create=True)
    if not root_tag:
        log.error("CREATE TAGS: Failed to create or retrieve root tag.")
        return
    parent_id = root_tag["id"]

    for cat in categories:
        # Create the main category tag under root
        cat_tag = find_tag(cat, create=True, parent_id=parent_id)
        if not cat_tag:
            log.error(f"CREATE TAGS: Failed to create or retrieve tag for {cat}")
            continue  # Skip this category if it failed
        cat_id = cat_tag["id"]

        # Create numbered child tags under category
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            num_tag = find_tag(num_tag_name, create=True, parent_id=cat_id)
            if not num_tag:
                log.error(f"CREATE TAGS: Failed to create subtag {num_tag_name}")
                continue

def remove_tag(name):
    remove_tag_tag = find_tag(name)
    if remove_tag_tag is not None:
        stash.destroy_tag(remove_tag_tag['id'])
        log.info(f"REMOVE TAG: Removed {remove_tag_tag['name']}")

def removeTags(categories):
    log.info(f"REMOVE TAGS: IN PROGRESS ...")
    remove_tag(TAG_RATING_PARENT["name"])
    for cat in categories:
        remove_tag(cat)

        # Remove numbered child tags under category
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            remove_tag(num_tag_name)

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


def calculate_rating(stash, scene, categories, minimum_required_tags ):
    log.info(f"CALCULATE RATING: {scene['title']}")
    tags = [tag['name'] for tag in scene['tags']]
    scores = {}
    for tag in tags:
        match = TAG_PATTERN.match(tag)
        if match:
            category, score = match.groups()
            if category in categories:
                scores[category] = int(score)

    log.debug(f"SCORES: {scores}")
    if len(scores) < minimum_required_tags:
        log.info(f"CALCULATE RATING: SKIPPED")
        return

    average = sum(scores.get(cat, 0) for cat in categories) / len(categories)
    final_rating = round(average * 20)  # Convert to 0-100 scale
    current_rating = scene.get("rating100") or 0

    log.debug(f"AVERAGE CALCULATION: {average}")
    log.debug(f"CURRENT RATING: {current_rating}")
    log.debug(f"FINAL RATING: {final_rating}")
    try:
        stash.update_scene( {"id": scene["id"], "rating100": final_rating} )
        log.info(f"CALCULATE RATING: Scene {scene['id']} updated with rating {final_rating}")
    except Exception as e:
        log.error(f"CALCULATE RATING: Failed to update scene {scene['id']}: {e}")

if __name__ == "__main__":
    main()
