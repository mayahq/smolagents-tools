# VNC Tool Base64 Screenshot Feature

## Overview

The VNC tool has been enhanced to return base64-encoded images when taking screenshots. This feature allows screenshots to be embedded directly in responses and used by agents for visual observations.

## Changes Made

1. **Import Addition**: Added `import base64` to support base64 encoding.

2. **Modified Methods**:
   - `_capture_screen()`: Now reads the captured PNG file and encodes it to base64
   - `_capture_region()`: Similarly enhanced with base64 encoding

3. **New Parameters**:
   - `img_title`: Title attribute for the image tag (default: "VNC Screenshot")
   - `img_alt`: Alt text for the image tag (default: "VNC screen capture")
   - `display`: Whether to display the screenshot ("true" or "false", default: "true")
   - `include_in_next_call`: Whether to include in agent observations ("true" or "false", default: "true")

4. **Output Format**: When a screenshot is taken, the tool now returns:
   - The original success message with file path
   - A formatted HTML image tag with base64-encoded data

## Image Tag Format

The returned image tag follows this format:

```html
<img title="[title]" alt="[description]" src="data:image/png;base64,[base64_data]" display="[true/false]" include_in_next_call="[true/false]">
```

Where:
- `title`: Descriptive title (e.g., "VNC Screenshot")
- `alt`: Alternative text describing the image
- `src`: Base64-encoded PNG data
- `display`: Whether to show the screenshot on screen ("true" or "false")
- `include_in_next_call`: Whether to include in agent observations ("true" or "false")

## Usage Examples

### Basic Screenshot with Defaults
```python
result = await vnc_tool.execute(
    action="capture_screen",
    filename="/tmp/screenshot.png"
)
```

### Screenshot with Custom Parameters
```python
result = await vnc_tool.execute(
    action="capture_screen",
    filename="/tmp/screenshot.png",
    img_title="Application Dashboard",
    img_alt="Main dashboard showing user metrics",
    display="true",
    include_in_next_call="true"
)
```

### Background Processing Screenshot (Not Displayed)
```python
result = await vnc_tool.execute(
    action="capture_screen",
    filename="/tmp/background.png",
    img_title="Background Process",
    img_alt="Screenshot for automated analysis",
    display="false",
    include_in_next_call="false"
)
```

### Region Capture with Custom Parameters
```python
result = await vnc_tool.execute(
    action="capture_region",
    x=100,
    y=100,
    width=800,
    height=600,
    filename="/tmp/region.png",
    img_title="Login Form",
    img_alt="Screenshot of the login form area"
)
```

### Region Capture with Auto-Generated Alt Text
```python
result = await vnc_tool.execute(
    action="capture_region",
    x=200,
    y=150,
    width=640,
    height=480,
    filename="/tmp/region_auto.png",
    img_title="Auto Region"
    # img_alt will be auto-generated as "VNC region capture at (200,150) 640x480"
)
```

## Benefits

1. **Direct Embedding**: Screenshots can be embedded directly in HTML/Markdown without file references
2. **Agent Observations**: Agents can use the visual information for decision-making
3. **No File Dependencies**: The image data is self-contained in the response
4. **Flexible Display Options**: Control whether screenshots are displayed or used for background processing
5. **Custom Metadata**: Parameterize title and alt text for better context
6. **Backward Compatible**: The tool still saves the PNG file as before

## Error Handling

If base64 encoding fails:
- The tool still returns success if the screenshot was saved
- The error is logged
- The output mentions the encoding failure but includes the file path

## Testing

Run the test script to verify the feature:

```bash
python test_vnc_parameterized.py
```

Or try the example:

```bash
python smolagents-tools/examples/vnc_base64_parameterized.py
```

## Notes

- The base64 encoding happens after the screenshot is saved to disk
- Large screenshots will result in long base64 strings
- The feature works for both `capture_screen` and `capture_region` actions
- Region capture still captures the full screen (vncdotool limitation) but includes region info in the alt text when not provided
- All parameters are optional and have sensible defaults