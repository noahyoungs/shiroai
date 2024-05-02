export type Slide = ShortBulletsSlide | MarkdownTableSlide | SimpleMermaidSlide | LongBulletsSlide | SectionHeaderSlide | PresentationTitleSlide;

export interface BaseSlide {
  slide_title: string;
  topic_id: string;
  id: string;
  slide_order: number;
}

export interface Excerpt {
  source_id: string;
  excerpt_id: string;
  text: string;
}

export interface Image {
  s3_key?: string;
  url?: string;
  alt: string;
  type: string;
  shape: string;
}

export interface ShortBulletsSlide extends BaseSlide {
  slide_type: 'short_bullets_slide';
  slide_content: ShortBulletContent[];
  sequential: boolean;
}

export interface ShortBulletContent {
  content: string;
  source_excerpt_id: string;
  excerpt: Excerpt;
}

export interface MarkdownTableSlide extends BaseSlide {
  slide_type: 'markdown_table_slide';
  slide_content: {
    table: string;
    footnotes: Record<string, Excerpt>;
  };
}

export interface SimpleMermaidSlide extends BaseSlide {
  slide_type: 'simple_mermaid_slide';
  slide_content: {
    mermaid_code: string;
    excerpt_ids: string[];
  };
}

export interface LongBulletsSlide extends BaseSlide {
  slide_type: 'long_bullets_slide';
  slide_content: {
    content: string;
    footnotes: Record<string, Excerpt>;
  };
}

export interface SectionHeaderSlide extends BaseSlide {
  slide_type: 'section_header_slide';
  slide_title: string;
  image: Image;
}

export interface PresentationTitleSlide extends BaseSlide {
  slide_type: 'presentation_title_slide';
  slide_title: string;
  image: Image;
}