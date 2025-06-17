import re

# Predefined categories
CATEGORIES = ["acting", "camera", "story", "intensity", "chemistry"]
TAG_PATTERN = re.compile(r"^([a-z_]+)_(\d)$")

def main(stash):
    scenes = stash.findScenes({})
    for scene in scenes:
        tags = [tag['name'] for tag in scene['tags']]
        scores = {}

        for tag in tags:
            match = TAG_PATTERN.match(tag)
            if match:
                category, score = match.groups()
                if category in CATEGORIES:
                    scores[category] = int(score)

        if scores:
            average = sum(scores.get(cat, 0) for cat in CATEGORIES) / len(CATEGORIES)
            final_rating = round(average)
        else:
            final_rating = 0

        if scene.get("rating") != final_rating:
            print(f"Updating scene '{scene['title']}' to rating {final_rating}")
            # stash.updateScene({
            #     "id": scene['id'],
            #     "rating": final_rating
            # })


def do_logcat(args):
    print(f"TESTING PLUGIN TASKS")