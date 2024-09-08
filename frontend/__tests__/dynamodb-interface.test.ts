// frontend/__tests__/dynamodb-interface.test.ts
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { getItems, updateItems, deleteItems, getAllItemsForPresentation, deleteAllItemsForPresentation } from "../src/utils/dynamodb-interface"; // Adjust path as necessary
import { User, Presentation, BaseSlide, Topic, Source } from "../src/utils/database-types"; // Import types
import { uuidv7 } from "uuidv7";

const dynamoDBClient = new DynamoDBClient({});

// Helper function to create dummy data for various item types
const createDummyData = (itemType: string): User | Presentation | BaseSlide | Topic | Source => {
  const user_id = `test_user_${uuidv7()}`;
  const presentation_id = `test_presentation_${uuidv7()}`;

  switch (itemType) {
    case 'user':
      return {
        user_id,
        name: 'Test User',
        email: 'test@example.com',
        created_at: Date.now(),
        foo: [{ bar: 'baz' }, { bar: 'qux' }],
        random: null,
      } as User;
    case 'presentation':
      return {
        user_id,
        presentation_id,
        title: 'Test Presentation',
        created_at: Date.now(),
        status: 'draft',
      } as Presentation;
    case 'slide':
      return {
        user_id,
        presentation_id,
        slide_id: `test_slide_${uuidv7()}`,
        slide_title: 'Test Slide',
        topic_id: `test_topic_${uuidv7()}`,
        slide_content: [
          {
            content: 'Test bullet point',
            icon: { name: 'test_icon', source: 'test_source' },
            slide_id: `bullet_${uuidv7()}`,
          },
        ],
        sequential: true,
        layout: 'list',
      } as BaseSlide;
    case 'topic':
      return {
        user_id,
        presentation_id,
        topic_id: `test_topic_${uuidv7()}`,
        title: 'Test Topic',
        reduced_docs: 'Test reduced docs',
        additional_attributes: { key: 'value' },
      } as Topic;
    case 'source':
      return {
        user_id,
        presentation_id,
        source_id: `test_source_${uuidv7()}`,
        title: 'Test Source',
        url: 'https://example.com',
        content: 'Test content',
        created_at: Date.now(),
      } as Source;
    default:
      throw new Error(`Unknown item type: ${itemType}`);
  }
};

describe('DynamoDB Interface Tests', () => {

  it('should retrieve a user item correctly with all attributes', async () => {
    const userData = createDummyData('user') as User;
    const userDataWithUndefined = { ...userData }; // shallow copy
    userDataWithUndefined.random_two = undefined; // Add an undefined attribute, which should be ignored
    await updateItems('user', [userDataWithUndefined]);

    const result = await getItems('user', { user_id: userData.user_id });
    expect(result).toMatchObject(userData);
    //@ts-ignore
    expect(result?.foo).toEqual([{ bar: 'baz' }, { bar: 'qux' }]);
  });

  it('should retrieve multiple user items with all attributes', async () => {
    const user1 = createDummyData('user') as User;
    const user2 = createDummyData('user') as User;
    await updateItems('user', [user1, user2]);

    const result = await getItems('user', [
      { user_id: user1.user_id },
      { user_id: user2.user_id }
    ]);
    expect(result).toEqual([user1, user2]);
  });

  it('should retrieve specific attributes of a user item', async () => {
    const userData = createDummyData('user') as User;
    await updateItems('user', [userData]);

    const result = await getItems('user', { user_id: userData.user_id }, ['name']);
    expect(result).toHaveProperty('name', 'Test User');
    expect(result).not.toHaveProperty('email'); // Exclude unnecessary attributes
  });

  it('should retrieve a slide item with specific attributes', async () => {
    const slideData = createDummyData('slide') as BaseSlide;
    await updateItems('slide', [slideData]);

    const result = await getItems('slide', {
      user_id: slideData.user_id,
      presentation_id: slideData.presentation_id,
      slide_id: slideData.slide_id,
    }, ['slide_title']);
    
    expect(result).toHaveProperty('slide_title', slideData.slide_title);
    expect(result).not.toHaveProperty('slide_content');
  });

  it('should return null when no item is found', async () => {
    const result = await getItems('user', { user_id: 'nonexistent_user' });
    expect(result).toBeNull();
  });

  it('should handle partial retrieval of models', async () => {
    const topicData = createDummyData('topic') as Topic;
    await updateItems('topic', [topicData]);

    const result = await getItems('topic', {
      user_id: topicData.user_id,
      presentation_id: topicData.presentation_id,
      topic_id: topicData.topic_id,
    }, ['title']);
    
    expect(result).toHaveProperty('title', 'Test Topic');
    expect(result).not.toHaveProperty('reduced_docs'); // Exclude reduced_docs
  });
 
  it('should delete a single item correctly', async () => {
    const userData = createDummyData('user') as User;
    await updateItems('user', [userData]);

    await deleteItems('user', [{ user_id: userData.user_id }]);
    const result = await getItems('user', { user_id: userData.user_id });
    expect(result).toBeNull();
  });

  it('should delete multiple items correctly', async () => {
    const pres1 = createDummyData('presentation') as Presentation;
    const pres2 = createDummyData('presentation') as Presentation;
    await updateItems('presentation', [pres1, pres2]);

    await deleteItems('presentation', [
      { user_id: pres1.user_id, presentation_id: pres1.presentation_id },
      { user_id: pres2.user_id, presentation_id: pres2.presentation_id }
    ]);

    const results = await getItems('presentation', [
      { user_id: pres1.user_id, presentation_id: pres1.presentation_id },
      { user_id: pres2.user_id, presentation_id: pres2.presentation_id }
    ]);
    expect(results).toEqual([null, null]);
  });

  it('should get all items for a presentation', async () => {
    const presData = createDummyData('presentation') as Presentation;
    const slide1 = createDummyData('slide') as BaseSlide;
    const slide2 = createDummyData('slide') as BaseSlide;
    slide1.user_id = slide2.user_id = presData.user_id;
    slide1.presentation_id = slide2.presentation_id = presData.presentation_id;

    await updateItems('presentation', [presData]);
    await updateItems('slide', [slide1, slide2]);

    const results = await getAllItemsForPresentation(presData.user_id, presData.presentation_id, 'slide');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(2);
    expect(results[0]).toHaveProperty('slide_id');
    expect(results[1]).toHaveProperty('slide_id');
  });

  it('should get all items for a presentation with specific attributes', async () => {
    const presData = createDummyData('presentation') as Presentation;
    const slide1 = createDummyData('slide') as BaseSlide;
    const slide2 = createDummyData('slide') as BaseSlide;
    slide1.user_id = slide2.user_id = presData.user_id;
    slide1.presentation_id = slide2.presentation_id = presData.presentation_id;

    await updateItems('presentation', [presData]);
    await updateItems('slide', [slide1, slide2]);

    const results = await getAllItemsForPresentation(presData.user_id, presData.presentation_id, 'slide', ['slide_title']);
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(2);
    expect(results[0]).toHaveProperty('slide_title');
    expect(results[0]).not.toHaveProperty('slide_content');
    expect(results[1]).toHaveProperty('slide_title');
    expect(results[1]).not.toHaveProperty('slide_content');
  });

  it('should delete all items for a presentation', async () => {
    const presData = createDummyData('presentation') as Presentation;
    const slide1 = createDummyData('slide') as BaseSlide;
    const slide2 = createDummyData('slide') as BaseSlide;
    slide1.user_id = slide2.user_id = presData.user_id;
    slide1.presentation_id = slide2.presentation_id = presData.presentation_id;

    await updateItems('presentation', [presData]);
    await updateItems('slide', [slide1, slide2]);

    await deleteAllItemsForPresentation(presData.user_id, presData.presentation_id, 'slide');

    const results = await getAllItemsForPresentation(presData.user_id, presData.presentation_id, 'slide');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  it('should handle empty results when getting all items for a presentation', async () => {
    const presData = createDummyData('presentation') as Presentation;
    await updateItems('presentation', [presData]);

    const results = await getAllItemsForPresentation(presData.user_id, presData.presentation_id, 'slide');
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  it('should handle deletion of non-existent items', async () => {
    const nonExistentUser = { user_id: 'non_existent_user' };
    await expect(deleteItems('user', [nonExistentUser])).resolves.not.toThrow();
  });

  it('should handle getting items with invalid identifiers', async () => {
    await expect(getItems('user', { invalid_key: 'value' } as any)).rejects.toThrow();
  });

});
