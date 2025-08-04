# Stashapp Plugin: Advanced Rating System

  This plugin allows you to automatically calculate a scenes rating based on different sub-criteria.

  Curate scenes on audio and video quality or maybe you find performance quality and storylines important as well?
  Set a tag for each type, save the scene and a rating will be calculated based on the set qualities.

  I created this plugin because I used to do this all manually and like to afterwards sort out my videos not only based on a single general rating factor.
  If you want to for example remove all the scenes which didn't look very good image wise. You can now filter for "Video: 1" subrating and make room for others.

## Features
- Create rating criteria based on multiple custom subcategories
- Creates required tag sets and it's relations
- Scans scenes, calculates and applies a general rating
- Custom minimum sub-rating amount (won't calculate rating when for ex only 2 categories are applied)

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
Go to Settings. In the Tasks tab scroll down to section "Plugin Tasks".
You'll find this plugin under the header "Advanced Rating System".

  Here you'll find a couple of buttons to trigger some functionalities.

### Process all scenes
Parses all scenes and looks for rating tags.
When a scene has a rating score for each and every category (or a minimum you're able to set), a scene is considered to be properly rated.
Then all tags are tallied up and averaged out. 

This will be the final rating score for this asset and is applied.

Otherwise when not enough or no rating tags are present, the plugin moves on to the next one.

  Note: this also happens individually when an item is edited in the Stash interface.
  Which is less taxing than doing the entire lot of scenes. (see "Hooks" below)

### Process all unrated scenes
A more lightweight version of the same process being used above.
This maintenance action is only taking action if the scene has no rating applied.

### Create all tags
Ensures all required tags are present and if not, creates them and assigns them to the correct parent tag.
Also looks for the existence of the root tag where all others will be nested under (Advanced Rating System).

### Remove all tags
Ensures all tags related to this plugin are removed and cleaned up.
You would probably use this when you're gonna uninstall the plugin and don't want to manually clean up.
Warning though this is a destructive action, you'll need to rate every asset all over again!

### Hooks
When a scene is updated. Calculation will be done for that single scene only.

## Dependencies (requirements.txt)
- yaml
- stashapi


## Rating criteria example

  Calculated rating here should be 3.6 (3.5 stars depending on your settings)

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
- Set scene rating (rounded down to nearest integer)

# Todo
- Automatically create (update if exists) tags when action is ran and they are not present
- Update Tags: update tag fields when present but doesn't match to expected tag content


# Dev Notes
```rm stable/stashAppAdvancedRating.zip && zip -j "stable/stashAppAdvancedRating.zip" "stashAppAdvancedRating.py" "stashAppAdvancedRating.yml" && sha256sum stable/stashAppAdvancedRating.zip```
