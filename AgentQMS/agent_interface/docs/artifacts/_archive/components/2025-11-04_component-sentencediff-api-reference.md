---
type: "component"
category: "api-reference"
status: "active"
version: "1.0"
tags: ['component', 'api-reference', 'sentence-diff', 'schema-engine', 'ui-component']
title: "SentenceDiff Component API Reference"
date: "2025-11-04 00:00 (KST)"
---

# SentenceDiff Component API Reference

## Overview

The `SentenceDiff` component provides advanced sentence comparison functionality with color-coded character-level diffs, statistics, and professional styling. It supports both inline and side-by-side display modes and integrates seamlessly with the schema engine.

**Component Type**: `sentence_diff`
**Status**: ✅ Active and implemented
**Location**: `streamlit_app/schema_engine/components/`

## Table of Contents

- [Quick Start](#quick-start)
- [YAML Configuration](#yaml-configuration)
- [Configuration Parameters](#configuration-parameters)
- [Display Modes](#display-modes)
- [Current Implementation](#current-implementation)
- [API Methods](#api-methods)
- [Features](#features)
- [Implementation Details](#implementation-details)
- [Examples](#examples)

## Quick Start

### Basic Usage
```yaml
- type: sentence_diff
  key: my_diff
  original_source: "data.original_text"
  corrected_source: "data.corrected_text"
```

### Direct Python Usage
```python
from streamlit_app.schema_engine.components.library.sentence_diff import SentenceDiff

diff = SentenceDiff()
diff.render_diff("Hello world", "Hello beautiful world", mode="side_by_side")
```

## YAML Configuration

### Schema Definition
```yaml
- type: sentence_diff
  key: component_key
  original_source: "data_source_path"
  corrected_source: "data_source_path"
  mode: "side_by_side"
  original_label: "Original Text"
  corrected_label: "Corrected Text"
  visible_when:
    field: condition_field
    operator: not_empty
```

### Required Parameters
- `original_source`: Data source path for original text
- `corrected_source`: Data source path for corrected text

### Optional Parameters
- `mode`: Display mode (`"side_by_side"` or `"inline"`)
- `original_label`: Label for original text
- `corrected_label`: Label for corrected text
- `visible_when`: Conditional visibility rules

## Configuration Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `original_source` | string | - | ✅ | Data source path for original text |
| `corrected_source` | string | - | ✅ | Data source path for corrected text |
| `mode` | string | `"side_by_side"` | ❌ | Display mode: `"inline"` or `"side_by_side"` |
| `original_label` | string | `"Original"` | ❌ | Display label for original text |
| `corrected_label` | string | `"Corrected"` | ❌ | Display label for corrected text |
| `visible_when` | object | - | ❌ | Conditional visibility configuration |

## Display Modes

### Side-by-Side Mode (Default)
Professional table-based comparison with:
- Character-level diff highlighting
- Color coding (red for deletions, green for additions)
- Statistics display (+X additions, -Y deletions)
- Responsive design with proper scrolling

### Inline Mode
Compact unified diff format with:
- Line-by-line comparison
- Traditional diff syntax
- Space-efficient display

## Current Implementation

### Active in UI
The component is currently implemented in the **Inference Page** with two instances:

#### Single Sentence Mode
```yaml
# Location: streamlit_app/page_schemas/pages/inference.yaml
- type: sentence_diff
  key: single_diff
  original_source: "selected_sample.err_sentence"
  corrected_source: "inference_result.result.corrected"
  visible_when:
    field: inference_result
    operator: not_empty
```

#### Custom Text Mode
```yaml
- type: sentence_diff
  key: custom_diff
  original_source: "custom_text_input"
  corrected_source: "custom_result.result.corrected"
  visible_when:
    field: custom_result
    operator: not_empty
```

### File Locations
- **Component Class**: `streamlit_app/schema_engine/components/sample_views.py`
- **Core Logic**: `streamlit_app/schema_engine/components/library/sentence_diff.py`
- **Renderer**: `streamlit_app/schema_engine/renderers/custom_component_renderer.py`
- **Schema Usage**: `streamlit_app/page_schemas/pages/inference.yaml`

## API Methods

### Core Methods

#### `render_diff(text1, text2, label1, label2, mode)`
Render a diff between two sentences.

**Parameters:**
- `text1` (str): Original text
- `text2` (str): Corrected text
- `label1` (str): Label for original text
- `label2` (str): Label for corrected text
- `mode` (str): Display mode

#### `render_multi_sentence_comparison(sentences, mode)`
Render comparison for multiple sentence pairs with tabbed interface.

**Parameters:**
- `sentences` (list): List of tuples (text1, text2, label1, label2)
- `mode` (str): Display mode

#### `render_multiple_errors(errors, mode)`
Render multiple errors from a single sample with tabbed navigation.

**Parameters:**
- `errors` (list): List of error dictionaries
- `mode` (str): Display mode

### Schema Integration Methods

#### `SentenceDiffComponent.render(component, context)`
Schema-driven rendering method.

**Parameters:**
- `component` (ComponentSchema): Schema configuration
- `context` (dict): Data binding context

## Features

### ✅ Implemented Features
- **Character-level diff detection** with precise highlighting
- **Color-coded visualization** (red deletions, green additions)
- **Statistics display** showing additions/deletions count
- **Responsive design** with proper text wrapping and scrolling
- **Multiple display modes** (side-by-side table, inline diff)
- **Tabbed interface** for multiple comparisons
- **Schema engine integration** with data binding
- **Conditional visibility** support
- **Error handling** and validation
- **Professional styling** matching application theme

### 🎯 Key Capabilities
- Handles Korean text with proper Unicode support
- Automatic text normalization and escaping
- Memory-efficient rendering for large texts
- Consistent styling with other UI components

## Implementation Details

### CSS Architecture
The component includes comprehensive CSS styling for:
- Table-based layouts with proper borders and spacing
- Color schemes for diff highlighting
- Responsive behavior and scrolling
- Typography and visual hierarchy
- Animation and interaction states

### Data Binding
Integrates with the schema engine's data binding system:
- Supports session state data sources
- Function-based data resolution
- Nested object property access
- Type conversion and validation

### Error Handling
Robust error handling for:
- Missing data sources
- Invalid text inputs
- Rendering failures
- Schema validation errors

## Examples

### Basic Sentence Comparison
```python
from streamlit_app.schema_engine.components.library.sentence_diff import SentenceDiff

diff = SentenceDiff()

# Simple comparison
diff.render_diff(
    "I goed to the store",
    "I went to the store",
    "Error",
    "Corrected"
)
```

### Multiple Sentence Comparison
```python
sentences = [
    ("I goed home", "I went home", "Sample 1", "Corrected 1"),
    ("She don't like it", "She doesn't like it", "Sample 2", "Corrected 2")
]

diff.render_multi_sentence_comparison(sentences, mode="side_by_side")
```

### Error Analysis Display
```python
errors = [
    {
        "type": "subject_verb_agreement",
        "err_sentence": "He go to school",
        "cor_sentence": "He goes to school",
        "original_target_part": "go",
        "golden_target_part": "goes"
    }
]

diff.render_multiple_errors(errors)
```

### Schema-Based Usage
```yaml
sections:
  - id: correction_results
    components:
      - type: sentence_diff
        key: correction_diff
        original_source: "selected_sample.err_sentence"
        corrected_source: "correction_result.corrected"
        mode: "side_by_side"
        original_label: "Original Text"
        corrected_label: "Grammar Corrected"
        visible_when:
          field: correction_result
          operator: not_empty
```

## Integration Guidelines

### Adding to New Pages
1. Import the component in page schema YAML
2. Configure data sources appropriately
3. Set visibility conditions based on data availability
4. Test with sample data to verify rendering

### Data Source Patterns
```yaml
# Session state
original_source: "session_data.original"

# Function results
original_source: "get_original_text()"

# Nested properties
original_source: "result.data.original_text"

# Array indexing
original_source: "samples[0].text"
```

### Performance Considerations
- Component automatically handles large texts with scrolling
- CSS is loaded once per session
- Diff calculation is performed client-side
- Memory usage scales with text length

## Troubleshooting

### Common Issues
- **No diff displayed**: Check data sources and visibility conditions
- **Styling issues**: Verify CSS loading and Streamlit theme compatibility
- **Performance problems**: Consider text length limits for very large inputs

### Debug Information
Enable debug logging to see:
- Data source resolution steps
- Rendering performance metrics
- CSS loading status
- Error conditions and recovery

---

**Version**: 1.0
**Last Updated**: 2025-11-04
**Status**: ✅ Active and production-ready
**Compatibility**: Streamlit 1.28+, Python 3.12+
