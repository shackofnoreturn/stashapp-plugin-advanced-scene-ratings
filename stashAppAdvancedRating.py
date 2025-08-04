from stashapi.stashapp import StashInterface
import stashapi.log as log
import sys
import re
import json

# TAGS
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")
SVG_TAG_IMG = (
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
    "image": SVG_TAG_IMG
}

# GLOBALS
settings = {
    "categories": "video_quality,acting,camera,story,intensity,chemistry",
    "minimum_required_tags": 5,
    "allow_destructive_actions": False
}


# MAIN
def main():
    global json_input, stash, categories, minimum_required_tags

    json_input = read_stdin_json()
    stash = connect_to_stash(json_input)
    config = load_plugin_config(stash)

    update_settings_from_config(config)
    categories = get_categories()
    minimum_required_tags = get_minimum_required_tags()
    allow_destructive_actions = get_allow_destructive_actions()

    handle_actions(json_input, stash, categories, minimum_required_tags)
    handle_hooks(json_input, stash)


# MAIN FUNCTIONS
def read_stdin_json():
    log.info("READING INPUT ...")
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            raise ValueError("READ STDIN JSON: No input received from stdin")
        return json.loads(raw_input)
    except json.JSONDecodeError as e:
        log.error(f"READ STDIN JSON: Failed to decode JSON: {e}")
    except ValueError as e:
        log.error(f"READ STDIN JSON: Input error: {e}")
    return {}

def connect_to_stash(json_input):
    log.info("CONNECTING STASH INTERFACE ...")
    try:
        server_connection = json_input["server_connection"]
        return StashInterface(server_connection)
    except KeyError:
        log.error("STASH INTERFACE: Missing 'server_connection' in user settings.")
    except Exception as e:
        log.error(f"STASH INTERFACE: Failed to initialize stash interface: {e}")
    return None

def load_plugin_config(stash):
    log.info("LOADING PLUGIN CONFIGURATION ...")
    try:
        return stash.get_configuration().get("plugins", {})
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to load plugin configuration: {e}")
        return {}

def update_settings_from_config(config):
    log.info("UPDATING SETTINGS WITH CONFIG ...")
    try:
        if "stashAppAdvancedRating" in config:
            settings.update(config["stashAppAdvancedRating"])
            log.debug(f"SETTINGS-POST: {settings}")
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to update settings: {e}")

def get_categories():
    log.info("GET CATEGORIES ...")
    try:
        cats = settings.get("categories", "")
        result = cats.split(",") if cats else []
        log.debug(f"CATEGORIES: {result}")
        return result
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to process categories: {e}")
        return []

def get_minimum_required_tags():
    log.info("GET MINIMUM REQUIREMENT ...")
    try:
        value = settings["minimum_required_tags"]
        log.debug(f"MINIMUM REQUIRED TAGS: {value}")
        return value
    except KeyError:
        log.error("PLUGIN CONFIGURATION: Missing 'minimum_required_tags' in settings.")
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to load minimum required tags: {e}")
    return None

def get_allow_destructive_actions():
    log.info("GET ALLOW DESTRUCTIVE ACTIONS ...")
    try:
        global allow_destructive_actions
        allow_destructive_actions = settings.get("allow_destructive_actions", False)
        log.debug(f"ALLOW DESTRUCTIVE ACTIONS: {allow_destructive_actions}")
    except Exception as e:
        log.error(f"PLUGIN CONFIGURATION: Failed to read 'allow_destructive_actions': {e}")
        allow_destructive_actions = False

def handle_actions(json_input, stash, categories, minimum_required_tags):
    log.info("HANDLING ACTION ...")
    args = json_input.get("args", {})
    mode = args.get("mode")
    if mode == "process_scenes":
        processScenes(stash, categories, minimum_required_tags, allScenes=True)
    elif mode == "process_scenes_unrated":
        processScenes(stash, categories, minimum_required_tags, allScenes=False)
    elif mode == "create_tags":
        createTags(categories)
    elif mode == "remove_tags":
        removeTags(categories)

def handle_hooks(json_input, stash):
    log.info("HANDLING HOOK ...")
    args = json_input.get("args", {})
    hook = args.get("hookContext", {})
    if hook.get("type") == "Scene.Update.Post":
        sceneID = hook.get("id")
        scene = stash.find_scene(sceneID)
        processScene(scene)   

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
        log.debug(f"CALCULATE RATING: SKIPPED")
    else:
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


# SCENES
def processScene(scene):
    if scene:
        log.info("PROCESSING SCENE: %s" % (scene["id"],))
        calculate_rating(stash, scene, categories, minimum_required_tags)
    else:
        log.debug("PROCESSING SCENE: SKIPPING ...")

def processScenes(stash, categories, minimum_required_tags, allScenes=True):
    global scenes
    if allScenes:
        log.info("PROCESSING ALL SCENES")
        scenes = stash.find_scenes({})
    else:
        log.info("PROCESSING UNRATED SCENES")
        scenes = stash.find_scenes({})
    
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


# TAGS
def find_tag(name, create=False, parent_id=None):
    tag = stash.find_tag(name, create=False)
    if tag is None:
        log.debug(f"FIND TAG: {name} not found")
        if create:
            log.debug(f"FIND TAG: Creating {name}")
            try:
                tag = stash.create_tag({"name": name})
                if tag:
                    log.debug(f"CREATE TAG: {tag['name']} created")
                    # Parent must be set via update_tag
                    if parent_id:
                        try:
                            stash.update_tag({
                                "id": tag["id"],
                                "parent_ids": [parent_id],
                                "image": SVG_TAG_IMG
                            })
                            log.debug(f"FIND TAG: Set parent of {tag['name']} to {parent_id}")
                        except Exception as e:
                            log.error(f"FIND TAG ERROR: {e}")
                else:
                    log.error(f"FIND TAG: Failed to create {name}")
            except Exception as e:
                log.error(f"FIND TAG ERROR: {e}")
                tag = None
    else:
        log.debug(f"FIND TAG: {tag['name']} found")
    return tag

def create_tag(obj):
    created_tag = stash.create_tag(obj)
    if created_tag is None:
        log.error(f"CREATE TAG: {obj['name']} already exists")
        return find_tag(obj["name"])
    else:
        log.debug(f"CREATE TAG: {created_tag['name']} created")
        return created_tag

def createTags(categories):
    log.info("CREATING TAGS ...")

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
    try:
        remove_tag_tag = find_tag(name)
        if remove_tag_tag is not None:
            stash.destroy_tag(remove_tag_tag['id'])
            log.debug(f"REMOVE TAG: Removed {remove_tag_tag['name']}")
        else:
            log.warning(f"REMOVE TAG: Tag '{name}' not found")
    except Exception as e:
        log.error(f"REMOVE TAG: Failed to remove tag '{name}' — {str(e)}")

def removeTags(categories):
    log.info(f"REMOVING TAGS ...")
    if not allow_destructive_actions:
        log.warning("REMOVE TAGS: Destructive actions are disabled. Enable 'allow_destructive_actions' in plugin settings to proceed.")
        return

    # Remove root tag
    remove_tag(TAG_RATING_PARENT["name"])
    for cat in categories:
        # Remove rating category tags
        remove_tag(cat)
        # Remove numbered child tags under each category
        for i in range(1, 6):
            num_tag_name = f"{cat}_{i}"
            remove_tag(num_tag_name)

if __name__ == "__main__":
    main()
