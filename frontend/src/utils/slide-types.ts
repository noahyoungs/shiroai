export type Slide = ShortBulletsSlide | MarkdownSlide | SimpleMermaidSlide | SectionHeaderSlide | PresentationTitleSlide;

export interface BaseSlide {
  slide_title: string;
  topic_id: string;
  id: string;
  hidden?: boolean;
  previous?: string;
  next?: string;
  [key: string]: any;
}

export interface Excerpt {
  source_id: string;
  excerpt_id: string;
  text: string;
}

export interface Image {
  s3_key?: string;
  url?: string;
  prompt: string;
  negative_prompt?: string;
  style?: string;
  model: string;
  width: number;
  height: number;
  shape: string;
  type: string;
}

export interface IconData {
  name: string;
  source: string;
  detailed_name?: string;
}

export interface ShortBulletsSlide extends BaseSlide {
  slide_type: 'short_bullets_slide';
  slide_content: ShortBulletContent[];
  sequential: boolean;
  layout: 'list' | 'grid';
}

export interface ShortBulletContent {
  content: string;
  source_excerpt_id: string;
  excerpt: Excerpt | null;
  icon: IconData;
  id: string;
}

export interface SimpleMermaidSlide extends BaseSlide {
  slide_type: 'simple_mermaid_slide';
  slide_content: {
    mermaid_code: string;
    excerpts: Excerpt[];
    light_svg: string;
    dark_svg: string;
  };
}

export interface MarkdownSlide extends BaseSlide {
  slide_type: 'markdown_slide';
  slide_content: {
    content: string;
    footnotes: Record<string, Excerpt>;
    prose_class?: string;
  };
}

export interface SectionHeaderSlide extends BaseSlide {
  slide_type: 'section_header_slide';
  slide_title: string;
  image: Image;
  image_position: 'left' | 'right';
}

export interface PresentationTitleSlide extends BaseSlide {
  slide_type: 'presentation_title_slide';
  slide_title: string;
  image: Image;
}
