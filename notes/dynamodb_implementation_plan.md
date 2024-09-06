### DynamoDB Implementation Plan

#### 1. Setup and Configuration

- **Python (`dynamodb_interface.py`)**: Wraps `boto3` using `aiobotocore`.
- **TypeScript (`dynamodb.ts_interface`)**: Wraps `@aws-sdk/client-dynamodb` (SDK v3).

#### 2. DynamoDB Schema and Key Construction

**Primary Key (PK) and Sort Key (SK):**

- **Partition Key (PK):** `String`
- **Sort Key (SK):** `String`

**Global Secondary Index (GSI1):**

- **Partition Key (GSI1PK):** Same as PK
- **Sort Key (GSI1SK):** `String`

**Item Types and Key Formation:**

1. **User (Profile)**
   - **PK:** `USER#{user_id}`
   - **SK:** `PROFILE`

2. **Presentations**
   - **PK:** `USER#{user_id}`
   - **SK:** `PRESENTATION#{presentation_id}`
   - **GSI1SK:** `LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}`

3. **Slides**
   - **PK:** `USER#{user_id}`
   - **SK:** `PRESENTATION#{presentation_id}#SLIDE#{slide_id}`
   - **GSI1SK:** `LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}`

4. **Topics**
   - **PK:** `USER#{user_id}`
   - **SK:** `PRESENTATION#{presentation_id}#TOPIC#{topic_id}`
   - **GSI1SK:** `LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}`

5. **Sources**
   - **PK:** `USER#{user_id}`
   - **SK:** `PRESENTATION#{presentation_id}#SOURCE#{source_id}`
   - **GSI1SK:** `LASTUPDATE#{timestamp}#PRESENTATION#{presentation_id}`

**Updating GSI1SK Attribute:**

When creating or updating any item (Presentation, Slide, Topic, or Source):

1. **Set the `last_updated` attribute** to the current timestamp.
2. **Set the `GSI1SK` attribute** as follows:
   - `GSI1SK = LASTUPDATE#{current_timestamp}#PRESENTATION#{presentation_id}`
   - For **Slides**, **Topics**, and **Sources**, use the `presentation_id` of the presentation they belong to.
3. **Note:** For the **User (Profile)** item type, the `GSI1SK` does not need to be updated.

#### 3. Function Implementations

### 3.1. Get Item(s)

- **Python**:
  - Function: `get_items(item_type: str, identifiers: Union[Dict[str, str], List[Dict[str, str]]], attributes: Optional[List[str]] = None, return_type: Optional[str] = 'dict') -> Union[List[Dict], List[BaseModel]]`
    - **Parameters**:
      - `item_type`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `identifiers`: Can be a single dictionary or a list of dictionaries containing necessary IDs (`user_id`, `presentation_id`, `slide_id`, `topic_id`, `source_id`).
      - `attributes`: Optional list of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
      - `return_type`: Determines whether to return a Pydantic Model or dictionary ('model' or 'dict').
    - **Implementation**:
      - **Determine Input Type**: Check if `identifiers` is a single dictionary or a list.
      - **Single Item Retrieval**:
        - Construct the primary key (PK and SK) based on `item_type` and `identifiers` if a single set of identifiers is provided.
        - Use `GetItem` to fetch a single item.
      - **Multiple Items Retrieval**:
        - Construct a list of primary keys based on `item_type` and each identifier set in `identifiers` if a list is provided.
        - Use `BatchGetItem` to fetch multiple items.
      - **Projection Expression**: If `attributes` are provided, construct a projection expression to fetch only specified attributes.
      - **Data Type Support**: Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).
      - **Output Handling**:
        - Convert the response to the specified format (`dict` or `model`) based on the `return_type` parameter.
        - Return a list of results, whether it's a list of dicts, a list of models, or a list of partial models.

- **TypeScript**:
  - Function: `getItems(itemType: string, identifiers: Record<string, string> | Record<string, string>[], attributes?: string[]): Promise<any[]>`
    - **Parameters**:
      - `itemType`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `identifiers`: Can be a single object or an array of objects containing necessary IDs (`userID`, `presentationID`, `slideID`, `topicID`, `sourceID`).
      - `attributes`: Optional array of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
    - **Implementation**:
      - **Determine Input Type**: Check if `identifiers` is a single object or an array.
      - **Single Item Retrieval**:
        - Construct the primary key (PK and SK) based on `itemType` and `identifiers` if a single set of identifiers is provided.
        - Use `GetItemCommand` to fetch a single item.
      - **Multiple Items Retrieval**:
        - Construct a list of primary keys based on `itemType` and each identifier set in `identifiers` if an array is provided.
        - Use `BatchGetItemCommand` to fetch multiple items.
      - **Projection Expression**: If `attributes` are provided, construct a projection expression to fetch only specified attributes.
      - **Data Type Support**: Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).
      - **Output Handling**: Return a list of items, handling data conversion based on the `itemType` and fetched attributes.


**3.2. Update/Create Item(s)**

- **Python**:
  - Function: `update_items(item_type: str, items: Union[List[Dict], List[BaseModel]]) -> None`
    - **Parameters**:
      - `item_type`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `items`: List of dictionaries or Pydantic models, depending on the item type. For 'slides' and 'topics', models or dicts are supported; for others, only dicts.
    - **Implementation**:
      - Convert Pydantic models to dictionaries if models are provided.
      - Construct the primary key (PK and SK) based on `item_type` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `UpdateItem` for a single item.
      - Use `TransactWriteItems` for multiple items.
      - Update `last_updated` and `GSI1SK` attributes for Presentations, Slides, Topics, and Sources.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

- **TypeScript**:
  - Function: `updateItems(itemType: string, items: Slide[] | Topic[] | Source[] | Presentation[] | any[]): Promise<void>`
    - **Parameters**:
      - `itemType`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `items`: Array of objects, each containing the necessary IDs and attributes to update/create.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `itemType` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `UpdateItemCommand` for a single item.
      - Use `TransactWriteItemsCommand` for multiple items.
      - Update `last_updated` and `GSI1SK` attributes for Presentations, Slides, Topics, and Sources.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

**3.3. Delete Item(s)**

- **Python**:
  - Function: `delete_items(item_type: str, identifiers: List[Dict[str, str]]) -> None`
    - **Parameters**:
      - `item_type`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `identifiers`: List of dictionaries containing necessary IDs for items to delete.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `item_type` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `DeleteItem` for a single ID.
      - Use `TransactWriteItems` for multiple IDs.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

- **TypeScript**:
  - Function: `deleteItems(itemType: string, identifiers: Record<string, string>[]): Promise<void>`
    - **Parameters**:
      - `itemType`: Type of the item (e.g., 'user', 'presentation', 'slide', 'topic', 'source').
      - `identifiers`: Array of objects containing necessary IDs for items to delete.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `itemType` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `DeleteItemCommand` for a single ID.
      - Use `TransactWriteItemsCommand` for multiple IDs.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

**3.4. Get All Items for a Presentation**

- **Python**:
  - Function: `get_all_items_for_presentation(user_id: str, presentation_id: str, item_type: str, attributes: Optional[List[str]] = None, return_type: Optional[str] = 'dict') -> Union[List[Dict], List[BaseModel]]`
    - **Parameters**:
      - `user_id`: User ID.
      - `presentation_id`: Presentation ID.
      - `item_type`: Type of the items to fetch (e.g., 'slide', 'topic', 'source').
      - `attributes`: Optional list of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
      - `return_type`: If 'slides' or 'topic', this parameter determines whether to return a Pydantic Model or dictionary ('model' or 'dict').
    - **Implementation**:
      - Use `Query` to fetch all items under a given `user_id` and `presentation_id`.
      - Ensure eager loading by fetching all items in one call.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
      - **Data Type Support**:
        - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).
      - **Output Handling**:
        - If `item_type` is 'slide' or 'topic', return a Pydantic model or dictionary based on `return_type` parameter.
        - If attributes are specified and `return_type` is 'model', return a Partial Model.

- **TypeScript**:
  - Function: `getAllItemsForPresentation(userID: string, presentationID: string, itemType: string, attributes?: string[]): Promise<Slide[] | Topic[] | Source[] | Presentation[]>`
    - **Parameters**:
      - `userID`: User ID.
      - `presentationID`: Presentation ID.
      - `itemType`: Type of the items to fetch (e.g., 'slide', 'topic', 'source').
      - `attributes`: Optional array of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
    - **Implementation**:
      - Use `QueryCommand` to fetch all items under a given `userID` and `presentationID`.
      - Ensure eager loading by fetching all items in one call.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

**3.5. Delete All Items for a Presentation**

- **Python**:
  - Function: `delete_all_items_for_presentation(user_id: str, presentation_id: str, item_type: str) -> None`
    - **Parameters**:
      - `user_id`: User ID.
      - `presentation_id`: Presentation ID.
      - `item_type`: Type of the items to delete (e.g., 'slide', 'topic', 'source').
    - **Implementation**:
      - Use `Query` to get primary keys.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `TransactWriteItems` with Delete action.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

- **TypeScript**:
  - Function: `deleteAllItemsForPresentation(userID: string, presentationID: string, itemType: string): Promise<void>`
    - **Parameters**:
      - `userID`: User ID.
      - `presentationID`: Presentation ID.
      - `itemType`: Type of the items to delete (e.g., 'slide', 'topic', 'source').
    - **Implementation**:
      - Use `QueryCommand` to get primary keys.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `TransactWriteItemsCommand` with Delete action.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

**3.6. Get All Presentation Items for a User**

- **Python**:
  - Function: `get_all_presentations_for_user(user_id: str, attributes: Optional[List[str]] = None, return_type: Optional[str] = 'dict') -> Union[List[Dict], List[BaseModel]]`
    - **Parameters**:
      - `user_id`: User ID.
      - `attributes`: Optional list of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
      - `return_type`: If 'slides' or 'topic', this parameter determines whether to return a Pydantic Model or dictionary ('model' or 'dict').
    - **Implementation**:
      - Use `Query` with GSI to fetch items sorted by `LastUpdate`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
      - **Data Type Support**:
        - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).
      - **Output Handling**:
        - If `item_type` is 'slide' or 'topic', return a Pydantic model or dictionary based on `return_type` parameter.
        - If attributes are specified and `return_type` is 'model', return a Partial Model.

- **TypeScript**:
  - Function: `getAllPresentationsForUser(userID: string, attributes?: string[]): Promise<Presentation[]>`
    - **Parameters**:
      - `userID`: User ID.
      - `attributes`: Optional array of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
    - **Implementation**:
      - Use `QueryCommand` with GSI to fetch items sorted by `LastUpdate`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

#### 4. Side Panel Read Operation

To retrieve the list of presentations for the side panel, sorted by the most recent update:

1. **Query GSI1** with:
   - **Partition Key (PK):** `USER#{user_id}`
   - **Sort Key (GSI1SK) begins_with:** `LASTUPDATE#`
   - Limit the query to 25 items.
   - Sort in descending order.

2. For each item returned from step 1, extract the `presentation_id` from the `GSI1SK` attribute.

3. Perform a batch get operation on the main table to retrieve the full presentation items using the extracted `presentation_ids`.

#### 5. Testing and Validation

- Write unit tests for each function to ensure they handle all data types (`String`, `Number`, `Boolean`, `List`, `Map`) and reserved words correctly.
- Test edge cases, such as empty inputs, non-existent IDs, and different return types (dict vs. model) in Python.

#### 6. Documentation

- Document each function with input parameters, expected output, and examples.
- Include setup instructions for AWS credentials and environment configuration.
- Provide specific examples of using models and partial models in Python.

#### 7. Deployment

- Ensure both Python and TypeScript code are integrated into their respective environments (backend and frontend).
- Deploy and test in a staging environment before moving to production.

This comprehensive plan ensures proper key formation, consistent handling of reserved words, flexible attribute fetching, dynamic typing in Python, and efficient use of DynamoDB's capabilities for managing hierarchical and time-sorted data.
