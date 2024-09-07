### DynamoDB Implementation Plan

#### 1. Setup and Configuration

- **Python (`dynamodb_interface.py`)**: Wraps `boto3` using `aiobotocore` with Pydantic models for slides and topics.
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
  - Function: `get_items(item_type: Literal['user', 'presentation', 'slide', 'topic', 'source'], identifiers: Union[Dict[str, str], List[Dict[str, str]]], attributes: Optional[List[str]] = None, return_type: Optional[Literal['dict', 'model']] = 'dict') -> Union[Dict, BaseModel, List[Dict], List[BaseModel]]`
    - **Parameters**:
      - `item_type`: Type of the item ('user', 'presentation', 'slide', 'topic', 'source').
      - `identifiers`: Can be a single dictionary or a list of dictionaries containing necessary IDs (user_id, presentation_id, etc.).
      - `attributes`: Optional list of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
      - `return_type`: Determines whether to return a Pydantic model or dictionary ('model' or 'dict'). Can only be 'dict' if the item type is not a Slide or Topic.
    - **Implementation**:
      - **Determine Input Type**: Check if `identifiers` is a single dictionary or a list.
      - **Single Item Retrieval**:
        - If a single set of `identifiers` is provided, construct the primary key (PK and SK) based on `item_type` and `identifiers`.
        - Use `GetItem` to fetch the item.
      - **Multiple Items Retrieval**:
        - If a list of `identifiers` is provided, construct a list of primary keys based on `item_type` and each identifier set.
        - Use `BatchGetItem` to fetch multiple items.
      - **Projection Expression**: If `attributes` are provided, construct a projection expression to fetch only specified attributes.
        - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - **Data Type Support**: Ensure the function handles String, Number, Boolean, List, and Map.
      - **Output Handling**:
        - Convert the response to the specified format (dict or model) based on `return_type`.
        - If only one item is requested, return a single dict or model.
        - If multiple items are requested, return a list of dicts or models.
        - If `item_type` is 'slide' or 'topic', and `return_type` is 'model', return a Pydantic model:
          - Use `.partial()` if attributes are provided, otherwise return a full model.
          - Use `.construct()` to create instances of the model without validation.

```python
if isinstance(identifiers, dict):  # Single item request
    item = get_single_item_from_dynamo()  # Fetch the single item from DynamoDB
    if item_type == 'slide':
        model_cls = Slide.partial() if attributes else Slide
        return model_cls.construct(**item)
    elif item_type == 'topic':
        model_cls = Topic.partial() if attributes else Topic
        return model_cls.construct(**item)
    else:
        return item
else:  # Multiple items request
    items = get_multiple_items_from_dynamo()  # Fetch multiple items from DynamoDB
    if item_type == 'slide':
        model_cls = Slide.partial() if attributes else Slide
        return [model_cls.construct(**item) for item in items]
    elif item_type == 'topic':
        model_cls = Topic.partial() if attributes else Topic
        return [model_cls.construct(**item) for item in items]
    else:
        return items
```

- **TypeScript**:
  - Function: `getItems(itemType: 'user' | 'presentation' | 'slide' | 'topic' | 'source', identifiers: Record<string, string> | Record<string, string>[], attributes?: string[]): Promise<any | any[]>`
    - **Parameters**:
      - `itemType`: Type of the item ('user', 'presentation', etc.).
      - `identifiers`: Can be a single object or an array of objects containing necessary IDs (userID, presentationID, etc.).
      - `attributes`: Optional array of strings specifying which attributes to fetch.
    - **Implementation**:
      - **Determine Input Type**: Check if `identifiers` is a single object or an array.
      - **Single Item Retrieval**:
        - If a single set of `identifiers` is provided, construct the primary key (PK and SK).
        - Use `GetItemCommand` to fetch the item.
      - **Multiple Items Retrieval**:
        - If an array of `identifiers` is provided, construct a list of primary keys and use `BatchGetItemCommand`.
      - **Projection Expression**: If `attributes` are provided, construct a projection expression.
      - **Output Handling**: Return a single item or an array based on the input.
        - If a single item is requested, return only that item.
        - If multiple items are requested, return the array.

```typescript
if (!Array.isArray(identifiers)) {  // Single item request
    const item = await getSingleItemFromDynamo();  // Fetch the single item
    return item;
} else {  // Multiple items request
    const items = await getMultipleItemsFromDynamo();  // Fetch multiple items
    return items;
}
```

### 3.2. Update/Create Item(s)

- **Python**:
  - Function: `update_items(item_type: Literal['user', 'presentation', 'slide', 'topic', 'source'], items: Union[List[Dict], List[BaseModel]]) -> None`
    - **Parameters**:
      - `item_type`: Type of the item (`'user'`, `'presentation'`, `'slide'`, `'topic'`, `'source'`).
      - `items`: List of dictionaries or Pydantic models, depending on the item type. For 'slides' and 'topics', models or dicts are supported; for others, only dicts.
    - **Implementation**:
      - Convert Pydantic models to dictionaries if models are provided.
      - Construct the primary key (PK and SK) based on `item_type` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `UpdateItem` for a single item.
      - Use `TransactWriteItems` for multiple items.
      - Update `last_updated` and `GSI1SK` attributes for Presentations, Slides, Topics, and Sources.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List`, and `Map` (Dict).

- **TypeScript**:
  - Function: `updateItems(itemType: 'user' | 'presentation' | 'slide' | 'topic' | 'source', items: Slide[] | Topic[] | Source[] | Presentation[] | any[]): Promise<void>`
    - **Parameters**:
      - `itemType`: Type of the item (`'user'`, `'presentation'`, `'slide'`, `'topic'`, `'source'`).
      - `items`: Array of objects, each containing the necessary IDs and attributes to update/create.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `itemType` and `identifiers`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - Use `UpdateItemCommand` for a single item.
      - Use `TransactWriteItemsCommand` for multiple items.
      - Update `last_updated` and `GSI1SK` attributes for Presentations, Slides, Topics, and Sources.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object).

### 3.3. Delete Item(s)

- **Python**:
  - Function: `delete_items(item_type: Literal['user', 'presentation', 'slide', 'topic', 'source'], identifiers: List[Dict[str, str]]) -> None`
    - **Parameters**:
      - `item_type`: Type of the item (`'user'`, `'presentation'`, `'slide'`, `'topic'`, `'source'`).
      - `identifiers`: List of dictionaries containing necessary IDs for items to delete.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `item_type` and `identifiers`.
      - Use `DeleteItem` for a single ID.
      - Use `TransactWriteItems` for multiple IDs.

- **TypeScript**:
  - Function: `deleteItems(itemType: 'user' | 'presentation' | 'slide' | 'topic' | 'source', identifiers: Record<string, string>[]): Promise<void>`
    - **Parameters**:
      - `itemType`: Type of the item (`'user'`, `'presentation'`, `'slide'`, `'topic'`, `'source'`).
      - `identifiers`: Array of objects containing necessary IDs for items to delete.
    - **Implementation**:
      - Construct the primary key (PK and SK) based on `itemType` and `identifiers`.
      - Use `DeleteItemCommand` for a single ID.
      - Use `TransactWriteItemsCommand` for multiple IDs.

### 3.4. Get All Items for a Presentation

- **Python**:
  - Function: `get_all_items_for_presentation(user_id: str, presentation_id: str, item_type: Literal['slide', 'topic', 'source'], attributes: Optional[List[str]] = None, return_type: Optional[Literal['model'|'dict']] = 'dict') -> Union[List[Dict], List[BaseModel]]`
    - **Parameters**:
      - `user_id`: User ID.
      - `presentation_id`: Presentation ID.
      - `item_type`: Type of the items to fetch (`'slide'`, `'topic'`, `'source'`).
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
        - Convert the response to the specified format (`dict` or `model`) based on the `return_type` parameter.
        - If `item_type` is `slide` or `topic`, and `return_type` is `model`, return a Pydantic model:
          - If `attributes` are provided, use `.partial()` to return a partial model.
            - Ex. `PartialTopic = Topic.partial()`
          - If `attributes` are not provided, return a full model.
          - Always use the .construct() method to create an instance of the model without validation
        ```python
        if item_type == 'slide':
            model_cls = Slide.partial() if attributes else Slide
            return [model_cls.construct(**item) for item in items]
        elif item_type == 'topic':
            model_cls = Topic.partial() if attributes else Topic
            return [model_cls.construct(**item) for item in items]
        ```

- **TypeScript**:
  - Function: `getAllItemsForPresentation(userID: string, presentationID: string, itemType: 'slide' | 'topic' | 'source', attributes?: string[]): Promise<Slide[] | Topic[] | Source[] | Presentation[]>`
    - **Parameters**:
      - `userID`: User ID.
      - `presentationID`: Presentation ID.
      - `itemType`: Type of the items to fetch (`'slide'`, `'topic'`, `'source'`).
      - `attributes`: Optional array of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
    - **Implementation**:
      - Use `QueryCommand` to fetch all items under a given `userID` and `presentationID`.
      - Ensure eager loading by fetching all items in one call.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
    - **Data Type Support**:
      - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).

### 3.5. Delete All Items for a Presentation

- **Python**:
  - Function: `delete_all_items_for_presentation(user_id: str, presentation_id: str, item_type: Literal['slide', 'topic', 'source']) -> None`
    - **Parameters**:
      - `user_id`: User ID.
      - `presentation_id`: Presentation ID.
      - `item_type`: Type of the items to delete (`'slide'`, `'topic'`, `'source'`).
    - **Implementation**:
      - Use `Query` to get primary keys.
      - Use `TransactWriteItems` with Delete action.

- **TypeScript**:
  - Function: `deleteAllItemsForPresentation(userID: string, presentationID: string, itemType: 'slide' | 'topic' | 'source'): Promise<void>`
    - **Parameters**:
      - `userID`: User ID.
      - `presentationID`: Presentation ID.
      - `itemType`: Type of the items to delete (`'slide'`, `'topic'`, `'source'`).
    - **Implementation**:
      - Use `QueryCommand` to get primary keys.
      - Use `TransactWriteItemsCommand` with Delete action.

### 3.6. Get All Presentation Items for a User

- **Python**:
  - Function: `get_all_presentations_for_user(user_id: str, attributes: Optional[List[str]] = None -> List[Dict]`
    - **Parameters**:
      - `user_id`: User ID.
      - `attributes`: Optional list of strings specifying which attributes to fetch. If not provided, all attributes will be returned.
    - **Implementation**:
      - Use `Query` with GSI to fetch items sorted by `LastUpdate`.
      - Use `ExpressionAttributeNames` for all attribute names to handle reserved words.
      - If `attributes` are provided, construct a projection expression to fetch only specified attributes.
      - **Data Type Support**:
        - Ensure the function handles `String`, `Number`, `Boolean`, `List` (Array), and `Map` (Object/Dict).


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
- Additional tests for verifying partial models (for slides and topics) when attributes are specified.
- Ensure that `Pydantic.construct()` correctly handles partial models with missing attributes and full models when no attributes are specified.

#### 6. Documentation

- Document each function with input parameters, expected output, and examples.
- Include setup instructions for AWS credentials and environment configuration.
- Provide specific documentation on handling Pydantic models for `Slide` and `Topic` types in Python, especially on the behavior of `Pydantic.construct()` and partial model creation.
