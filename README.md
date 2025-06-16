# Stashapp Advanced Rating System Plugin

  This plugin makes you able to precisely rate every scene based on multiple criteria

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
1. Populate Rating Tags
2. Curate your scene using tags
3. Rating gets calculated and applied on save


## Dependencies (requirements.txt)
- yaml
- stashapi

## Features
- Let's you create multiple rating criteria
- Creates new set of rating tags to use
- Scans all scenes in your Stash instance
- Detects special rating tags
- Collects all special ratings for all scenes
- Calculates an average or aggregate score for the final rating
- Update the scene's rating accordingly (0 to 5).


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

