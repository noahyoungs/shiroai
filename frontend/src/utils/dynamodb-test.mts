import { updateSlides, getAllSlides, getSlides } from '/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/utils/dynamodb.ts'; // Adjust the import path as necessary
import type { Slide } from './slide-types'; // Use 'type' to import the Slide type
import { v4 as uuidv4 } from 'uuid';
import { config as dotenvConfig } from 'dotenv';
dotenvConfig({ path: '.env.local' });

async function testUpdateAndGetSlides() {
  const presentationID = uuidv4();

  const slides: Partial<Slide>[] = [
    {
      id: uuidv4(),
      slide_type: 'short_bullets_slide',
      slide_title: "Slide 1",
      topic_id: "Topic 1",
      hidden: false,
      slide_content: [
        {
          content: "Bullet point 1",
          source_excerpt_id: uuidv4(),
          excerpt: {
            source_id: "Source 1",
            excerpt_id: uuidv4(),
            text: "Excerpt text 1",
          },
          icon: {
            name: "icon-name",
            source: "icon-source",
            detailed_name: "icon-detailed-name",
          },
          id: uuidv4(),
        },
      ],
      sequential: true,
      layout: 'list',
    },
    {
      id: uuidv4(),
      slide_type: 'markdown_slide',
      slide_title: "Slide 2",
      topic_id: "Topic 2",
      hidden: false,
      slide_content: {
        content: "Markdown content",
        footnotes: {
          footnote1: {
            source_id: "Source 2",
            excerpt_id: uuidv4(),
            text: "Footnote text",
          },
        },
      },
    },
    {
      id: uuidv4(),
      slide_type: 'simple_mermaid_slide',
      slide_title: "Slide 3",
      topic_id: "Topic 3",
      hidden: false,
      slide_content: {
        mermaid_code: "graph TD; A-->B;",
        excerpts: [
          {
            source_id: "Source 3",
            excerpt_id: uuidv4(),
            text: "Mermaid excerpt",
          },
        ],
        light_svg: "<svg>Light</svg>",
        dark_svg: "<svg>Dark</svg>",
      },
    },
    {
      id: uuidv4(),
      slide_type: 'section_header_slide',
      slide_title: "Slide 4",
      topic_id: "Topic 4",
      hidden: false,
      image: {
        s3_key: "image-key",
        url: "https://example.com/image.jpg",
        alt: "An example image",
        type: "cover",
        shape: "rectangle",
      },
      image_position: 'left',
    },
    {
      id: uuidv4(),
      slide_type: 'presentation_title_slide',
      slide_title: "Slide 5",
      topic_id: "Topic 5",
      hidden: false,
      image: {
        s3_key: "title-image-key",
        url: "https://example.com/title-image.jpg",
        alt: "Title slide image",
        type: "cover",
        shape: "rectangle",
      },
    },
  ];

  console.log("Updating slides...");
  const updateResult = await updateSlides(presentationID, slides);
  console.log("Update result:", updateResult);

  console.log("Retrieving all slides...");
  const allSlides = await getAllSlides(presentationID);
  console.log("All slides:", allSlides);

  if (allSlides.length > 0) {
    console.log("Retrieving single slide...");
    const singleSlide = await getSlides(presentationID, allSlides[0].id);
    console.log("Single slide:", singleSlide);
  }

  console.log("Retrieving multiple slides...");
  const slideIDs = allSlides.map((slide) => slide.id);
  const multipleSlides = await getSlides(presentationID, slideIDs);
  console.log("Multiple slides:", multipleSlides);
}

testUpdateAndGetSlides().catch((error) => console.error("Test failed:", error));
