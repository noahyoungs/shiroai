//@ts-nocheck
import { v4 as uuidv4 } from 'uuid';
import { batchUpdateSlides, updateSlide, deleteSlide, getSlide, getSlides } from './dynamodb';
import { Slide } from '@/utils/slide-types';

export async function testSlideFunctions() {
  const presentationID = uuidv4();
  const slide1ID = uuidv4();
  const slide2ID = uuidv4();
  const slide3ID = uuidv4();

  // Test batchUpdateSlides
  const newSlides: Slide[] = [
    {
      id: slide1ID,
      slide_type: 'short_bullets_slide',
      slide_title: 'Slide 1',
      topic_id: 'topic1',
      slide_content: [{ content: 'Bullet 1', source_excerpt_id: 'excerpt1' }],
      sequential: true,
    },
    {
      id: slide2ID,
      slide_type: 'markdown_table_slide',
      slide_title: 'Slide 2',
      topic_id: 'topic2',
      slide_content: {
        table: '| Column 1 | Column 2 |\n|----------|----------|\n| Row 1    | Value 1  |\n| Row 2    | Value 2  |',
        footnotes: { '1': 'Footnote 1', '2': 'Footnote 2' },
      },
    },
  ];

  await batchUpdateSlides(presentationID, newSlides);
  console.log('Slides created successfully');

  // Test getSlides
  const slides = await getSlides(presentationID);
  console.log('Retrieved slides:', slides);

  // Test updateSlide
  const updatedSlideData: Partial<Slide> = {
    slide_title: 'Updated Slide 1',
    slide_content: [{ content: 'Updated Bullet 1', source_excerpt_id: 'excerpt1' }],
  };

  await updateSlide(presentationID, slide1ID, updatedSlideData);
  console.log('Slide updated successfully');

  // Test getSlide
  const slide = await getSlide(presentationID, slide1ID);
  console.log('Retrieved slide:', slide);

  // Test deleteSlide
  await deleteSlide(presentationID, slide2ID);
  console.log('Slide deleted successfully');

  // Test getSlides after deletion
  const updatedSlides = await getSlides(presentationID);
  console.log('Retrieved slides after deletion:', updatedSlides);

  // Test creating a new slide
  const newSlide: Slide = {
    id: slide3ID,
    slide_type: 'simple_mermaid_slide',
    slide_title: 'Slide 3',
    topic_id: 'topic3',
    slide_content: {
      mermaid_code: 'graph TD;\n  A-->B;\n  A-->C;\n  B-->D;\n  C-->D;',
      excerpt_ids: ['excerpt2', 'excerpt3'],
    },
  };

  await batchUpdateSlides(presentationID, [newSlide]);
  console.log('New slide created successfully');

  // Test getSlides after creating a new slide
  const finalSlides = await getSlides(presentationID);
  console.log('Retrieved slides after creating a new slide:', finalSlides);
}

testSlideFunctions().catch(console.error);