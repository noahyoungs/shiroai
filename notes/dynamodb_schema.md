# Shiro AI DynamoDB Schema

Primary Key:
 - Partition Key (PK): String
 - Sort Key (SK): String

Global Secondary Index (GSI1):
 - Partition Key: PK
 - Sort Key: GSI1SK: String

Item Types:
 1. User:
    • PK: USER#{user_id}
    • SK: PROFILE

 2. Presentations:
    • PK: USER#{user_id}
    • SK: PRESENTATION#{presentation_id}
    • GSI1SK: LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}

 3. Slides:
    • PK: USER#{user_id}
    • SK: PRESENTATION#{presentation_id}#SLIDE#{slide_id}
    • GSI1SK: LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}

 4. Topics:
    • PK: USER#{user_id}
    • SK: PRESENTATION#{presentation_id}#TOPIC#{topic_id}
    • GSI1SK: LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}

 5. Sources:
    • PK: USER#{user_id}
    • SK: PRESENTATION#{presentation_id}#SOURCE#{source_id}
    • GSI1SK: LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}

Additional Attributes:
 - last_updated: Number (timestamp)
 - (Other attributes as needed for each item type)

Side Panel Read Operation:
To retrieve the list of presentations for the side panel, sorted by most recent update:

1. Query GSI1 with:
   - Partition Key (PK) = USER#{user_id}
   - Sort Key (GSI1SK) begins_with LASTUPDATE#
   - Limit the query to 25 items
   - Sort in descending order

2. For each item returned from step 1, extract the presentation_id from the GSI1SK attribute.

3. Perform a batch get operation on the main table to retrieve the full presentation items using the extracted presentation_ids.

Updating GSI1SK:
When creating or updating any item (Presentation, Slide, Topic, or Source):

1. Set the 'last_updated' attribute to the current timestamp.

2. Set the GSI1SK attribute as follows:
   GSI1SK = LASTUPDATE#{current_timestamp}#PRESENTATION#{presentation_id}

   Note: For Slides, Topics, and Sources, use the presentation_id of the presentation they belong to.

This schema allows for:
1. Storing user profiles with user-specific settings and information.
2. Organizing all presentations and related items (slides, topics, sources) by user.
3. Efficiently querying the most recently updated presentations for a user using GSI1.
4. Maintaining the hierarchy of items within a presentation.

To use this schema:
1. Retrieve user profile: Query with PK = USER#{user_id} and SK = PROFILE
2. Get all items for a user: Query with PK = USER#{user_id}
3. Get a specific presentation and its items: Query with PK = USER#{user_id} and SK begins_with PRESENTATION#{presentation_id}
4. Get recently updated presentations for the side panel: Use the Side Panel Read Operation described above
