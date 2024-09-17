# Shiro AI DynamoDB Schema

**Primary Key:**
- Partition Key (PK): String
- Sort Key (SK): String

**Global Secondary Index (GSI1):**
- Partition Key: PK
- Sort Key: SK

**Item Types:**

1. **User:**
   - PK: `USER#{user_id}`
   - SK: `PROFILE`

2. **Presentations:**
   - PK: `USER#{user_id}`
   - SK: `PRESENTATION#{presentation_id}`
   - GSI1SK: `LASTUPDATED#{timestamp}`

3. **Slides:**
   - PK: `USER#{user_id}`
   - SK: `PRESENTATION#{presentation_id}#SLIDE#{slide_id}`
   - **No GSI1SK** for slides.

4. **Topics:**
   - PK: `USER#{user_id}`
   - SK: `PRESENTATION#{presentation_id}#TOPIC#{topic_id}`
   - **No GSI1SK** for topics.

5. **Sources:**
   - PK: `USER#{user_id}`
   - SK: `PRESENTATION#{presentation_id}#SOURCE#{source_id}`
   - **No GSI1SK** for sources.

**Additional Attributes:**
- `last_updated`: Number (timestamp)
- `topic`: String (for presentations, to be displayed in the side panel)
- (Other attributes as needed for each item type)

---

## **Side Panel Read Operation**

To retrieve the list of presentations for the side panel, sorted by the most recent update:

1. Query GSI1 with:
   - Partition Key (PK) = `USER#{user_id}`
   - Sort Key (SK) begins with `PRESENTATION#`
   - Limit the query to N items (e.g., 25)
   - Sort in descending order by GSI1SK (set `ScanIndexForward` to false)

2. This query will directly return the presentation items with their `topic` attribute and `presentation_id` (extracted from the SK), sorted by the most recent update.

3. For pagination or loading more items:
   - Use the `ExclusiveStartKey` parameter with the last evaluated key from the previous query.
   - This allows retrieving the next N items after a given PK and SK combination, still sorted by GSI1SK.
   - Example: To get the next 25 items after a specific presentation, use its PK, SK, and GSI1SK as the `ExclusiveStartKey`.

Note: This pagination approach works efficiently because only presentation items have the GSI1SK attribute, which contains the `LASTUPDATED#` timestamp used for sorting.

---

## **Updating GSI1SK**

When creating or updating **presentation** items:

1. Set the `last_updated` attribute to the current timestamp.
2. Set the `GSI1SK` as follows:
   - `GSI1SK = LASTUPDATED#{current_timestamp}`

   **Note**: Only presentation items have the `GSI1SK` attribute. Slides, Topics, and Sources do not use the GSI.
