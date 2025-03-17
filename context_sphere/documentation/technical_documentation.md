# Technical Documentation: Preprocessing Pipeline

[← Back to Overview](PreProcessing_Documentation.md) | [Theoretical Alignment →](theoretical_alignment.md) | [Implementation Analysis →](implementation_analysis.md)

## Table of Contents
- [Data Transformation Workflow](#data-transformation-workflow)
  - [Initial Data Loading](#initial-data-loading)
  - [Intermediate Storage](#intermediate-storage)
  - [Thread Structure Building](#thread-structure-building)
  - [Context Sphere Creation](#context-sphere-creation)
- [Context Sphere Structure](#context-sphere-structure)
  - [Content Selection Principles](#content-selection-principles)
  - [Format Structure](#format-structure)
- [Implementation Considerations](#implementation-considerations)
  - [Data Quality](#data-quality)
  - [Performance Optimization](#performance-optimization)
  - [Validation Strategy](#validation-strategy)

---

## Data Transformation Workflow

### Initial Data Loading

> **Purpose**: Transform raw CSV data into a structured format while ensuring data quality

#### Implementation
```python
class DataPreprocessor:
    def process(self):
        """Process the data by loading it from CSV and applying preprocessing steps."""
        self.df = pd.read_csv(self.file_path)
        self._convert_dates()
        self._handle_missing_values()
        self._convert_id_columns()
        self._create_new_features()
```

#### Key Design Decisions
- **Missing Value Handling**:
  - `'No Headline'` for empty headlines
  - `'No Comment'` for empty comments
  - `'Unknown'` for missing metadata
  - *Rationale*: Provides clear context rather than ambiguous empty values

- **Date Standardization**:
  - ISO format conversion
  - Consistent temporal representation
  - *Rationale*: Ensures consistent temporal context representation

### Intermediate Storage

> **Purpose**: Provide efficient intermediate storage for preprocessed data

#### Implementation
- Serializes preprocessed DataFrame to pickle format
- Maintains data structure and types integrity

#### Key Design Decisions
- **Pickle Format Selection**:
  ```python
  def save_preprocessed_data(self, output_path: str):
      with open(output_path, 'wb') as f:
          pickle.dump(self.df, f)
  ```
  - *Rationale*: Preserves Python object structures efficiently
  - *Validation*: Automated checks between CSV and pickle

### Thread Structure Building

> **Purpose**: Create hierarchical representation of comment threads through a three-phase process

#### Phase 1: JSON Structure Creation
```python
def build_comment_thread(self, comments: pd.DataFrame, parent_id: int) -> List[Dict]:
    """Build complete hierarchical structure of comments and replies"""
    replies = comments[comments['ID_Posting_Parent'] == parent_id]
    return [{
        'id': int(reply['ID_Posting']),
        'parent_id': int(reply['ID_Posting_Parent']),
        'user_id': int(reply['ID_CommunityIdentity']),
        'user_name': reply['UserCommunityName'],
        'user_gender': reply['UserGender'],
        # ... all other metadata 
        'replies': self.build_comment_thread(comments, int(reply['ID_Posting']))
    } for _, reply in replies.iterrows()]
```
- *Rationale*: Creates complete thread structure with all metadata for flexibility in later processing

#### Phase 2: User-Specific Thread Filtering
```python
def user_in_comment_or_replies(comment, user_id):
    """Check for user presence in comment thread"""
    if comment['user_id'] == user_id:
        return True
    for reply in comment.get('replies', []):
        if user_in_comment_or_replies(reply, user_id):
            return True
    return False

def filter_comments_by_user(comments, user_id, level=0):
    """Filter threads to preserve user context"""
    filtered_comments = []
    for comment in comments:
        if user_in_comment_or_replies(comment, user_id):
            new_comment = {
                "user_name": comment['user_name'],
                "comment_headline": comment['comment_headline'],
                "comment_text": comment['comment_text'],
                "comment_created_at": comment['comment_created_at'],
                "replies": filter_comments_by_user(comment.get('replies', []), user_id, level + 1)
            }
            filtered_comments.append(new_comment)
    return filtered_comments
```
- *Rationale*: Preserves conversation context while reducing data to user-relevant threads

#### Phase 3: Markdown Generation
```python
def generate_comment_markdown(comments, level=0):
    """Generate human-readable format"""
    markdown = ""
    indent = "  " * level
    for comment in comments:
        markdown += f"{indent}> *Headline*: {comment.get('comment_headline', 'Empty Heading')}\n"
        markdown += f"{indent}{comment['user_name']} schreibt:\n"
        markdown += f"{indent}> {comment['comment_text']}\n"
        markdown += f"{indent}> Erstellt am {format_date(comment['comment_created_at'])}\n\n"
        if comment.get('replies'):
            markdown += generate_comment_markdown(comment['replies'], level + 1)
    return markdown
```
- *Rationale*: Creates human and LLM-readable format with preserved thread structure

### Token Management

> **Purpose**: Ensure efficient token usage while maintaining context quality

#### Implementation
```python
def count_tokens(text):
    """Token counting using cl100k_base encoding"""
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    return len(tokens)
```

#### Configuration
```json
{
    "MIN_TOKEN_COUNT": 5000,
    "MAX_TOKEN_COUNT": 15000,
    "SAMPLE_SIZE": 20
}
```

#### Sampling Strategy
- Token range: 5,000-15,000 tokens per context sphere
- Sample size: 20 files for analysis
- Selection criteria:
  ```python
  if min_token_count <= token_count <= max_token_count:
      eligible_files.append(user_id)
  ```

#### Metadata Tracking
```python
def create_metadata_file(user_id, user_name, user_gender, user_created_at, total_tokens, comments_extracted):
    """Track user context metrics"""
    metadata = {
        "user_id": int(user_id),
        "user_name": user_name,
        "user_gender": user_gender,
        "user_created_at": user_created_at,
        "total_tokens": int(total_tokens),
        "comments_extracted": int(comments_count)
    }
```

#### Key Benefits
- Efficient context preservation
- Structured thread representation
- Token-aware sampling
- Metadata tracking for analysis

## Context Sphere Structure

### Content Selection Principles

#### Included Elements
| Category | Elements | Rationale |
|----------|----------|-----------|
| User Metadata | Name, creation date, gender | Provides user context baseline |
| Article Context | Title, date, channel, ressort | Establishes discussion context |
| Comment Content | Text, headlines, timestamps | Captures user expression |
| Thread Structure | Parent-child relationships | Preserves conversation flow |

#### Excluded Elements
- Technical IDs (except for reference)
- Millisecond precision timestamps
- System metadata

> *Rationale*: Avoid noise in emotional context analysis

### Format Structure

#### Hierarchy
1. **User Overview**
   - Basic user information
   - Account context

2. **Article Sections**
   - Article metadata
   - Discussion context

3. **Comment Threads**
   - Hierarchical structure
   - Temporal progression
   - Interaction context


## Dataset Statistics

### Token Distribution Analysis

> **Purpose**: Provide insights into the distribution of tokens across the dataset to justify sampling decisions and demonstrate dataset characteristics.

#### Overall Token Distribution
![Distribution of Total Tokens with Outliers](images/Oktober/distribution_with_outliers.png)
*Figure 1: Distribution of total tokens including outliers, showing the full range of context sphere sizes*

#### Cleaned Token Distribution
![Distribution of Total Tokens without Outliers](images/Oktober/token_distribution_without_outliers.png)
*Figure 2: Distribution of total tokens excluding outliers, providing a clearer view of typical context sphere sizes*

#### Token Range Analysis
![Percentage of Files by Token Range](images/Oktober/token_range_percentage.png)
*Figure 3: Percentage distribution of files across token ranges, showing the concentration of context spheres by size*

#### Key Observations
- Majority of context spheres (>40%) contain 0-1000 tokens
- Significant drop in frequency above 2000 tokens
- Long tail distribution extending to 350,000 tokens
- Median token count: ~33,000 tokens

#### Implications for Sampling
- Selected range (5,000-15,000 tokens) represents a balance between:
  - Context richness
  - Processing efficiency
  - Representative sample size
- Excludes extreme outliers while maintaining meaningful context

## Implementation Considerations

### Data Quality
- ✓ UTF-8 encoding throughout pipeline
- ✓ Explicit missing value handling
- ✓ Validation at transformation steps

### Performance Optimization
- ✓ Efficient thread building structures
- ✓ Token-aware formatting
- ✓ Batch processing capability

### Validation Strategy
- ✓ Automated format checks
- ✓ Manual sample verification
- ✓ Cross-transformation validation

---

[↑ Back to Top](#technical-documentation-preprocessing-pipeline)

