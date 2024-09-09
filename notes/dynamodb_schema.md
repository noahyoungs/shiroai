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

## **Side Panel Read Operation (Updated)**

To retrieve the list of presentations for the side panel, sorted by the most recent update:

1. Query GSI1 with:
   - Partition Key (PK) = `USER#{user_id}`
   - Sort Key (SK) begins with `LASTUPDATED#`
   - Limit the query to 25 items
   - Sort in descending order

2. Perform a batch get operation to retrieve the full presentation items based on the `SK` values, which contain the `PRESENTATION#{presentation_id}`.

---

## **Updating GSI1SK**

When creating or updating **presentation** items:

1. Set the `last_updated` attribute to the current timestamp.
2. Set the `GSI1SK` as follows:
   - `GSI1SK = LASTUPDATED#{current_timestamp}`

   **Note**: Do not set the `GSI1SK` for Slides, Topics, or Sources. Only presentations will update the GSI.
