# backend/tests/dynamodb_interface_tests.py

import pytest
from uuid_extensions import uuid7str
from dynamodb_interface import (
    get_items, update_items, delete_items, get_all_items_for_presentation,
    delete_all_items_for_presentation
)
from database_models import *

# Helper function to create dummy data
def create_dummy_data(item_type):
    user_id = f"test_user_{uuid7str()}"
    presentation_id = f"test_presentation_{uuid7str()}"
    
    if item_type == 'user':
        return {
            'user_id': user_id,
            'name': 'Test User',
            'email': 'test@example.com',
            'created_at': 1000000000,
            'good': False,
            'foo': [{'bar': 'baz'}, {'bar': 'qux'}],
            'random': None

        }
    elif item_type == 'presentation':
        return {
            'user_id': user_id,
            'presentation_id': presentation_id,
            'title': 'Test Presentation',
            'created_at': 1000000000,
            'status': 'draft',
            'bad': False
        }
    elif item_type == 'slide':
        return ShortBulletsSlide(
            user_id=user_id,
            presentation_id=presentation_id,
            slide_id=f"test_slide_{uuid7str()}",
            slide_title="Test Slide",
            topic_id=f"test_topic_{uuid7str()}",
            slide_content=[
                {
                    "content": "Test bullet point",
                    "icon": IconData(name="test_icon", source="test_source"),
                    "slide_id": f"test_bullet_{uuid7str()}"
                }
            ],
            sequential=True,
            layout="list"
        ).model_dump()
    elif item_type == 'topic':
        return Topic(
            user_id=user_id,
            presentation_id=presentation_id,
            topic_id=f"test_topic_{uuid7str()}",
            title="Test Topic",
            reduced_docs="Test reduced docs",
            additional_attributes={"key": "value"}
        ).model_dump()
    elif item_type == 'source':
        return {
            'user_id': user_id,
            'presentation_id': presentation_id,
            'source_id': f"test_source_{uuid7str()}",
            'title': 'Test Source',
            'url': 'https://example.com',
            'content': 'Test content',
            'created_at': '2023-09-01T12:00:00Z'
        }
    else:
        raise ValueError(f"Unknown item type: {item_type}")

# Test get_items function
@pytest.mark.asyncio
async def test_get_items():
    # Test single item retrieval
    user_data = create_dummy_data('user')
    await update_items('user', [user_data])
    result = await get_items('user', {'user_id': user_data['user_id']})
    assert isinstance(result, dict)
    assert not result.get('good')
    assert result.get('created_at') > 2
    assert result.get('foo') == [{'bar': 'baz'}, {'bar': 'qux'}]
    assert result['name'] == 'Test User'

    # Test multiple items retrieval
    user_data1 = create_dummy_data('user')
    user_data2 = create_dummy_data('user')
    await update_items('user', [user_data1, user_data2])
    result = await get_items('user', [{'user_id': user_data1['user_id']}, {'user_id': user_data2['user_id']}])
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['name'] == 'Test User'
    assert result[1]['name'] == 'Test User'

    # Test with specific attributes
    result = await get_items('user', {'user_id': user_data['user_id']}, attributes=['name'])
    assert isinstance(result, dict)
    assert 'name' in result
    assert 'user_id' in result # identifier should always be included
    assert result.get('user_id') is not None
    assert result.get('last_updated') is None # last update should not be included because its a user
    assert 'email' not in result

    # Test slide with specific attributes
    slide_data = create_dummy_data('slide')
    await update_items('slide', [slide_data])
    result = await get_items('slide', {'user_id': slide_data['user_id'], 'presentation_id': slide_data['presentation_id'], 'slide_id': slide_data['slide_id']}, attributes=['slide_title'])
    assert isinstance(result, dict)
    assert result.get('slide_title') == "Test Slide"
    assert result.get('slide_id') == slide_data['slide_id'] # identifier should always be included
    assert result.get('last_updated') is not None  # last update should be included because its not a user
    assert result.get('slide_content') is None # slide content should not be included


    # Test with model return type
    slide_data = create_dummy_data('slide')
    await update_items('slide', [slide_data])
    result = await get_items('slide', {'user_id': slide_data['user_id'], 'presentation_id': slide_data['presentation_id'], 'slide_id': slide_data['slide_id']}, return_type='model')
    assert isinstance(result, ShortBulletsSlide)

    # Test with partial model
    topic_data = create_dummy_data('topic')
    await update_items('topic', [topic_data])
    result = await get_items('topic', {'user_id': topic_data['user_id'], 'presentation_id': topic_data['presentation_id'], 'topic_id': topic_data['topic_id']}, attributes=['title'], return_type='model')
    PartialTopic = Topic.partial()
    assert result.__class__.__name__ == PartialTopic.__name__
    assert hasattr(result, 'title')
    assert not result.reduced_docs

# Test update_items function
@pytest.mark.asyncio
async def test_update_items():
    # Test single item update
    user_data = create_dummy_data('user')
    await update_items('user', [user_data])
    result = await get_items('user', {'user_id': user_data['user_id']})
    assert result['name'] == 'Test User'

    # Test multiple items update
    pres_data1 = create_dummy_data('presentation')
    pres_data2 = create_dummy_data('presentation')
    await update_items('presentation', [pres_data1, pres_data2])
    result = await get_items('presentation', [{'user_id': pres_data1['user_id'], 'presentation_id': pres_data1['presentation_id']},
                                              {'user_id': pres_data2['user_id'], 'presentation_id': pres_data2['presentation_id']}])
    assert len(result) == 2
    assert result[0]['title'] == 'Test Presentation'
    assert result[1]['title'] == 'Test Presentation'

    # Test update with Pydantic model
    slide_data = create_dummy_data('slide')
    slide_model = ShortBulletsSlide(**slide_data)
    await update_items('slide', [slide_model])
    result = await get_items('slide', {'user_id': slide_data['user_id'], 'presentation_id': slide_data['presentation_id'], 'slide_id': slide_data['slide_id']})
    assert result['slide_title'] == "Test Slide"

# Test delete_items function
@pytest.mark.asyncio
async def test_delete_items():
    # Test single item deletion
    user_data = create_dummy_data('user')
    await update_items('user', [user_data])
    await delete_items('user', [{'user_id': user_data['user_id']}])
    result = await get_items('user', {'user_id': user_data['user_id']})
    assert result is None

    # Test multiple items deletion
    pres_data1 = create_dummy_data('presentation')
    pres_data2 = create_dummy_data('presentation')
    await update_items('presentation', [pres_data1, pres_data2])
    await delete_items('presentation', [{'user_id': pres_data1['user_id'], 'presentation_id': pres_data1['presentation_id']},
                                        {'user_id': pres_data2['user_id'], 'presentation_id': pres_data2['presentation_id']}])
    result = await get_items('presentation', [{'user_id': pres_data1['user_id'], 'presentation_id': pres_data1['presentation_id']},
                                              {'user_id': pres_data2['user_id'], 'presentation_id': pres_data2['presentation_id']}])
    assert result == [None, None]

# Test get_all_items_for_presentation function
@pytest.mark.asyncio
async def test_get_all_items_for_presentation():
    pres_data = create_dummy_data('presentation')
    slide_data1 = create_dummy_data('slide')
    slide_data2 = create_dummy_data('slide')
    slide_data1['user_id'] = slide_data2['user_id'] = pres_data['user_id']
    slide_data1['presentation_id'] = slide_data2['presentation_id'] = pres_data['presentation_id']
    
    await update_items('presentation', [pres_data])
    await update_items('slide', [slide_data1, slide_data2])
    
    result = await get_all_items_for_presentation(pres_data['user_id'], pres_data['presentation_id'], 'slide')
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, dict) for item in result)

    # Test with model return type
    result = await get_all_items_for_presentation(pres_data['user_id'], pres_data['presentation_id'], 'slide', return_type='model')
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, ShortBulletsSlide) for item in result)

    # Test with specific attributes
    result = await get_all_items_for_presentation(pres_data['user_id'], pres_data['presentation_id'], 'slide', attributes=['slide_title'])
    assert isinstance(result, list)
    assert len(result) == 2
    assert all('slide_title' in item for item in result)
    assert all('slide_content' not in item for item in result)

# Test delete_all_items_for_presentation function
@pytest.mark.asyncio
async def test_delete_all_items_for_presentation():
    pres_data = create_dummy_data('presentation')
    slide_data1 = create_dummy_data('slide')
    slide_data2 = create_dummy_data('slide')
    slide_data1['user_id'] = slide_data2['user_id'] = pres_data['user_id']
    slide_data1['presentation_id'] = slide_data2['presentation_id'] = pres_data['presentation_id']
    
    await update_items('presentation', [pres_data])
    await update_items('slide', [slide_data1, slide_data2])
    
    await delete_all_items_for_presentation(pres_data['user_id'], pres_data['presentation_id'], 'slide')
    result = await get_all_items_for_presentation(pres_data['user_id'], pres_data['presentation_id'], 'slide')
    assert len(result) == 0



# # Run the tests
# if __name__ == "__main__":
#     asyncio.run(pytest.main([__file__]))