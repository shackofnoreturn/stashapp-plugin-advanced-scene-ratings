# Stashapp Plugin: Advanced Rating System

  This plugin makes you able to precisely rate every scene based on multiple criteria
  Curate your scenes using the advanced rating system tags.
  Rating gets calculated and applied on save or on demand.

## Features
- Create rating criteria based on multiple subcategories
- Creates required tag sets
- Scans all scenes and calculates and applies final rating
- Detects special rating tags
- Collects all special ratings for all scenes
- Calculates an average or aggregate score for the final rating
- Update the scene's rating accordingly (0 to 5).

## How to install
1. Go to settings page (cog wheel icon top-right)
2. Go to plugins section (left menu)
3. Under "Available Plugins" click on "Add Source" button
4. Fill in these fields and click "Confirm"
- Name: Advanced Rating System
- Source URL: ```https://github.com/shackofnoreturn/stashapp-plugin-advanced-scene-ratings.git```
5. Unfold "Advanced Rating System" under "Available Plugins" and click the checkmark next to the desired plugins
6. Click "Install" button in the upper right corner


## How to use
Go to Settings. In the Tasks tab scroll down to section "Plugin Tasks"
You'll find this plugin under the header "Advanced Rating System".

  Here you'll find a couple of buttons to trigger some functionalities.

### Process all scenes
Parses all scenes and looks for rating tags.
When a scene has a rating score for each and every category, a scene is considered to be properly rated.
Then all tags are tallied up and averaged out. This will be the final rating score for this asset, so it is applied.
Otherwise when not enough or no rating tags are present, the plugin moves on to the next one.

  Note: this also happens individually when an item is edited in the Stash interface.
  Which is less taxing than doing the entire lot of scenes.

### Process all unrated scenes
A more lightweight version of the same process being used above.
This maintenance action is only taking action if the scene has no rating applied.

### Create all tags
Ensures all required tags are present and if not, creates them and assigns them to the correct parent tag.
Root tag where all others will be nested under is the "Advanced Rating System" tag.

### Remove all tags
Ensures all tags related to this plugin are removed and cleaned up.
You would probably use this when you're gonna uninstall the plugin and don't want to manually clean up.
Warning though this is a destructive action, you'll need to rate every asset all over again!


## Dependencies (requirements.txt)
- yaml
- stashapi


## Rating Criteria (example)

  Calculated rating here should be 3.6 --> 3.5 stars

- Acting
    - acting_3
- Camera
    - camera_4
- Story
    - story_5
- Intensity
    - intensity_2
- Chemistry
    - chemistry_4

**Each one ends in a number (0–5) for rating, and we’ll define the categories as:**

```python
CATEGORIES = ["acting", "camera", "story", "intensity", "chemistry"]
```

## Logic
- For each scene:
    -> Scan all tags
- For each tag matching category_score (e.g., acting_4):
    -> Parse the score
- Collect one score per category
- Average the scores
- Set scene rating (rounded or floored to integer)


rm stable/stashAppAdvancedRating.zip && zip -j "stable/stashAppAdvancedRating.zip" "stashAppAdvancedRating.py" "stashAppAdvancedRating.yml" && sha256sum stable/stashAppAdvancedRating.zip